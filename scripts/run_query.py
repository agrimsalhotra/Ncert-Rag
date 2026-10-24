import sys
import time

from src.generation.chain import NcertRag

DEMO_QUESTIONS = [
    "What is a balanced chemical equation and why must equations be balanced?",
    "How is Plaster of Paris prepared and what is it used for?",
    "Which metals react with cold water?",
    "What is photosynthesis?",                 # science, but not in the loaded chapters
    "Who won the 2011 cricket world cup?",     # unrelated on purpose
]


def print_answer(result, elapsed):
    print(f"\nQ: {result.question}   ({elapsed:.1f}s)")
    print(f"refused={result.refused}  reason={result.reason}")
    print(result.answer)
    for source in result.sources:
        print(f"  [{source.number}] {source.label}  (score {source.score:.3f})")


def main():
    rag = NcertRag()

    if len(sys.argv) > 1:
        questions = [" ".join(sys.argv[1:])]   # python -m scripts.run_query "your question"
    else:
        questions = DEMO_QUESTIONS

    for question in questions:
        start = time.perf_counter()
        result = rag.ask(question, class_num=10)
        print_answer(result, time.perf_counter() - start)


if __name__ == "__main__":
    main()