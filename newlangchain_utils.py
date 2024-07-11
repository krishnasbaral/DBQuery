# **********************************************************************************************#
# File name: newlangchain_utils.py
# Created by: Krushna B.
# Creation Date: 25-Jun-2024
# Application Name: DBQUERY_NEW.AI
#
# Change Details:
# Version No:     Date:        Changed by     Changes Done         
# 01             25-Jun-2024   Krushna B.     Initial Creation
# 01             04-Jul-2024   Krushna B.     Added logic for data visualization 
# 
# **********************************************************************************************#
import os
import pandas as pd
from dotenv import load_dotenv


load_dotenv()

db_user = os.getenv("db_user")
db_password = os.getenv("db_password")
db_host=os.getenv("db_host")
#db_warehouse=os.getenv("db_warehouse")
db_database=os.getenv("db_database")
db_port=os.getenv("db_port")
db_schema= os.getenv("db_schema")  # Change if your schema is different
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2")
# LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
# LANGCHAIN_ENDPOINT=os.getenv("LANGCHAIN_ENDPOINT")


from langchain_community.utilities.sql_database import SQLDatabase
#from langchain.agents import create_sql_agent
#from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain.memory import ChatMessageHistory
from operator import itemgetter

from urllib.parse import quote_plus


from operator import itemgetter

from langchain_core.output_parsers import StrOutputParser

from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

from table_details import table_chain as select_table
from prompts import final_prompt, answer_prompt, few_shot_prompt
from table_details import get_table_details , get_tables , itemgetter , create_extraction_chain_pydantic, Table 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker



import streamlit as st
# @st.cache_resource
def get_chain(question, _messages, selected_model):
    llm = ChatOpenAI(model=selected_model, temperature=0)
    #db = SQLDatabase.from_uri(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")  
    table_details = get_table_details()
    table_details_prompt = f"""Return the names of ALL the SQL tables that MIGHT be relevant to the user question. \
    The tables are:

    {table_details}

    Remember to include ALL POTENTIALLY RELEVANT tables, even if you're not sure that they're needed."""
    print("From utis.py Table_details_prompt: ", table_details_prompt)
    table_chain = {"input": itemgetter("question")} | create_extraction_chain_pydantic(Table, llm, system_message=table_details_prompt) | get_tables



    chosen_tables=table_chain.invoke({"question": question})
    # chosen_tables=select_table.invoke({"question": question})
    print("tables chosen for query gen are: ... " , question , " ---" , chosen_tables)
    print("Creating DB Connection ... ")

    db = SQLDatabase.from_uri(f'postgresql+psycopg2://{quote_plus(db_user)}:{quote_plus(db_password)}@{db_host}:{db_port}/{db_database}'
                             ,schema=db_schema
                            #  , include_tables=['fin_abt_attribution', 'fin_dbt_adv_campaign_visitors', 'fin_dbt_content', 'fin_dbt_ecommerce', 'fin_dbt_forms', 'fin_dbt_goals', 'fin_dbt_search']
                            #  ,include_tables= chosen_tables
                             , view_support=True
                             ,sample_rows_in_table_info=1
                             ,lazy_table_reflection=True
                              )
    llm = ChatOpenAI(model=selected_model, temperature=0)
    print("Generate Query Starting")
    generate_query = create_sql_query_chain(llm, db, final_prompt)
    SQL_Statement = generate_query.invoke({"question": question, "messages": _messages})
    print(f"Generated SQL Statement before execution: {SQL_Statement}") 

    print("and messages..", _messages, "This is generated query..", SQL_Statement)
    execute_query = QuerySQLDataBaseTool(db=db)
    rephrase_answer = answer_prompt | llm | StrOutputParser()

    chain = (
        RunnablePassthrough.assign(table_names_to_use=table_chain) |
        RunnablePassthrough.assign(query=generate_query).assign(
            result=itemgetter("query") | execute_query
        ) | rephrase_answer
    )

    return chain, chosen_tables, SQL_Statement, db

def create_history(messages):
    history = ChatMessageHistory()
    for message in messages:
        if message["role"] == "user":
            history.add_user_message(message["content"])
        else:
            history.add_ai_message(message["content"])
    return history

def invoke_chain(question, messages, selected_model):
    history = create_history(messages)
    chain, chosen_tables, SQL_Statement, db = get_chain(question, history.messages, selected_model)
    print(f"Generated SQL Statement: {SQL_Statement}")
    SQL_Statement = SQL_Statement.replace("SQL Query:", "").strip()
    response = chain.invoke({"question": question, "top_k": 3, "messages": history.messages})
    print("Printing the question: ... ", question)
    print("Printing the response: ... ", response)
    print("Printing the chosen tables: ... ", chosen_tables)
    
    alchemyEngine = create_engine(f'postgresql+psycopg2://{quote_plus(db_user)}:{quote_plus(db_password)}@{db_host}:{db_port}/{db_database}')
    

    tables_data = {}
    for table in chosen_tables:
        query = response.split(";")[0] + ";"
        # result = db.run(query)
        print(f"Executing SQL Query: {query}")
        with alchemyEngine.connect() as conn:
            df = pd.read_sql(
                sql=query,
                con=conn.connection
            )
        # tables_data[table] = pd.DataFrame()
        tables_data[table] = df
        break 
    
    
    return response, chosen_tables, tables_data, db
