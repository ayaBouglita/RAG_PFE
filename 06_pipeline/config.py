from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SCHEMA_DIR = BASE_DIR / "01_schema"
SQL_DIR = BASE_DIR / "02_sql_examples"
RAG_DIR = BASE_DIR / "03_rag_docs"
PROMPTS_DIR = BASE_DIR / "04_prompts"
TESTS_DIR = BASE_DIR / "05_tests"
ARTIFACTS_DIR = BASE_DIR / "artifacts"

ARTIFACTS_DIR.mkdir(exist_ok=True)

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
FAISS_INDEX_PATH = ARTIFACTS_DIR / "faiss_index.bin"
DOCS_PATH = ARTIFACTS_DIR / "documents.json"

TOP_K = 5