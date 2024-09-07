import PyPDF2
import io
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import MongoDBAtlasVectorSearch
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.schema import Document
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
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=200)
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

def gemini_chatbot(class_selected, subject_selected, chapter_selected, user_question):

    # Initialize embeddings
    embeddings = initialize_embeddings()
    print("embeddings initialize")

    # Load the PDF document from the provided backend path
    pdf_path = None
    print("pdf loaded")

    if pdf_path:
        # Load the PDF document from the provided backend path
        context = load_pdf_from_path(pdf_path)
        print("PDF loaded")

        # Process the PDF content into chunks
        texts = split_documents(context)


        # Store embeddings into MongoDB and initialize vector search
        # Store the PDF embeddings into MongoDB Atlas
        vector_index = store_embeddings_in_mongodb(texts, embeddings).as_retriever()
        print("vector_index")

    else:
        # If no PDF is provided, use existing MongoDB vector search
        print("No PDF provided, using MongoDB vector search")
        vector_index = get_vector_search(embeddings).as_retriever()

    # Get relevant documents based on the user's question
    docs = vector_index.get_relevant_documents(user_question)
    print("docs")

    # Define Prompt Template
    prompt_template = """
    Answer the question as detailed as possible from the provided context,
    make sure to provide all the details, if the answer is not in
    provided context just say, "answer is not available in the context",
    don't provide the wrong answer\n\n
    Context:\n {context}\n
    Question: \n{question}\n
    Answer:
    """

    # Create Prompt
    prompt = PromptTemplate(template=prompt_template, input_variables=['context', 'question'])
    print("prompt generation")

    # Initialize the Gemini model
    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3, api_key=google_api_key)
    print("model initialize")

    # Load QA Chain
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    print("chain of thought's")
    # Get the response
    response = chain.invoke({"input_documents": docs, "question": user_question}, return_only_outputs=True)
    print("response get")
    print("response :",response)

    # Return the answer
    return response['output_text']
