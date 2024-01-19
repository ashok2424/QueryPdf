from dotenv import load_dotenv
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback

# Function to get OpenAI API Key from user input
def get_api_key():
    input_text = st.text_input(
        label="Please enter your OpenAI API Key",
        placeholder="Ex: sk-2twmA8tfCb8un4...",
        key="openai_api_key_input"
    )
    return input_text

# Function to load the Language Model (LLM)
def load_llm(openai_api_key):
    llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)
    return llm

# Main function for Streamlit app
def main():
    # Load environment variables
    load_dotenv()

    # Set Streamlit page configuration
    st.set_page_config(page_title="Ask your PDF")

    # Set app header with improved styling
    st.title("Ask your PDF 💬")
    st.markdown(
        "Upload a PDF and ask questions about its content using OpenAI's language model."
    )

    # File upload section
    pdf = st.file_uploader("Upload your PDF", type="pdf")

    # Get OpenAI API Key from user input
    openai_api_key = get_api_key()

    # Load Language Model (LLM)
    llm = load_llm(openai_api_key=openai_api_key)

    # Extract text from PDF
    if pdf is not None:
        pdf_reader = PdfReader(pdf)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        # Split text into chunks
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)

        # Create embeddings
        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        knowledge_base = FAISS.from_texts(chunks, embeddings)

        

        # Submit button 
        user_question = st.text_input("Ask a question about your PDF:")
        ask_question_button = st.button("Submit")

        # Handle user interaction
        if ask_question_button:
            # Display warning if no OpenAI API Key is provided
            if not openai_api_key:
                st.warning(
                    'Please insert OpenAI API Key. Instructions [here](https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key)',
                    icon="⚠️"
                )
                st.stop()

            # Perform similarity search
            with st.spinner("Processing..."):
                docs = knowledge_base.similarity_search(user_question)

                # Load question-answering chain
                chain = load_qa_chain(llm, chain_type="stuff")

                # Run the chain with user input
                with get_openai_callback() as cb:
                    response = chain.run(input_documents=docs, question=user_question)

            # Display the response
            st.success("Here's the answer:")
            st.write(response)

if __name__ == '__main__':
    main()
