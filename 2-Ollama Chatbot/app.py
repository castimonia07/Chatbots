import os
import streamlit as st

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama

load_dotenv()

# LangSmith
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"] = "Q&A Chatbot with Ollama"


# Prompt
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a helpful assistant. "
        "Please respond to user queries in a concise and informative manner."
    ),
    ("user", "Question: {question}")
])


def generate_response(question, engine, temperature, max_tokens):

    llm = ChatOllama(
        model=engine,
        temperature=temperature,
        num_predict=max_tokens
    )

    output_parser = StrOutputParser()

    chain = prompt | llm | output_parser

    return chain.invoke({
        "question": question
    })


# UI
st.title("Q&A Chatbot with Ollama")

st.sidebar.title("Settings")

# Models installed in Ollama
model = st.sidebar.selectbox(
    "Select Model",
    ["gemma:2b", "mistral"]
)

temperature = st.sidebar.slider(
    "Temperature",
    min_value=0.0,
    max_value=1.0,
    value=0.7
)

max_tokens = st.sidebar.slider(
    "Max Tokens",
    min_value=50,
    max_value=1000,
    value=200
)

st.write("Go ahead and ask any questions")

user_input = st.text_input("Enter your question here:")

if user_input:

    response = generate_response(
        user_input,
        model,
        temperature,
        max_tokens
    )

    st.write(response)

else:
    st.write("Please enter a question to get a response.")