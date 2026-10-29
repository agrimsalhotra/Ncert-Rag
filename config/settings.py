# import os
# from pathlib import Path

# from dotenv import load_dotenv

# PROJECT_ROOT = Path(__file__).resolve().parent.parent
# load_dotenv(PROJECT_ROOT / ".env")   # reads API keys etc. from .env if the file exists

# RAW_DIR = PROJECT_ROOT / "data" / "raw"
# PARSED_DIR = PROJECT_ROOT / "data" / "parsed"
# CHUNKS_DIR = PROJECT_ROOT / "data" / "chunks"
# VECTORSTORE_DIR = PROJECT_ROOT / "data" / "vectorstore"
# EVAL_DIR = PROJECT_ROOT / "data" / "eval"
# MODELS_DIR = PROJECT_ROOT / "data" / "models"      # downloaded re-ranker model lives here

# # --- Embeddings & vector store ---
# EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"
# COLLECTION_NAME = "ncert_science_bge_small_v1"   # model name is in the collection name on purpose
# EMBED_BATCH_SIZE = 32

# # BGE models work best when search QUERIES (not passages) start with this sentence
# QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "

# # --- Retrieval ---
# RERANKER_MODEL_NAME = "ms-marco-MiniLM-L-12-v2"
# ANSWER_CONTENT_TYPES = ("concept", "activity")     # exercises are excluded from answers
# BM25_TOP_K = 15
# DENSE_TOP_K = 15
# HYBRID_WEIGHTS = (0.5, 0.5)                        # (bm25, dense)
# RERANK_TOP_N = 5                                   # child chunks kept after re-ranking
# MAX_PARENTS = 3                                    # parent sections passed to the LLM

# # --- Generation (hosted LLM APIs) ---
# # Comma-separated, in priority order: the first is used, the others are fallbacks.
# LLM_PROVIDERS = [
#     name.strip()
#     for name in os.getenv("LLM_PROVIDERS", "groq").split(",")
#     if name.strip() != ""
# ]
# LLM_TEMPERATURE = 0.0
# LLM_MAX_RETRIES = 1    # fail fast so the fallback provider can take over

# GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
# GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
# OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free")
# OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# # --- Guardrails ---
# REFUSAL_SCORE = 0.10       # best re-rank score below this -> refuse without calling the LLM
# MIN_PASSAGE_SCORE = 0.30   # passages scoring below this are not shown to the LLM

# # --- Evaluation ---
# GOLDEN_SET_PATH = EVAL_DIR / "golden_set.json"
# RESULTS_PATH = EVAL_DIR / "last_run.json"
# EVAL_CLASS_NUM = 10
# JUDGE_MODEL = os.getenv("JUDGE_MODEL", "gemini-2.5-flash")
# JUDGE_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
# EVAL_PAUSE_SECONDS = 4     # pause between questions to respect free-tier rate limits



import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")   # reads API keys etc. from .env if the file exists

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PARSED_DIR = PROJECT_ROOT / "data" / "parsed"
CHUNKS_DIR = PROJECT_ROOT / "data" / "chunks"
VECTORSTORE_DIR = PROJECT_ROOT / "data" / "vectorstore"
EVAL_DIR = PROJECT_ROOT / "data" / "eval"
MODELS_DIR = PROJECT_ROOT / "data" / "models"      # downloaded re-ranker model lives here

# --- Embeddings & vector store ---
EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"
COLLECTION_NAME = "ncert_science_bge_small_v1"   # model name is in the collection name on purpose
EMBED_BATCH_SIZE = 32

# BGE models work best when search QUERIES (not passages) start with this sentence
QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "

# --- Retrieval ---
# config/settings.py
RERANKER_MODEL_NAME = "ms-marco-TinyBERT-L-2-v2"  # ~5x faster on CPU than MiniLM-L-12-v2
BM25_TOP_K = 8                                    # down from 15
DENSE_TOP_K = 8
# RERANKER_MODEL_NAME = "ms-marco-MiniLM-L-12-v2"
ANSWER_CONTENT_TYPES = ("concept", "activity")     # exercises are excluded from answers
# BM25_TOP_K = 15
# DENSE_TOP_K = 15
HYBRID_WEIGHTS = (0.5, 0.5)                        # (bm25, dense)
RERANK_TOP_N = 8                                   # child chunks kept after re-ranking
MAX_PARENTS = 5
                                   # parent sections passed to the LLM

# --- Generation (hosted LLM APIs) ---
# Comma-separated, in priority order: the first is used, the others are fallbacks.
LLM_PROVIDERS = [
    name.strip()
    for name in os.getenv("LLM_PROVIDERS", "groq").split(",")
    if name.strip() != ""
]
LLM_TEMPERATURE = 0.0
LLM_MAX_RETRIES = 1    # fail fast so the fallback provider can take over

GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/free")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# --- Guardrails ---
REFUSAL_SCORE = 0.10       # best re-rank score below this -> refuse without calling the LLM
MIN_PASSAGE_SCORE = 0.30   # passages scoring below this are not shown to the LLM

# --- Evaluation ---
GOLDEN_SET_PATH = EVAL_DIR / "golden_set.json"
RESULTS_PATH = EVAL_DIR / "last_run.json"
EVAL_CLASS_NUM = 10
JUDGE_MODEL = os.getenv("JUDGE_MODEL", "gemini-3.8-flash")
JUDGE_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
EVAL_PAUSE_SECONDS = 4     # pause between questions to respect free-tier rate limits