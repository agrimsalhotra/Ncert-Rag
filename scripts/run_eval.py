import asyncio
import json
import sys

from config.settings import EVAL_CLASS_NUM, RESULTS_PATH
from src.evaluation.checks import answer_check, refusal_ok, retrieval_hit
from src.evaluation.golden_set import load_golden_set
from src.evaluation.ragas_eval import add_ragas_scores
from src.generation.chain import NcertRag


def average(rows, key):
    values = [row[key] for row in rows if row.get(key) is not None]
    if len(values) == 0:
        return None, 0
    return sum(values) / len(values), len(values)


def count_true(rows, key):
    values = [row[key] for row in rows if row.get(key) is not None]
    return sum(1 for value in values if value), len(values)


def show(value):
    return f"{value:.2f}" if value is not None else "-"


def main():
    items = load_golden_set()
    rag = NcertRag()

    # --- Run the RAG pipeline on every golden question ---
    rows = []
    for item in items:
        result = rag.ask(item.question, class_num=EVAL_CLASS_NUM)
        row = {
            "id": item.id,
            "question": item.question,
            "answer": result.answer,
            "refused": result.refused,
            "reason": result.reason,
            "refusal_ok": refusal_ok(item, result),
            "retrieval_hit": retrieval_hit(item, result.retrieved_parents),
            "answer_check": answer_check(item, result.answer),
            "contexts": [parent.text for parent in result.retrieved_parents],
            "faithfulness": None,
            "context_recall": None,
            "context_precision": None,
        }
        rows.append(row)
        print(
            f"{item.id}: refusal_ok={row['refusal_ok']}  retrieval_hit={row['retrieval_hit']}  "
            f"answer_check={row['answer_check']}  ({result.reason})"
        )

    # --- Ragas (uses the Gemini judge). Skip with: --skip-ragas ---
    if "--skip-ragas" not in sys.argv:
        print("\nScoring with Ragas ...")
        asyncio.run(add_ragas_scores(rows, items))

    # --- Summary ---
    ok, total = count_true(rows, "refusal_ok")
    hits, hit_total = count_true(rows, "retrieval_hit")
    checks, check_total = count_true(rows, "answer_check")
    print("\n=== SUMMARY ===")
    print(f"Guardrail behaviour correct : {ok}/{total}")
    print(f"Retrieval hit-rate          : {hits}/{hit_total}")
    print(f"Required-word checks passed : {checks}/{check_total}")
    for key in ["faithfulness", "context_recall", "context_precision"]:
        mean, count = average(rows, key)
        print(f"{key:28}: {show(mean)}   (over {count} questions)")

    RESULTS_PATH.write_text(
        json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nDetails saved to {RESULTS_PATH}")


if __name__ == "__main__":
    main()