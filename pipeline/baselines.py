"""Baseline retrieval pipelines for DCR paper comparison.

Three conditions:
  1. NaiveVectorPipeline — cosine similarity only, top-K, no fusion, no graph
  2. VanillaRAGPipeline — vector + keyword, simple merge, no typed traversal
  3. RetrievalPipeline (existing) — full DCR with all 7 stages

All share the same backend, embedder, and synthesizer so the only variable
is the retrieval strategy.
"""
import time

import numpy as np
import structlog

from .backend import StorageBackend
from .types import (
    AnswerScore,
    Gap,
    RetrievalHop,
    RetrievalResult,
    RetrievalTrace,
    ScoredEntity,
    StageTrace,
)

logger = structlog.get_logger(__name__)


class NaiveVectorPipeline:
    """Baseline 1: Pure vector search + synthesis.

    No intent classification, no keyword search, no graph traversal,
    no fusion, no confidence weighting, no dedup, no gap detection.
    Just cosine similarity → top K → synthesize.
    """

    def __init__(self, backend: StorageBackend, embed_fn=None, synthesize_fn=None, config=None):
        self.backend = backend
        self.embed_fn = embed_fn
        self.synthesize_fn = synthesize_fn
        self.max_results = (config or {}).get("max_results", 15)
        self.token_budget = (config or {}).get("token_budget", 8000)

    async def retrieve(self, question: str) -> RetrievalResult:
        start_time = time.time()

        # Just vector search
        if not self.embed_fn:
            return self._empty_result(question, start_time)

        query_embedding = await self.embed_fn(question)
        vector_results = await self.backend.vector_search(query_embedding, top_k=self.max_results)

        # Build context directly from top results — no scoring adjustments
        context_parts = []
        hops = []
        tokens_used = 0

        for entity in vector_results[:self.max_results]:
            block = f"Entity: {entity.name} ({entity.entity_type})\nDescription: {entity.description}\n"
            block_tokens = len(block) // 4
            if tokens_used + block_tokens > self.token_budget:
                break
            context_parts.append(block)
            tokens_used += block_tokens

            hops.append(RetrievalHop(
                entity_id=entity.entity_id,
                entity_name=entity.name,
                entity_type=entity.entity_type,
                layer=entity.layer,
                confidence=entity.confidence,
                hop_number=0,
                matched_by="vector",
                fused_score=entity.score,
                found_by=["vector"],
            ))

        context_text = "\n---\n".join(context_parts)

        # Synthesize
        t6 = time.time()
        if self.synthesize_fn:
            answer, score, citations = await self.synthesize_fn(question, context_text, {})
        else:
            answer = "(No synthesis)"
            score = AnswerScore.PARTIAL
            citations = []
        synthesis_ms = int((time.time() - t6) * 1000)

        total_ms = int((time.time() - start_time) * 1000)

        trace = RetrievalTrace(
            question=question,
            sub_queries=[question],
            intent_weights={},
            hops=hops,
            stage_trace=StageTrace(
                vector_candidates=len(vector_results),
                keyword_candidates=0,
                graph_candidates=0,
                fused_unique=len(vector_results),
                after_dedup=len(hops),
                context_selected=len(hops),
            ),
            total_entities_searched=self.backend.entity_count(),
            total_entities_retrieved=len(hops),
            synthesis_ms=synthesis_ms,
            total_ms=total_ms,
        )

        return RetrievalResult(
            answer=answer,
            citations=citations,
            score=score,
            trace=trace,
            gaps=[],
            context_text=context_text,
        )

    def _empty_result(self, question, start_time):
        return RetrievalResult(
            answer="No embedder available.",
            citations=[], score=AnswerScore.NOT_ANSWERABLE,
            trace=RetrievalTrace(question=question, sub_queries=[], intent_weights={},
                                 total_ms=int((time.time() - start_time) * 1000)),
            gaps=[], context_text="",
        )


