"""Cross-model judge check: GPT-4 scores the same (question, answer) pairs.

Samples 15 pairs from DCR and 15 from vanilla RAG (trial-1), stratified by
DDC class. Sends each to GPT-4o as an independent judge. Compares whether
the MISSING direction (DCR < RAG) holds under a different model.
"""

import asyncio
import json
import os
import random
from pathlib import Path

from openai import AsyncOpenAI

EXPERIMENT_DIR = Path(__file__).parent

JUDGE_PROMPT = """You are evaluating whether a question about a domain knowledge base has been adequately answered.

Given the question and answer below, classify the answer as one of:
- ANSWERABLE: The answer fully addresses the question with specific, cited details.
- PARTIAL: The answer partially addresses the question but key specifics are missing.
- NOT_ANSWERABLE: The answer fails to address the question or provides no useful information.

Question: {question}

Answer: {answer}

Respond with ONLY one word: ANSWERABLE, PARTIAL, or NOT_ANSWERABLE"""

SCORE_MAP = {
    "ANSWERABLE": "CLEAN",
    "PARTIAL": "INCOMPLETE",
    "NOT_ANSWERABLE": "MISSING",
}


def sample_pairs(condition: str, n: int = 15) -> list[dict]:
    path = EXPERIMENT_DIR / "trial-1" / f"{condition}.checkpoint.json"
    with open(path) as f:
        data = json.load(f)
    results = data["results"]

    by_class = {"CLEAN": [], "INCOMPLETE": [], "MISSING": []}
    for idx, r in results.items():
        by_class[r["ddc_class"]].append({
            "index": int(idx),
            "question": r["question"],
            "answer": r["answer"],
            "original_ddc": r["ddc_class"],
            "condition": condition,
        })

    random.seed(42)
    sampled = []
    counts = {"CLEAN": 5, "INCOMPLETE": 7, "MISSING": 3}
    for cls, target in counts.items():
        pool = by_class[cls]
        take = min(target, len(pool))
        sampled.extend(random.sample(pool, take))
        if take < target:
            # Fill from INCOMPLETE if not enough MISSING
            extra = target - take
            remaining = [p for p in by_class["INCOMPLETE"] if p not in sampled]
            sampled.extend(random.sample(remaining, min(extra, len(remaining))))

    return sampled[:n]


async def judge_with_gpt4(client: AsyncOpenAI, pair: dict) -> dict:
    prompt = JUDGE_PROMPT.format(question=pair["question"], answer=pair["answer"])
    try:
        resp = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0,
        )
        raw = resp.choices[0].message.content.strip().upper()

        # Extract score
        gpt4_ddc = None
        for keyword, ddc in [("NOT_ANSWERABLE", "MISSING"), ("NOT ANSWERABLE", "MISSING"),
                              ("PARTIAL", "INCOMPLETE"), ("ANSWERABLE", "CLEAN")]:
            if keyword in raw:
                gpt4_ddc = ddc
                break

        return {
            **pair,
            "gpt4_raw": raw,
            "gpt4_ddc": gpt4_ddc or "UNKNOWN",
        }
    except Exception as e:
        return {**pair, "gpt4_raw": str(e), "gpt4_ddc": "ERROR"}


async def main():
    dotenv_path = Path(__file__).parent.parent.parent / ".env"
    if dotenv_path.exists():
        for line in dotenv_path.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

    client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])

    dcr_pairs = sample_pairs("dcr", 15)
    rag_pairs = sample_pairs("vanilla_rag", 15)
    all_pairs = dcr_pairs + rag_pairs

    print(f"Judging {len(all_pairs)} pairs with GPT-4o...")
    print(f"  DCR: {len(dcr_pairs)} pairs ({sum(1 for p in dcr_pairs if p['original_ddc']=='CLEAN')} CLEAN, "
          f"{sum(1 for p in dcr_pairs if p['original_ddc']=='INCOMPLETE')} INC, "
          f"{sum(1 for p in dcr_pairs if p['original_ddc']=='MISSING')} MISS)")
    print(f"  RAG: {len(rag_pairs)} pairs ({sum(1 for p in rag_pairs if p['original_ddc']=='CLEAN')} CLEAN, "
          f"{sum(1 for p in rag_pairs if p['original_ddc']=='INCOMPLETE')} INC, "
          f"{sum(1 for p in rag_pairs if p['original_ddc']=='MISSING')} MISS)")

    tasks = [judge_with_gpt4(client, p) for p in all_pairs]
    results = await asyncio.gather(*tasks)

    # Analyze
    dcr_results = [r for r in results if r["condition"] == "dcr"]
    rag_results = [r for r in results if r["condition"] == "vanilla_rag"]

    print("\n=== GPT-4o Cross-Judge Results ===\n")

    for label, group in [("DCR", dcr_results), ("Vanilla RAG", rag_results)]:
        gpt4_counts = {}
        for r in group:
            gpt4_counts[r["gpt4_ddc"]] = gpt4_counts.get(r["gpt4_ddc"], 0) + 1
        print(f"{label} (n={len(group)}): {gpt4_counts}")

    # Agreement with original Claude scoring
    agree = sum(1 for r in results if r["gpt4_ddc"] == r["original_ddc"])
    print(f"\nAgreement with Claude original: {agree}/{len(results)} ({100*agree/len(results):.1f}%)")

    # Direction check: does GPT-4 also see fewer MISSING in DCR?
    dcr_missing = sum(1 for r in dcr_results if r["gpt4_ddc"] == "MISSING")
    rag_missing = sum(1 for r in rag_results if r["gpt4_ddc"] == "MISSING")
    print(f"\nMISSING direction check:")
    print(f"  DCR MISSING (GPT-4):  {dcr_missing}/{len(dcr_results)}")
    print(f"  RAG MISSING (GPT-4):  {rag_missing}/{len(rag_results)}")
    print(f"  Direction holds: {'YES' if rag_missing >= dcr_missing else 'NO'}")

    # Disagreement details
    print("\n=== Disagreements ===\n")
    for r in results:
        if r["gpt4_ddc"] != r["original_ddc"]:
            direction = "promoted" if ["MISSING","INCOMPLETE","CLEAN"].index(r["gpt4_ddc"]) > ["MISSING","INCOMPLETE","CLEAN"].index(r["original_ddc"]) else "demoted"
            print(f"  Q{r['index']} ({r['condition']}): Claude={r['original_ddc']} → GPT-4={r['gpt4_ddc']} ({direction})")

    # Save results
    output = {
        "model": "gpt-4o",
        "pairs_total": len(results),
        "dcr_pairs": len(dcr_results),
        "rag_pairs": len(rag_results),
        "agreement": agree,
        "agreement_pct": round(100 * agree / len(results), 1),
        "dcr_missing_gpt4": dcr_missing,
        "rag_missing_gpt4": rag_missing,
        "direction_holds": rag_missing >= dcr_missing,
        "results": results,
    }

    out_path = EXPERIMENT_DIR / "aggregate" / "cross_judge_gpt4_results.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
