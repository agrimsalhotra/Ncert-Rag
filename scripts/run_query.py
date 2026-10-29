# import sys
# import time

# from src.generation.chain import NcertRag

# DEMO_QUESTIONS = [
#     "What is a balanced chemical equation and why must equations be balanced?",
#     "How is Plaster of Paris prepared and what is it used for?",
#     "Which metals react with cold water?",
#     "What is photosynthesis?",                 # science, but not in the loaded chapters
#     "Who won the 2011 cricket world cup?",     # unrelated on purpose
# ]


# def print_answer(result, elapsed):
#     print(f"\nQ: {result.question}   ({elapsed:.1f}s)")
#     print(f"refused={result.refused}  reason={result.reason}")
#     print(result.answer)
#     for source in result.sources:
#         print(f"  [{source.number}] {source.label}  (score {source.score:.3f})")


# # def main():
# #     rag = NcertRag()

# #     if len(sys.argv) > 1:
# #         questions = [" ".join(sys.argv[1:])]   # python -m scripts.run_query "your question"
# #     else:
# #         questions = DEMO_QUESTIONS

# #     for question in questions:
# #         start = time.perf_counter()
# #         result = rag.ask(question, class_num=10)
# #         print_answer(result, time.perf_counter() - start)
# # scripts/run_query.py
# def main():
#     rag = NcertRag()
#     if len(sys.argv) > 1:
#         questions = [" ".join(sys.argv[1:])]
#         for question in questions:
#             start = time.perf_counter()
#             result = rag.ask(question, class_num=10)
#             print_answer(result, time.perf_counter() - start)
#     else:
#         while True:
#             question = input("\nAsk a question (or 'q' to quit): ").strip()
#             if question.lower() in ("q", "quit", "exit", ""):
#                 break
#             start = time.perf_counter()
#             result = rag.ask(question, class_num=10)
#             print_answer(result, time.perf_counter() - start)

# if __name__ == "__main__":
#     main()
import sys
import time
from src.generation.chain import NcertRag


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