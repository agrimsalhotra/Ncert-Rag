#########
SETUP
#########

1. Create a .env file in the main directory.
2. Copy .env.example in the .env file.
3. Add api keys for the models.
4. Add ncert pdfs from "https://drive.google.com/file/d/1xOJDQoqQXkGbnFTUQxnX8CY6fpPdnssh/view?usp=sharing" following the name format "class6_science_ch01.pdf" in the /data/raw folder.
5. run bash setup.



##############
BASH SETUP 
##############

python -m venv .venv

source .venv/Scripts/activate       

pip install --upgrade pip

pip install -r requirements.txt


##############
SCRIPTS
##############

1. Ingestion:
   python -m scripts.run_ingestion

2. Compare Chunking Strategies:
   python -m scripts.compare_chunking
   python -m scripts.compare_chunking --file class10_science_ch01.json

3. Indexing:
   python -m scripts.run_indexing

4. Search / Query:
   python -m scripts.run_search
   python -m scripts.run_query "What is a chemical reaction?"

##############
CHUNKING STRATEGIES IMPLEMENTED (src/chunking/)
##############
- Fixed Character Chunking (fixed.py): Strictly splits by character window with overlap.
- Recursive Character Chunking (recursive.py): Multi-level delimiter splitting (paragraphs, lines, sentences).
- Token-Based Chunking (token_based.py): BPE token-aware splitting (cl100k_base).
- Sentence & Semantic Chunking (semantic.py): Natural sentence boundary extraction preserving semantic flow.
- Markdown / Header Chunking (markdown.py): Splits along NCERT section headings (H1 to H5).
- Hierarchical Chunking (hierarchical.py): Parent-child chunking for high-precision retrieval and context expansion.


