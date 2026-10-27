from langchain_classic.agents import create_openai_tools_agent
import streamlit as st
from pathlib import Path

from langchain_community.agent_toolkits import (
    create_sql_agent,
    SQLDatabaseToolkit
)

from langchain_community.utilities import SQLDatabase

from langchain_classic.agents import create_openai_tools_agent

from langchain_classic.agents import AgentExecutor

# from langchain.agents import AgentType

from langchain_community.callbacks.streamlit import (
    StreamlitCallbackHandler
)

from sqlalchemy import create_engine
from sqlalchemy.engine import URL

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


st.set_page_config(
    page_title="LangChain: Chat with SQL SB",
    page_icon="🤖"
)


LOCALDB="USE_LOCALDB"

MYSQL="USE_MYSQL"

## radio button to select database type

radio_opt=["Use SQLLite 3 Databse-Student.db","Connect to your SQL Database"]

selected_opt=st.sidebar.radio(label="Choose the DB which you want to chat",options=radio_opt)


# things required to connect with thw my sql databasel workbench
if radio_opt.index(selected_opt)==1:
    db_uri=MYSQL
    mysql_host=st.sidebar.text_input("Enter your MySQL Host:",value="localhost")
    mysql_port=st.sidebar.text_input("Enter your MySQL Port:",value="3306")
    mysql_user=st.sidebar.text_input("Enter your MySQL User:",value="root")
    mysql_password=st.sidebar.text_input("Enter your MySQL Password:",type="password")

else:
    db_uri=LOCALDB
    db_path=Path(__file__).parent/"Student.db"
    st.sidebar.write(f"Using Local Database: {db_path}")

api_key=st.sidebar.text_input(label="Enter your Groq API Key:",type="password")

if not db_uri:
    st.info("Please enter the database information and uri")

if not api_key:
    st.info("Please enter your Groq API Key to continue")

### LLM Model

llm = ChatGroq(
    api_key=api_key,
    model="openai/gpt-oss-20b",
    streaming=True,
    temperature=0
)

@st.cache_resource(ttl="2h") # till 2hrs keep it in a cache
def configure_db(
    db_uri,
    mysql_host=None,
    mysql_port=None,
    mysql_user=None,
    mysql_password=None
):
    if db_uri == LOCALDB:

        db_path = (Path(__file__).parent / "Student.db").absolute()

        engine = create_engine(
            f"sqlite:///{db_path}"
        )

    else:

        if not all([
            mysql_host,
            mysql_port,
            mysql_user,
            mysql_password
        ]):
            st.error("Please provide all MySQL connection details")
            return None

        connection_url = URL.create(
            drivername="mysql+pymysql",
            username=mysql_user,
            password=mysql_password,
            host=mysql_host,
            port=int(mysql_port),
            database="student_db"
        )

        engine = create_engine(connection_url)

    return engine


if db_uri == MYSQL:
    engine = configure_db(
        db_uri,
        mysql_host,
        mysql_port,
        mysql_user,
        mysql_password
    )
else:
    engine = configure_db(db_uri)

db = SQLDatabase(engine)


## toolkit for SQL database

## toolkit for SQL database

toolkit = SQLDatabaseToolkit(
    db=db,
    llm=llm
)

tools = toolkit.get_tools()


prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an agent designed to interact with a SQL database."),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = create_openai_tools_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    agent_type="ZERO_SHOT_REACT_DESCRIPTION"
)

## Chat history management
if "messages" not in st.session_state or st.sidebar.button("Clear Chat History"):
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "Hi, I'm a chatbot who can answer questions about the database. How can I help you?"
        }
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query=st.chat_input(
    placeholder="Ask me anything about the database"
)


if user_query:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_query
        }
    )

    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        st_cb=StreamlitCallbackHandler(st.container(),expand_new_thoughts=False)  ## Streamlit Callback Handler to show the thoughts and actions of the agent in the Streamlit app
        response = agent_executor.invoke(
            {
                "input": user_query
            },
            config={
                "callbacks": [st_cb]
            }
        )

        response = response["output"]
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response
            }
        )
        st.write(response)