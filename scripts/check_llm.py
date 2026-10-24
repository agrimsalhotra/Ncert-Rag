from src.generation.llm import KEY_NAMES, build_single_llm


def main():
    for provider in KEY_NAMES:
        try:
            llm = build_single_llm(provider)
            reply = llm.invoke("Reply with the single word: ready")
            print(f"{provider:11} OK      -> {str(reply.content)[:60]!r}")
        except Exception as error:
            print(f"{provider:11} FAILED  -> {type(error).__name__}: {str(error)[:150]}")


if __name__ == "__main__":
    main()