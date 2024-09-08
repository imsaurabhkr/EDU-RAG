import chromadb

def delete_chroma_collection(path, name):
    # Create a persistent ChromaDB client
    chroma_client = chromadb.PersistentClient(path=path)
    
    # Check if the collection exists
    try:
        # Attempt to get the collection, if it exists
        chroma_client.get_collection(name=name)
        # If collection exists, delete it
        chroma_client.delete_collection(name=name)
        print(f"Collection '{name}' deleted successfully.")
    except ValueError as e:
        print(f"Collection '{name}' does not exist or has already been deleted.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
delete_chroma_collection(path="Books/RAG/contents", name="rag_experiment")
