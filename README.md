#########
SETUP
#########

1. Create a .env file in the main directory.
2. Copy .env.example in the .env file.
3. Add api keys for the models.
4. Add ncert pdfs from "" following the name format "class6_science_ch01.pdf" in the /data/raw folder.
5. run bash setup.



##############
BASH SETUP 
##############

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt


##############
SCRIPTS
##############

python -m scripts.run_ingestion        
python -m scripts.run_indexing   
python -m scripts.run_search

python -m scripts.run_query
python -m scripts.run_query "Why is rusting a problem for iron articles?"     ####custom question
