import os
import sys
import chromadb
from google import genai
# NEW: Import the embedding function from Chroma
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()


# Define models
# Use the open-source model, just like in index_commits.py
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
GENERATIVE_MODEL = 'gemini-2.5-flash'
DB_PATH = "./chroma_db"
# Must match the collection name from index_commits.py
COLLECTION_NAME = "git_commits_st"

def main():
    # Initialize the generative model client (new SDK style)
    try:
        client = genai.Client()
        print("Successfully initialized Gemini client.")
    except Exception as e:
        print(f"Error initializing generative model client: {e}")
        print("Please check your API key and that the model name is correct.")
        sys.exit(1)

    # Initialize ChromaDB client (persistent)
    try:
        # Initialize the same embedding function used for indexing
        print("Loading open-source embedding model...")
        st_embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL_NAME
        )
        
        dbClient = chromadb.PersistentClient(path=DB_PATH)
        # Tell Chroma to use this embedding function when getting the collection
        collection = dbClient.get_collection(
            name=COLLECTION_NAME,
            embedding_function=st_embedding_function
        )
        print(f"Connected to ChromaDB. Found {collection.count()} indexed commits.")
    except Exception as e:
        print(f"Error connecting to ChromaDB at '{DB_PATH}': {e}")
        print(f"Make sure you have indexed a repo into the '{COLLECTION_NAME}' collection.")
        print("Run 'python index_commits.py /path/to/repo' first?")
        sys.exit(1)
        
    print("\n--- GenAI Git-Bot (Hybrid Mode) ---")
    print("Using local embeddings and Gemini for answers.")
    print("Ask questions about your commit history. Type 'exit' or 'quit' to end.")

    while True:
        try:
            # 1. Get user query
            user_query = input("\nQuery: ").strip()
            
            if user_query.lower() in ['exit', 'quit']:
                print("Exiting...")
                break
                
            if not user_query:
                continue

            print("Searching database (using local model)...")
            # 2. Query ChromaDB for relevant commits
            # We pass the text query, and Chroma handles the embedding
            results = collection.query(
                query_texts=[user_query],
                n_results=5  # Get top 5 most relevant commits
            )
            
            context_documents = results['documents'][0]
            
            if not context_documents:
                print("Answer: I couldn't find any relevant commits in the database to answer that question.")
                continue

            # 4. Build the prompt for the generative model
            context = "\n\n---\n\n".join(context_documents)
            
            prompt = f"""
            You are a helpful Git project assistant. Your task is to answer the user's question based *only*
            on the provided Git commit data. Do not make up information. If the answer is not
            in the provided commits, say so.

            Here is the relevant commit data:
            ---
            {context}
            ---

            User's Question:
            {user_query}

            Answer:
            """

            print("Generating answer with Gemini...")
            # 5. Generate the answer
            response = client.models.generate_content(
                model=GENERATIVE_MODEL,
                contents=prompt
            )
            
            print(f"\nAnswer: {response.text}")

        except Exception as e:
            print(f"An error occurred: {e}")
        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()