class VanillaRAGPipeline:
    """Baseline 2: Vector + keyword search with simple merge.

    Has: vector search, keyword search, basic score merge.
    Missing: intent classification, typed graph traversal, layer priority boost,
    confidence weighting, 5-layer dedup, gap detection.
    """

    def __init__(self, backend: StorageBackend, embed_fn=None, synthesize_fn=None, config=None):
        self.backend = backend
        self.embed_fn = embed_fn
        self.synthesize_fn = synthesize_fn
        self.max_results = (config or {}).get("max_results", 15)
        self.token_budget = (config or {}).get("token_budget", 8000)

    async def retrieve(self, question: str) -> RetrievalResult:
        start_time = time.time()

        # Vector search
        query_embedding = None
        vector_results = []
        if self.embed_fn:
            query_embedding = await self.embed_fn(question)
            entity_count = self.backend.entity_count()
            top_k = max(20, min(200, entity_count // 5))
            vector_results = await self.backend.vector_search(query_embedding, top_k=top_k)

        # Keyword search
        entity_count = self.backend.entity_count()
        top_k = max(20, min(200, entity_count // 5))
        keyword_results = await self.backend.keyword_search(question, top_k=top_k)

        # Simple merge — combine scores, no RRF, no layer boost
        entity_scores: dict[str, float] = {}
        entity_map: dict[str, ScoredEntity] = {}

        for entity in vector_results:
            entity_scores[entity.entity_id] = entity.score
            entity_map[entity.entity_id] = entity

        for entity in keyword_results:
            if entity.entity_id in entity_scores:
                # Simple average of both scores
                entity_scores[entity.entity_id] = (entity_scores[entity.entity_id] + entity.score) / 2
            else:
                entity_scores[entity.entity_id] = entity.score
                entity_map[entity.entity_id] = entity

        # Sort by score, take top K
        sorted_ids = sorted(entity_scores, key=lambda x: -entity_scores[x])[:self.max_results]

        # Build context
        context_parts = []
        hops = []
        tokens_used = 0

        for eid in sorted_ids:
            entity = entity_map[eid]
            block = f"Entity: {entity.name} ({entity.entity_type})\nDescription: {entity.description}\n"

            rels = [f"  {r['type']} → {r['target_id']}" for r in entity.relationships[:5]]
            if rels:
                block += "Relationships:\n" + "\n".join(rels) + "\n"

            block_tokens = len(block) // 4
            if tokens_used + block_tokens > self.token_budget:
                break
            context_parts.append(block)
            tokens_used += block_tokens

            found_by = []
            if any(e.entity_id == eid for e in vector_results):
                found_by.append("vector")
            if any(e.entity_id == eid for e in keyword_results):
                found_by.append("keyword")

            hops.append(RetrievalHop(
                entity_id=entity.entity_id,
                entity_name=entity.name,
                entity_type=entity.entity_type,
                layer=entity.layer,
                confidence=entity.confidence,
                hop_number=0,
                matched_by=found_by[0] if found_by else "unknown",
                fused_score=entity_scores[eid],
                found_by=found_by,
            ))

        context_text = "\n---\n".join(context_parts)

        # Synthesize
        t6 = time.time()
        if self.synthesize_fn:
            answer, score, citations = await self.synthesize_fn(question, context_text, {})
        else:
            answer = "(No synthesis)"
            score = AnswerScore.PARTIAL
            citations = []
        synthesis_ms = int((time.time() - t6) * 1000)

        total_ms = int((time.time() - start_time) * 1000)

        trace = RetrievalTrace(
            question=question,
            sub_queries=[question],
            intent_weights={},
            hops=hops,
            stage_trace=StageTrace(
                vector_candidates=len(vector_results),
                keyword_candidates=len(keyword_results),
                graph_candidates=0,
                fused_unique=len(entity_scores),
                after_dedup=len(hops),
                context_selected=len(hops),
            ),
            total_entities_searched=self.backend.entity_count(),
            total_entities_retrieved=len(hops),
            synthesis_ms=synthesis_ms,
            total_ms=total_ms,
        )

        return RetrievalResult(
            answer=answer,
            citations=citations,
            score=score,
            trace=trace,
            gaps=[],
            context_text=context_text,
        )
