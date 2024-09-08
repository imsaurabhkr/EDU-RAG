import os
import re
from pypdf import PdfReader
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
import google.generativeai as genai
import db  # Import db for fetching the API key

# Get Google API key from db.py
google_api_key = db.get_google_api_key()

class GeminiEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        if not google_api_key:
            raise ValueError("Google API Key not provided. Please provide it via db.get_google_api_key()")
        
        # print(f"Embedding input: {input}")
        genai.configure(api_key=google_api_key)
        model = "models/embedding-001"
        title = "Custom query"
        
        try:
            embedding_result = genai.embed_content(model=model, content=input, task_type="retrieval_document", title=title)["embedding"]
            # print("Embedding successfully generated.")
        except Exception as e:
            print(f"Error in generating embeddings: {e}")
            raise e
        
        return embedding_result

def load_pdf(file_path):
    # print(f"Loading PDF from: {file_path}")
    reader = PdfReader(file_path)
    text = "".join([page.extract_text() for page in reader.pages])
    # print("PDF loaded successfully and text extracted.")
    return text

def split_text(text, chunk_size=2000, overlap=200):
    chunks = []
    start = 0
    
    while start < len(text):
        end = min(start + chunk_size, len(text))  # Ensure we don't go beyond the length of the text
        chunks.append(text[start:end])
        start += chunk_size - overlap  # Move the start forward by chunk_size minus the overlap
        
    # print(f"Text split into {len(chunks)} chunks with {chunk_size} characters per chunk and {overlap} character overlap.")
    return chunks


def load_chroma_collection(path, name):
    # print(f"Loading Chroma collection from path: {path}, with collection name: {name}")
    chroma_client = chromadb.PersistentClient(path=path)
    
    # Check if the collection exists, create it if not
    try:
        db = chroma_client.get_collection(name=name, embedding_function=GeminiEmbeddingFunction())
        # print(f"Collection '{name}' loaded successfully.")
    except ValueError:
        # print(f"Collection '{name}' does not exist. Creating a new collection.")
        db = chroma_client.create_collection(name=name, embedding_function=GeminiEmbeddingFunction())
        # print(f"Collection '{name}' created successfully.")
    
    return db


def store_embeddings_in_chroma(text_chunks, chroma_collection):
    # print("Storing embeddings in Chroma...")
    
    # Generate unique IDs for each text chunk
    ids = [f"doc_{i}" for i in range(len(text_chunks))]
    
    # Add the documents and their IDs to the Chroma collection
    chroma_collection.add(documents=text_chunks, ids=ids)
    
    # print(f"Stored {len(text_chunks)} text chunks in Chroma.")

def get_relevant_passage(query, db, n_results=3):
    # print(f"Querying Chroma DB for: {query}")
    results = db.query(query_texts=[query], n_results=n_results)['documents'][0]
    # print(f"Relevant passage found: {results}")
    return results

def make_rag_prompt(query, relevant_passage):
    # print(f"Creating RAG prompt for query: {query}")
    escaped = relevant_passage.replace("'", "").replace('"', "").replace("\n", " ")
    # prompt = ("""You are a helpful and informative bot that answers questions using text from the reference passage included below. \
    #     Be sure to respond in a complete sentence, being comprehensive, including all relevant background information. \
    #     However, you are talking to a non-technical audience, so be sure to break down complicated concepts and \
    #     strike a friendly and conversational tone. \
    #     If the passage is irrelevant to the answer, you may ignore it.
    #     QUESTION: '{query}'
    #     PASSAGE: '{relevant_passage}'

    #     ANSWER:""").format(query=query, relevant_passage=escaped)
    prompt = ("""Answer the question as detailed as possible from the provided context,
        make sure to provide all the details, if the answer is not in
        provided context just say, "answer is not available in the context",
        don't provide the wrong answer\n\n
        Context:\n {relevant_passage}\n
        Question: \n{query}\n
        Answer:""").format(query=query, relevant_passage=escaped)
    # print("RAG prompt created.")
    return prompt

def generate_answer(prompt):
    if not google_api_key:
        raise ValueError("Google API Key not provided. Please provide it via db.get_google_api_key()")
    
    # print(f"Generating answer using Gemini model with prompt: {prompt[:100]}...")  # Only printing part of the prompt for readability
    genai.configure(api_key=google_api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    try:
        answer = model.generate_content(prompt)
        # print("Answer generated successfully.")
    except Exception as e:
        print(f"Error in generating answer: {e}")
        raise e
    
    return answer.text

def generate_answer_from_db(db, query):
    # print(f"Generating answer for query: {query}")
    relevant_text = get_relevant_passage(query, db, n_results=3)
    prompt = make_rag_prompt(query, relevant_passage="".join(relevant_text))
    answer = generate_answer(prompt)
    return answer

def gemini_chatbot(class_selected, subject_selected, chapter_selected, user_question, pdf_path=None):
    # print(f"Starting chatbot for class: {class_selected}, subject: {subject_selected}, chapter: {chapter_selected}")
    
    if pdf_path:
        # Load and process the PDF
        pdf_text = load_pdf(pdf_path)
        text_chunks = split_text(pdf_text, chunk_size=2000, overlap=200)
        
        chroma_collection = load_chroma_collection(path="Books/RAG/contents", name="rag_experiment")
        # Store embeddings
        store_embeddings_in_chroma(text_chunks, chroma_collection)
    else:
        print("No PDF path provided. Using existing Chroma collection.")
        chroma_collection = load_chroma_collection(path="Books/RAG/contents", name="rag_experiment")

    # print(f"Retrieving answer for question: {user_question}")
    answer = generate_answer_from_db(chroma_collection, query=user_question)
    # print(f"Answer retrieved: {answer}")
    return answer