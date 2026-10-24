import time

from src.retrieval.search import NcertSearch

DEMO_QUESTIONS = [
    "What is a balanced chemical equation?",
    "Why does an aqueous solution of an acid conduct electricity?",
    "Write the reaction of sodium carbonate with HCl",
    "How does iron react with copper sulphate solution?",
    "Who won the 2011 cricket world cup?",   # out of syllabus on purpose
]


def main():
    searcher = NcertSearch()

    for question in DEMO_QUESTIONS:
        start = time.perf_counter()
        results = searcher.search(question, class_num=10)
        elapsed = time.perf_counter() - start

        print(f"\nQ: {question}   ({elapsed:.2f}s)")
        for parent, score in results:
            where = f"ch{parent.chapter_num} sec {parent.section_number or '-'}"
            preview = parent.text.replace("\n", " ")[:100]
            print(f"  {score:.3f} | {where:14} | {parent.content_type:8} | {preview}")


if __name__ == "__main__":
    main()