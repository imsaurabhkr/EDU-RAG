import PyPDF2
import io
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.schema import Document
from langchain.chains import RetrievalQA

import db

# Load environment variables from db.py
google_api_key = db.get_google_api_key()

def load_pdf_from_path(pdf_path):
    """
    Load PDF from a given backend path and extract the text content.
    """
    print("pdf processing for chunk")
    with open(pdf_path, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        pdf_pages = pdf_reader.pages
        # Extract text from each page
        context = "\n\n".join(page.extract_text() for page in pdf_pages)
        return context

def split_documents(context):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    return text_splitter.split_text(context)

def initialize_embeddings():
    print("embedding initialize")
    # Initialize Google Generative AI Embeddings
    return GoogleGenerativeAIEmbeddings(model="models/embedding-001")

def store_embeddings_in_mongodb(texts, embeddings):
    """
    Store the PDF text embeddings into MongoDB Atlas.
    """
    print("Storing embeddings in MongoDB Atlas")
    mongo_collection = db.get_mongo_collection()
    index_name = db.get_index_name()

    # Convert texts to Document objects
    documents = [Document(page_content=text) for text in texts]
    
    # Initialize MongoDB vector search with embeddings
    MongoDBAtlasVectorSearch.from_documents(
        documents=documents,
        embedding=embeddings,
        collection=mongo_collection,
        index_name=index_name
    )
    
    return MongoDBAtlasVectorSearch.from_connection_string(
        db.get_mongo_uri(),
        f"{db.get_db_name()}.{db.get_collection_name()}",
        embeddings,
        index_name=index_name
    )

def get_vector_search(embeddings):
    return MongoDBAtlasVectorSearch.from_connection_string(
        db.get_mongo_uri(),
        f"{db.get_db_name()}.{db.get_collection_name()}",
        embeddings,
        index_name=db.get_index_name()
    )

def get_qa_retriever(vector_search):
    """
    Get the QA retriever using the vector search object with MongoDB Atlas.
    """
    return vector_search.as_retriever(
        search_type="cosine",
        search_kwargs={
            "k": 3,
            "post_filter_pipeline": [{"$limit": 2}]
        }
    )

def get_question_embedding(question, embeddings):
    # Get the embedding vector for the question
    return embeddings.embed_query(question)

# def user_query(question, vector_search):
    
#     # Implements _get_relevant_documents which retrieves documents relevant to a query.
#     retriever = vector_search.as_retriever()

#     # Load "stuff" documents chain. Stuff documents chain takes a list of documents,
#     # inserts them all into a prompt and passes that prompt to an LLM.
#     model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3, api_key=google_api_key)

#     qa = RetrievalQA.from_chain_type(model, chain_type="stuff", retriever=retriever)

#     # Execute the chain

#     retriever_output = qa.invoke(question)
#     print("output :",retriever_output)


#     # Return Atlas Vector Search output, and output generated using RAG Architecture
#     return retriever_output
    
#     # return docs


def gemini_chatbot(class_selected, subject_selected, chapter_selected, user_question, pdf_path=None):
    # Initialize embeddings
    embeddings = initialize_embeddings()

    if pdf_path:
        # Load and process the PDF document into chunks
        context = load_pdf_from_path(pdf_path)
        texts = split_documents(context)

        # Store embeddings into MongoDB and initialize vector search
        vector_search = store_embeddings_in_mongodb(texts, embeddings).as_retriever()
        # .as_retriever()
    else:
        # If no PDF is provided, use existing MongoDB vector search
        vector_search = get_vector_search(embeddings).as_retriever()

    # Get QA retriever from the vector search
    # qa_retriever = get_qa_retriever(vector_search)

    # Convert user question to embedding vector
    # question_embedding = get_question_embedding()

    # Perform similarity search with the embedding vector
    # docs = user_query(user_question, vector_search)
    docs = vector_search.invoke(user_question)
    print("retrieved_docs :",docs)

    # Define the prompt template for the response
    prompt_template = """
    Answer the question as detailed as possible from the provided context.
    If the answer is not in the provided context, give an answer based on your knowledge.
    Do not provide incorrect information.\n\n
    Context:\n {context}\n
    Question:\n{question}\n
    Answer:
    """

    # Create the prompt
    prompt = PromptTemplate(template=prompt_template, input_variables=['context', 'question'])

    # Initialize the Gemini model
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3, api_key=google_api_key)

    # Load QA Chain with the "stuff" method
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    # Get the response using the QA retriever and user question
    response = chain.invoke({"input_documents": docs, "question": user_question}, return_only_outputs=True)

    # Return the answer
    return response['output_text']