import streamlit as st
from dotenv import load_dotenv
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

import os
from dotenv import load_dotenv

load_dotenv()


## Langsmith tracking
os.environ['LANGCHAIN_API_KEY'] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "Q&A Chatbot with Gemini"


## Prompt Template
prompt=ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant.Please response to the user queries in a concise and informative manner."),
        ("user","Question: {question}"),
    ]
)


def generate_response(question,api_key,llm,temperature,max_tokens):
    llm = ChatGoogleGenerativeAI(
        model=llm,
        google_api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    output_parser=StrOutputParser()
    chain=prompt|llm|output_parser
    answer=chain.invoke({"question": question})
    return answer


## Title of the Streamlit app
st.title("Q&A Chatbot with Gemini")

## Sidebar for user inputs
st.sidebar.title("Settings")
api_key = st.sidebar.text_input("Enter your Gemini API Key", type="password")

## Dropdown for selecting the model
llm=st.sidebar.selectbox("Select", ["gemini-1.5-turbo", "gemini-1.5", "gemini-3.8-flash", "gemini-3.8", "gemini-2.1", "gemini-1.0", "gemini-1.0-mini"])


## Adjust response parameters
temperature=st.sidebar.slider("Temperature",min_value=0.0,max_value=1.0,value=0.7)
max_tokens=st.sidebar.slider("Max Tokens",min_value=50,max_value=1000,value=200)


## Main interface for user input and displaying the response

st.write("Go ahead and ask any questions")

user_input=st.text_input("Enter your question here:")

if user_input:
    response=generate_response(user_input,api_key,llm,temperature,max_tokens)
    st.write(response)

else:
    st.write("Please enter a question to get a response.")

