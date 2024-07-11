from examples import get_example_selector
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder,FewShotChatMessagePromptTemplate,PromptTemplate

example_prompt = ChatPromptTemplate.from_messages(
    [
        # ("human", "{input}\nSQLQuery:"),
         ("human", "{input}"),
        ("ai", "{query}"),
    ]
)
few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,
    example_selector=get_example_selector(),
    input_variables=["input","top_k"],
)

final_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", """You are a  PostgreSQL Query expert. Given an input question, create a syntactically correct query to run.Please provide the SQL query without any extra formatting or text.
Never generate table names or column names on your own.\n\nUnless otherwise specificed, Here is the relevant table info: {table_info}\n\nBelow are a number of examples of questions and their corresponding SQL queries."""),
        few_shot_prompt,
        MessagesPlaceholder(variable_name="messages"),
        ("human", "{input}"),
    ]
)
print ("This is final prompt ...." , final_prompt , " .. and this is few shot prompt.." , few_shot_prompt)
answer_prompt = PromptTemplate.from_template(
    """Given the user question, corresponding SQL query, and SQL result, answer the user question.
     Start with SQL query as first line of your answer then follow it with your answer in new line.
     Respond without modifying any of the nouns or numerical values. 
     DO NOT modify any of the nouns or numerical values received in SQL result.

Question: {question}
SQL Query: {query}
SQL Result: {result}
Answer: """
)
