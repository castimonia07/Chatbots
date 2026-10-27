import streamlit as st
from langchain_groq import ChatGroq

from langchain_community.utilities import (
    ArxivAPIWrapper,
    WikipediaAPIWrapper
)

from langchain_core.prompts import ChatPromptTemplate

from langchain_community.tools import (
    ArxivQueryRun,
    WikipediaQueryRun,
    DuckDuckGoSearchResults
)

from langchain.agents import create_agent

from langchain_community.callbacks.streamlit import StreamlitCallbackHandler

import os
from dotenv import load_dotenv


# ---------------------------------------------------------
# Creating Wrappers for Arxiv and Wikipedia
# ---------------------------------------------------------

arxiv_wrapper = ArxivAPIWrapper(
    top_k_results=1,
    doc_content_char_max=200
)

arxiv = ArxivQueryRun(
    api_wrapper=arxiv_wrapper
)


api_wrapper_wiki = WikipediaAPIWrapper(
    top_k_results=1,
    doc_content_chars_max=250
)

wiki = WikipediaQueryRun(
    api_wrapper=api_wrapper_wiki
)


# ---------------------------------------------------------
# DuckDuckGo Search Tool
# ---------------------------------------------------------

search = DuckDuckGoSearchResults(
    name="Search"
)


# ---------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------

st.title("🔎 LangChain - Chat with search")

"""
In this example, we're using StreamlitCallbackHandler
to display the thoughts and actions of an agent in an
interactive Streamlit app.

The agent can use different tools such as:
- DuckDuckGo
- Arxiv
- Wikipedia
"""


# ---------------------------------------------------------
# Sidebar for settings
# ---------------------------------------------------------

st.sidebar.title("Settings")

api_key = st.sidebar.text_input(
    "Enter your Groq API Key",
    type="password"
)


# ---------------------------------------------------------
# Chat history management
# ---------------------------------------------------------

if "messages" not in st.session_state:

    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "Hi, I'm a chatbot who can search the web. How can I help you?"
        }
    ]


# ---------------------------------------------------------
# Display previous messages
# ---------------------------------------------------------

for msg in st.session_state.messages:

    st.chat_message(
        msg["role"]
    ).write(
        msg["content"]
    )


# ---------------------------------------------------------
# User input
# ---------------------------------------------------------

if prompt := st.chat_input(
    placeholder="What is machine learning?"
):

    # Store user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    st.chat_message("user").write(prompt)


    # -----------------------------------------------------
    # Groq LLM
    # -----------------------------------------------------

    llm = ChatGroq(
        api_key=api_key,
        model="openai/gpt-oss-20b",
        streaming=True,
        temperature=0
    )


    # -----------------------------------------------------
    # Tools available to the agent
    # -----------------------------------------------------

    tools = [
        search,
        arxiv,
        wiki
    ]


    # -----------------------------------------------------
    # Create agent
    # -----------------------------------------------------

    search_agent = create_agent(
        model=llm,
        tools=tools
    )


    # -----------------------------------------------------
    # Generate response
    # -----------------------------------------------------

    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(
            st.container(),
            expand_new_thoughts=False
        )

        result = search_agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },
            config={
                "callbacks": [st_cb]
            }
        )

        # Get final response from agent
        response = result["messages"][-1].content


        # Store assistant response
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response
            }
        )


        # Display response
        st.write(response)


# ---------------------------------------------------------
# Explanation
# ---------------------------------------------------------

# """
# create_agent is the modern LangChain agent API.

# The agent can decide which tool to use based on the
# user's question.

# Available tools:

# 1. DuckDuckGo
#    -> General web search

# 2. Arxiv
#    -> Research papers

# 3. Wikipedia
#    -> General knowledge

# Flow:

# User Question
#       ↓
#     Agent
#       ↓
# Choose appropriate tool
#       ↓
# DuckDuckGo / Arxiv / Wikipedia
#       ↓
# Tool result
#       ↓
#     Agent
#       ↓
# Final Answer
# """