import asyncio
import os

from openai import AsyncOpenAI
from ragas.llms import llm_factory
from ragas.metrics.collections import ContextPrecision, ContextRecall, Faithfulness

from config.settings import EVAL_PAUSE_SECONDS, JUDGE_BASE_URL, JUDGE_MODEL
from src.generation.guardrails import CITATION_PATTERN


def build_metrics():
    """Gemini judge through Google's OpenAI-compatible endpoint."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY is missing. Add it to your .env file.")

    client = AsyncOpenAI(
        api_key=api_key,
        base_url=JUDGE_BASE_URL,
        max_retries=5,      # backs off and retries on rate limits (HTTP 429)
        timeout=120.0,
    )
    llm = llm_factory(JUDGE_MODEL, provider="openai", client=client)

    return {
        "faithfulness": Faithfulness(llm=llm),
        "context_recall": ContextRecall(llm=llm),
        "context_precision": ContextPrecision(llm=llm),
    }


def read_value(result):
    """Metric results carry the number in .value."""
    return float(getattr(result, "value", result))


async def run_metric(name, metric_call):
    """Await one metric. A failure becomes None so one bad call never stops the run."""
    try:
        result = await metric_call
        return read_value(result)
    except Exception as error:
        print(f"    {name} failed: {type(error).__name__}: {str(error)[:150]}")
        return None


async def add_ragas_scores(rows, items):
    """Score every answered question that has a reference. Adds scores to the rows."""
    metrics = build_metrics()
    items_by_id = {item.id: item for item in items}

    for row in rows:
        item = items_by_id[row["id"]]
        if row["refused"] or item.reference == "":
            continue

        print(f"  scoring {row['id']} ...")
        # Citation markers like [1] or 【1】 are not claims, so remove them first
        answer = CITATION_PATTERN.sub("", row["answer"]).strip()
        contexts = row["contexts"]

        row["faithfulness"] = await run_metric(
            "faithfulness",
            metrics["faithfulness"].ascore(
                user_input=item.question, response=answer, retrieved_contexts=contexts
            ),
        )
        row["context_recall"] = await run_metric(
            "context_recall",
            metrics["context_recall"].ascore(
                user_input=item.question,
                retrieved_contexts=contexts,
                reference=item.reference,
            ),
        )
        row["context_precision"] = await run_metric(
            "context_precision",
            metrics["context_precision"].ascore(
                user_input=item.question,
                reference=item.reference,
                retrieved_contexts=contexts,
            ),
        )
        await asyncio.sleep(EVAL_PAUSE_SECONDS)