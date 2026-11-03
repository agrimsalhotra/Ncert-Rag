import sys
import time

from src.generation.chain import NcertRag
from src.utils.logging_setup import configure_utf8_output

configure_utf8_output()


def print_answer(result, elapsed):
    print(f"\n({elapsed:.2f}s) refused={result.refused}  reason={result.reason}")
    print(f"\n{result.answer}\n")
    if result.sources:
        print("Sources:")
        for source in result.sources:
            print(f"  [{source.number}] {source.label}  (score {source.score:.3f})")
    print("-" * 60)


def main():
    print("Initializing NCERT RAG pipeline (loading models, vectorstore, and parent chunks)...")
    init_start = time.perf_counter()
    rag = NcertRag()
    init_elapsed = time.perf_counter() - init_start
    print(f"Ready in {init_elapsed:.2f}s! Type 'quit', 'exit', or 'q' to end the session.\n")

    # If arguments are passed on the CLI, run only that single query and exit
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:]).strip()
        start = time.perf_counter()
        result = rag.ask(question, class_num=10)
        print_answer(result, time.perf_counter() - start)
        return

    # Interactive session: models stay warm in RAM across all questions
    while True:
        try:
            query = input("Ask a question: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        if not query:
            continue

        if query.lower() in {"quit", "exit", "q"}:
            print("Session ended.")
            break

        start = time.perf_counter()
        result = rag.ask(query, class_num=10)
        elapsed = time.perf_counter() - start

        print_answer(result, elapsed)


if __name__ == "__main__":
    main()
