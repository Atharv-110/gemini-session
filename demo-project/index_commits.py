import os
import sys
import git
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from datetime import datetime


# NEW: Define our local, open-source embedding model
# 'all-MiniLM-L6-v2' is a very popular, fast, and high-quality model.
# The first time you run this, it will download the model (a few hundred MB).
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2" 

DB_PATH = "./chroma_db"
# NEW: Let's use a new collection name to avoid errors
# This DB will store 'all-MiniLM-L6-v2' vectors, not Gemini vectors.
COLLECTION_NAME = "git_commits_st"

def get_commits_from_repo(repo_path):
    """
    Extracts commit data from a local Git repository.
    """
    try:
        repo = git.Repo(repo_path)
    except git.exc.InvalidGitRepositoryError:
        print(f"Error: Path '{repo_path}' is not a valid Git repository.")
        return [], [], []
    except git.exc.NoSuchPathError:
        print(f"Error: Path '{repo_path}' does not exist.")
        return [], [], []

    documents = []
    metadatas = []
    ids = []

    print(f"Reading commits from {repo_path}...")
    
    for commit in repo.iter_commits():
        commit_time = commit.committed_datetime.strftime("%Y-%m-%d %H:%M:%S")
        author = commit.author.name
        sha = commit.hexsha

        # Get the full 'git show' output for non-merge commits
        if len(commit.parents) > 1:
            # Handle merge commits: just index the message
            doc_content = (
                f"Author: {author}\n"
                f"Date: {commit_time}\n"
                f"Message: {commit.message}\n"
                f"Diff: --- Merge commit, no diff indexed ---"
            )
        else:
            # Handle regular and initial commits
            try:
                # repo.git.show() returns the full "git show" output as a string,
                # including author, date, message, and the code diff.
                doc_content = repo.git.show(sha)
            except Exception as e:
                print(f"Warning: Could not get diff for {sha}. Indexing message only. {e}")
                # Fallback to just indexing metadata if 'git show' fails
                doc_content = (
                    f"Author: {author}\n"
                    f"Date: {commit_time}\n"
                    f"Message: {commit.message}\n"
                    f"Diff: --- Error retrieving diff ---"
                )
        
        documents.append(doc_content)
        metadatas.append({
            "author": author,
            "date": commit_time,
            "sha": sha
        })
        ids.append(sha)

    print(f"Found {len(documents)} commits to process.")
    return documents, metadatas, ids

def create_and_store_embeddings(documents, metadatas, ids):
    """
    Stores documents in ChromaDB, which will *automatically* generate embeddings.
    """
    if not documents:
        print("No documents to index.")
        return

    # Initialize the embedding function
    print(f"Loading open-source embedding model: '{EMBEDDING_MODEL_NAME}'")
    # This will download the model from Hugging Face if you don't have it.
    st_embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL_NAME
    )

    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path=DB_PATH)
    
    # Get or create the collection, telling it to use our open-source model
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=st_embedding_function
    )

    print("Generating embeddings (locally) and indexing in ChromaDB...")
    
    try:
        existing_ids = set(collection.get(include=[])['ids'])
    except Exception as e:
        print(f"Note: Could not get existing IDs (collection might be empty). {e}")
        existing_ids = set()
        
    print(f"Found {len(existing_ids)} existing documents in the database.")

    # Filter out documents that are already indexed
    new_documents = []
    new_metadatas = []
    new_ids = []

    for doc, meta, id_str in zip(documents, metadatas, ids):
        if id_str not in existing_ids:
            new_documents.append(doc)
            new_metadatas.append(meta)
            new_ids.append(id_str)
            
    if not new_ids:
        print("All commits are already indexed. Database is up-to-date.")
        return

    print(f"Adding {len(new_ids)} new commits to the database...")
    print("ChromaDB will now generate embeddings for these. This may take a moment...")

    # Process in batches
    batch_size = 100 
    for i in range(0, len(new_documents), batch_size):
        batch_docs = new_documents[i:i + batch_size]
        batch_metas = new_metadatas[i:i + batch_size]
        batch_ids = new_ids[i:i + batch_size]

        print(f"Processing batch {i // batch_size + 1}...")

        # We just give Chroma the documents, and *it* runs the embedding function.
        try:
            collection.add(
                documents=batch_docs,
                metadatas=batch_metas,
                ids=batch_ids
            )
        except Exception as e:
            print(f"Error processing batch {i // batch_size + 1}: {e}")
            print("Skipping this batch.")
    
    print(f"\nSuccessfully indexed {len(new_ids)} new documents.")
    print(f"Database stored at: {DB_PATH}")
    print(f"Collection name: {COLLECTION_NAME}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python index_commits.py /path/to/your/git/repo")
        sys.exit(1)
        
    repo_path = sys.argv[1]
    
    documents, metadatas, ids = get_commits_from_repo(repo_path)
    
    if documents:
        create_and_store_embeddings(documents, metadatas, ids)

if __name__ == "__main__":
    main()