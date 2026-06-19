"""Domain-Aware Retrieval Pipeline — 7-stage retrieval with typed traversal.

Usage:
    pipeline = RetrievalPipeline(backend, embedder)
    result = await pipeline.retrieve("How does a claim flow from submission to payment?")
"""
import asyncio
import math
import re
import time
from collections import defaultdict

import numpy as np
import structlog

from .backend import StorageBackend
from .query_understanding import classify_query
from .types import (
    AnswerScore,
    Gap,
    QueryUnderstanding,
    RetrievalHop,
    RetrievalResult,
    RetrievalTrace,
    ScoredEntity,
    StageTrace,
)

logger = structlog.get_logger(__name__)


class RetrievalPipeline:
    """7-stage retrieval pipeline with typed traversal and gap detection."""

    def __init__(
        self,
        backend: StorageBackend,
        embed_fn=None,  # async fn(text) -> np.ndarray
        synthesize_fn=None,  # async fn(question, context, intent) -> (answer, score, citations)
        config: dict | None = None,
    ):
        self.backend = backend
        self.embed_fn = embed_fn
        self.synthesize_fn = synthesize_fn
        self.config = config or {}

        # Configurable parameters
        self.vector_top_k = self.config.get("vector_search_top_k", 200)
        self.keyword_top_k = self.config.get("keyword_search_top_k", 200)
        self.graph_max_hops = self.config.get("graph_max_hops", 3)
        self.graph_max_seeds = self.config.get("graph_max_seeds", 15)
        self.rrf_k = self.config.get("rrf_k", 60)
        self.cosine_blend = self.config.get("cosine_blend_weight", 0.3)
        self.confidence_weight = self.config.get("confidence_weight", 1.0)
        self.bottom_cutoff = self.config.get("bottom_cutoff", 0.15)
        self.text_sim_threshold = self.config.get("text_similarity_threshold", 0.85)
        self.type_diversity_max = self.config.get("type_diversity_max_ratio", 0.5)
        self.token_budget = self.config.get("token_budget", 8000)
        self.max_results = self.config.get("max_results", 15)

    async def retrieve(self, question: str) -> RetrievalResult:
        """Run the full 7-stage retrieval pipeline."""
        start_time = time.time()

        # Auto-scale top_k relative to KB size (cap at 20% of entities)
        entity_count = self.backend.entity_count()
        if entity_count > 0:
            scaled_top_k = max(20, min(self.vector_top_k, entity_count // 5))
            self.vector_top_k = scaled_top_k
            self.keyword_top_k = scaled_top_k

        # Stage 0: Query Understanding
        understanding = classify_query(question)
        logger.info(
            "stage0_query_understanding",
            question=question[:100],
            intents=understanding.intent_weights,
            layer_priorities=understanding.layer_priorities,
        )

        # Stage 1: Parallel Search
        t1 = time.time()
        vector_results, keyword_results, graph_results, query_embedding = (
            await self._stage1_parallel_search(understanding)
        )
        search_ms = int((time.time() - t1) * 1000)

        logger.info(
            "stage1_parallel_search",
            vector=len(vector_results),
            keyword=len(keyword_results),
            graph=len(graph_results),
            search_ms=search_ms,
        )

        # Stage 2: Fusion
        fused = self._stage2_fusion(
            vector_results, keyword_results, graph_results,
            understanding, query_embedding,
        )

        # Stage 3: Scoring Adjustments
        self._stage3_scoring(fused)

        # Stage 4: Dedup
        deduped = self._stage4_dedup(fused, understanding)

        # Stage 5: Context Building + Trace
        context_text, hops = self._stage5_context(deduped, understanding)

        # Stage 6: Synthesis
        t6 = time.time()
        if self.synthesize_fn:
            answer, score, citations = await self.synthesize_fn(
                question, context_text, understanding.intent_weights,
            )
        else:
            answer = "(No synthesis function configured — retrieval only)"
            score = AnswerScore.PARTIAL
            citations = []
        synthesis_ms = int((time.time() - t6) * 1000)

        # Stage 7: Gap Detection
        gaps = self._stage7_gaps(hops, score, question)

        total_ms = int((time.time() - start_time) * 1000)

        # Build detailed stage trace
        stage_trace = StageTrace(
            intent_weights=understanding.intent_weights,
            layer_priorities=understanding.layer_priorities,
            vector_candidates=len(vector_results),
            keyword_candidates=len(keyword_results),
            graph_candidates=len(graph_results),
            fused_unique=len(fused),
            after_scoring=len(fused),  # scoring doesn't remove, just re-ranks
            after_dedup=len(deduped),
            context_selected=len(hops),
            tokens_used=sum(len(h.entity_name) + 50 for h in hops),  # approximate
            token_budget=self.token_budget,
            synthesis_score=score.value,
            gaps_detected=len(gaps),
        )

        trace = RetrievalTrace(
            question=question,
            sub_queries=[question],
            intent_weights=understanding.intent_weights,
            hops=hops,
            stage_trace=stage_trace,
            total_entities_searched=self.backend.entity_count(),
            total_entities_retrieved=len(deduped),
            vector_search_ms=search_ms,
            keyword_search_ms=0,
            graph_search_ms=0,
            synthesis_ms=synthesis_ms,
            total_ms=total_ms,
            gaps=gaps,
        )

        logger.info(
            "retrieval_complete",
            question=question[:80],
            answer_score=score.value,
            entities_retrieved=len(deduped),
            gaps=len(gaps),
            total_ms=total_ms,
        )

        return RetrievalResult(
            answer=answer,
            citations=citations,
            score=score,
            trace=trace,
            gaps=gaps,
            context_text=context_text,
        )

    # ── Stage 1: Parallel Search ──

    async def _stage1_parallel_search(
        self, understanding: QueryUnderstanding,
    ) -> tuple[list[ScoredEntity], list[ScoredEntity], list[ScoredEntity], np.ndarray | None]:
        """Run vector, keyword, and graph search in parallel."""
        query_embedding = None
        vector_results = []
        keyword_results = []
        graph_results = []

        # Prepare tasks
        tasks = []

        # Vector search (if embedder available)
        if self.embed_fn:
            async def _vector():
                nonlocal query_embedding, vector_results
                query_embedding = await self.embed_fn(understanding.original_question)
                vector_results = await self.backend.vector_search(query_embedding, self.vector_top_k)
            tasks.append(_vector())

        # Keyword search
        async def _keyword():
            nonlocal keyword_results
            keyword_results = await self.backend.keyword_search(
                understanding.original_question, self.keyword_top_k,
            )
        tasks.append(_keyword())

        # Run vector + keyword in parallel
        await asyncio.gather(*tasks)

        # Graph search — needs vector results as seeds
        seed_ids = [e.entity_id for e in (vector_results or keyword_results)[:self.graph_max_seeds]]
        if seed_ids:
            graph_results = await self.backend.graph_neighbors(
                seed_ids,
                max_hops=self.graph_max_hops,
                edge_types=understanding.edge_priorities,
                max_seeds=self.graph_max_seeds,
            )

        return vector_results, keyword_results, graph_results, query_embedding

    # ── Stage 2: Fusion (RRF + layer boost + cosine re-score) ──

    def _stage2_fusion(
        self,
        vector_results: list[ScoredEntity],
        keyword_results: list[ScoredEntity],
        graph_results: list[ScoredEntity],
        understanding: QueryUnderstanding,
        query_embedding: np.ndarray | None,
    ) -> list[ScoredEntity]:
        """Merge results from all search methods using RRF."""
        # Build result lists (as lists of entity IDs)
        result_lists: list[list[str]] = []
        entity_map: dict[str, ScoredEntity] = {}
        # Track which methods found each entity
        found_by_map: dict[str, list[str]] = defaultdict(list)
        # Track graph provenance separately (preserved even when keyword wins)
        graph_provenance: dict[str, dict] = {}

        for method, results in [("vector", vector_results), ("keyword", keyword_results), ("graph", graph_results)]:
            id_list = []
            for entity in results:
                id_list.append(entity.entity_id)
                found_by_map[entity.entity_id].append(method)

                # Preserve graph hop info separately — never overwritten
                if method == "graph" and entity.hop_number > 0:
                    if entity.entity_id not in graph_provenance:
                        graph_provenance[entity.entity_id] = {
                            "hop": entity.hop_number,
                            "from": entity.relationship_from,
                            "rel": entity.relationship_type,
                            "decay": entity.hop_decay,
                        }

                # Keep the version with highest score for ranking
                if entity.entity_id not in entity_map or entity.score > entity_map[entity.entity_id].score:
                    entity_map[entity.entity_id] = entity
            if id_list:
                result_lists.append(id_list)

        # Attach multi-method provenance and graph hop info to winning entities
        for eid, entity in entity_map.items():
            entity.found_by = found_by_map.get(eid, [])
            if eid in graph_provenance:
                gp = graph_provenance[eid]
                entity.graph_hop = gp["hop"]
                entity.graph_from = gp["from"]
                entity.graph_rel = gp["rel"]
                # If the entity was found by keyword at hop 0 but graph knows
                # it's reachable at hop N via a relationship, update the hop info
                if entity.hop_number == 0 and gp["hop"] > 0:
                    entity.hop_number = gp["hop"]
                    entity.relationship_from = gp["from"]
                    entity.relationship_type = gp["rel"]
                    entity.hop_decay = gp["decay"]

        if not result_lists:
            return []

        # RRF: score(entity) = Σ(1 / (k + rank)) across all lists
        rrf_scores: dict[str, float] = defaultdict(float)
        for result_list in result_lists:
            for rank, eid in enumerate(result_list):
                rrf_scores[eid] += 1 / (self.rrf_k + rank)

        # Normalize to 0-1
        max_rrf = max(rrf_scores.values()) if rrf_scores else 1
        for eid in rrf_scores:
            rrf_scores[eid] /= max_rrf

        # Layer priority boost
        for eid, rrf_score in rrf_scores.items():
            entity = entity_map.get(eid)
            if entity:
                layer_boost = understanding.layer_priorities.get(entity.layer, 1.0)
                rrf_scores[eid] = rrf_score * layer_boost

        # Cosine re-score (blend with RRF)
        if query_embedding is not None and self.cosine_blend > 0:
            for eid in rrf_scores:
                entity = entity_map.get(eid)
                if entity and eid in {e.entity_id for e in vector_results}:
                    # Entity was in vector results — get its cosine score
                    cosine_score = next(
                        (e.score for e in vector_results if e.entity_id == eid), 0
                    )
                    rrf_scores[eid] = (
                        (1 - self.cosine_blend) * rrf_scores[eid]
                        + self.cosine_blend * cosine_score
                    )

        # Build final scored list
        fused = []
        for eid in sorted(rrf_scores, key=lambda x: -rrf_scores[x]):
            entity = entity_map.get(eid)
            if entity:
                entity.score = rrf_scores[eid]
                fused.append(entity)

        return fused

    # ── Stage 3: Scoring Adjustments ──

    def _stage3_scoring(self, results: list[ScoredEntity]):
        """Apply confidence, density, and source boosts."""
        if not results:
            return

        min_score = min(e.score for e in results)
        max_score = max(e.score for e in results)
        score_range = max_score - min_score if max_score > min_score else 1
        low_cutoff = min_score + self.bottom_cutoff * score_range

        for entity in results:
            if entity.score < low_cutoff:
                continue  # Skip bottom tier

            # Confidence boost (linear with floor)
            if self.confidence_weight > 0:
                conf_factor = 0.5 + 0.5 * entity.confidence
                entity.score *= conf_factor ** self.confidence_weight

            # Relationship density boost
            edge_count = len(entity.relationships)
            if edge_count > 0:
                entity.score *= (1 + 0.03 * math.log(1 + edge_count))

            # Source document count boost
            source_count = len(entity.source_documents)
            if source_count > 0:
                entity.score *= (1 + 0.02 * math.log(1 + source_count))

        # Re-sort after adjustments
        results.sort(key=lambda x: -x.score)

    # ── Stage 4: Dedup ──

    def _stage4_dedup(
        self, results: list[ScoredEntity], understanding: QueryUnderstanding,
    ) -> list[ScoredEntity]:
        """5-layer dedup pipeline, intent-aware."""
        # Layer 1: Exact entity ID dedup (keep highest scored)
        seen_ids: dict[str, ScoredEntity] = {}
        for entity in results:
            if entity.entity_id not in seen_ids or entity.score > seen_ids[entity.entity_id].score:
                seen_ids[entity.entity_id] = entity
        deduped = list(seen_ids.values())
        deduped.sort(key=lambda x: -x.score)

        # Layer 2: Text similarity (Jaccard > threshold → remove lower)
        filtered = []
        for entity in deduped:
            entity_words = set(re.findall(r"\w+", entity.description.lower()))
            is_duplicate = False
            for kept in filtered:
                kept_words = set(re.findall(r"\w+", kept.description.lower()))
                if entity_words and kept_words:
                    intersection = entity_words & kept_words
                    union = entity_words | kept_words
                    jaccard = len(intersection) / len(union)
                    if jaccard > self.text_sim_threshold:
                        is_duplicate = True
                        break
            if not is_duplicate:
                filtered.append(entity)
        deduped = filtered

        # Layer 3: Inverse relationship dedup
        # A.exposes→B and B.exposed_by→A are the same hop — merge
        inverse_pairs = set()
        final = []
        for entity in deduped:
            pair_key = None
            if entity.relationship_from:
                pair = tuple(sorted([entity.entity_id, entity.relationship_from]))
                if pair in inverse_pairs:
                    continue  # Already have this pair
                inverse_pairs.add(pair)
            final.append(entity)
        deduped = final

        # Layer 4: Type diversity (skip for listing/comparison queries)
        if not understanding.is_listing_query and not understanding.is_comparison_query:
            type_counts: dict[str, int] = defaultdict(int)
            max_per_type = max(1, int(len(deduped) * self.type_diversity_max))
            diverse = []
            for entity in deduped:
                if type_counts[entity.entity_type] < max_per_type:
                    diverse.append(entity)
                    type_counts[entity.entity_type] += 1
            deduped = diverse

        # Layer 5: Layer diversity (ensure relevant layers represented)
        if not understanding.is_listing_query:
            layer_counts: dict[str, int] = defaultdict(int)
            max_per_layer = max(1, int(len(deduped) * 0.6))
            diverse = []
            for entity in deduped:
                if layer_counts[entity.layer] < max_per_layer:
                    diverse.append(entity)
                    layer_counts[entity.layer] += 1
            deduped = diverse

        return deduped[:self.max_results]

    # ── Stage 5: Context Building + Trace ──

    def _stage5_context(
        self, results: list[ScoredEntity], understanding: QueryUnderstanding,
    ) -> tuple[str, list[RetrievalHop]]:
        """Build context text for LLM and generate retrieval trace.

        Includes entity body content with score-weighted token allocation:
        each entity gets a share of the budget proportional to its retrieval score.
        """
        hops: list[RetrievalHop] = []
        context_parts: list[str] = []
        tokens_used = 0

        # Interleave by layer priority (round-robin)
        by_layer: dict[str, list[ScoredEntity]] = defaultdict(list)
        for entity in results:
            by_layer[entity.layer].append(entity)

        ordered_layers = sorted(
            by_layer.keys(),
            key=lambda l: -understanding.layer_priorities.get(l, 1.0),
        )

        interleaved: list[ScoredEntity] = []
        while any(by_layer.values()):
            for layer in ordered_layers:
                if by_layer[layer]:
                    interleaved.append(by_layer[layer].pop(0))

        # Score-weighted token allocation per entity
        total_score = sum(e.score for e in interleaved) or 1.0
        TOKEN_FLOOR = 250
        TOKEN_CEILING = 2500

        for entity in interleaved:
            # Calculate this entity's body token budget
            raw_share = int(self.token_budget * (entity.score / total_score))
            body_token_budget = max(TOKEN_FLOOR, min(TOKEN_CEILING, raw_share))

            # Build header
            block = f"Entity: {entity.name} ({entity.entity_type}, confidence: {entity.confidence:.0%})\n"
            block += f"Description: {entity.description}\n"

            # Relationships
            rels = [f"  {r['type']} → {r['target_id']}" for r in entity.relationships[:5]]
            if rels:
                block += "Relationships:\n" + "\n".join(rels) + "\n"

            if entity.source_documents:
                block += f"Source: {entity.source_documents[0]}\n"

            # Include entity body content (strip Open Questions, then first-N truncation)
            body_text = entity.body.strip() if entity.body else ""
            if body_text:
                body_text = re.split(r'\n##\s*Open Questions', body_text)[0].strip()
            if body_text:
                body_char_budget = body_token_budget * 4
                if len(body_text) > body_char_budget:
                    body_text = body_text[:body_char_budget].rsplit("\n", 1)[0] + "\n[...]"
                block += f"\n{body_text}\n"

            block_tokens = len(block) // 4
            if tokens_used + block_tokens > self.token_budget:
                break

            context_parts.append(block)
            tokens_used += block_tokens

            # Build hop trace
            gap_flag = entity.confidence < 0.4 or len(entity.relationships) == 0
            gap_reason = None
            if entity.confidence < 0.4:
                gap_reason = "low_confidence"
            elif len(entity.relationships) == 0:
                gap_reason = "orphan_entity"

            hops.append(RetrievalHop(
                entity_id=entity.entity_id,
                entity_name=entity.name,
                entity_type=entity.entity_type,
                layer=entity.layer,
                confidence=entity.confidence,
                hop_number=entity.hop_number,
                matched_by=entity.matched_by,
                relationship_from=entity.relationship_from,
                relationship_type=entity.relationship_type,
                fused_score=entity.score,
                gap_flag=gap_flag,
                gap_reason=gap_reason,
                found_by=entity.found_by,
            ))

        context_text = "\n---\n".join(context_parts)
        return context_text, hops

    # ── Stage 7: Gap Detection ──

    def _stage7_gaps(
        self, hops: list[RetrievalHop], score: AnswerScore, question: str,
    ) -> list[Gap]:
        """Detect knowledge gaps from retrieval results."""
        gaps: list[Gap] = []

        for hop in hops:
            # Low confidence hub
            if hop.confidence < 0.4 and hop.hop_number <= 1:
                gaps.append(Gap(
                    gap_type="low_confidence_hub",
                    entity_id=hop.entity_id,
                    description=f"{hop.entity_name} has {hop.confidence:.0%} confidence",
                    suggested_action=f"Enrich {hop.entity_name} with more source documents",
                    severity="high",
                    source_question=question,
                ))

            # Orphan entity
            if hop.gap_reason == "orphan_entity":
                gaps.append(Gap(
                    gap_type="orphan_entity",
                    entity_id=hop.entity_id,
                    description=f"{hop.entity_name} has no typed relationships",
                    suggested_action=f"Add relationships for {hop.entity_name}",
                    severity="low",
                    source_question=question,
                ))

        # Ambiguous entities (similar names at similar scores)
        high_scored = [h for h in hops if h.fused_score > 0.7]
        for i, a in enumerate(high_scored):
            for b in high_scored[i + 1:]:
                a_words = set(a.entity_name.lower().split())
                b_words = set(b.entity_name.lower().split())
                if a_words and b_words:
                    jaccard = len(a_words & b_words) / len(a_words | b_words)
                    if jaccard > 0.6:
                        gaps.append(Gap(
                            gap_type="ambiguous_entity",
                            entity_id=a.entity_id,
                            description=f"'{a.entity_name}' and '{b.entity_name}' may be the same entity",
                            suggested_action="Disambiguate or merge these entities",
                            severity="medium",
                            source_question=question,
                        ))

        # NOT_ANSWERABLE gaps
        if score == AnswerScore.NOT_ANSWERABLE:
            entities_found = len([h for h in hops if h.fused_score > 0])
            if entities_found > 0:
                gaps.append(Gap(
                    gap_type="thin_coverage",
                    entity_id=hops[0].entity_id if hops else None,
                    description=f"Found {entities_found} related entities but content is insufficient",
                    suggested_action="Enrich existing entities with more detail from source documents",
                    severity="high",
                    source_question=question,
                ))
            else:
                gaps.append(Gap(
                    gap_type="missing_entity",
                    entity_id=None,
                    description="No entities in the KB could answer this question",
                    suggested_action="Extract new entities from source documents",
                    severity="high",
                    source_question=question,
                ))

        return gaps
