# **********************************************************************************************#
# File name: newmain.py
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
import streamlit as st
#from openai import OpenAI
import configure 
from PIL import Image
img = Image.open(r"images.png")
st.set_page_config(page_title="DBQuery.AI", page_icon=img)
# from table_details import get_table_details , get_tables , itemgetter , create_extraction_chain_pydantic, Table , llm
#commenting below to focus on streamlit
from newlangchain_utils import *
import plotly.express as px
from io import BytesIO

col1, col2 = st.columns([1, 5])

with col1:
    st.image("img.jpg", width=110)

with col2:
    st.title("Database Assistant for Service Desk")

# Set OpenAI API key from Streamlit secrets
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
# May not be used
#client = OpenAI(api_key="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")

# Set a default model
# if "openai_model" not in st.session_state:
#     #May not be used
#     st.session_state["openai_model"] = "gpt-3.5-turbo"

# Define a list of subject areas
subject_areas = ['Employee', 'Customer', 'Medical', 'Manufacturing', 'Sales', 
                 'Finance']
if "selected_subject" not in st.session_state:
    st.session_state.selected_subject = subject_areas[0]

if "previous_subject" not in st.session_state:
    st.session_state.previous_subject = ""

# Create a dropdown menu to select a subject area
configure.selected_subject = st.selectbox("Select a Subject Area", subject_areas, index=subject_areas.index(st.session_state.selected_subject))
if configure.selected_subject != st.session_state.previous_subject:
    st.session_state.messages = []
    st.session_state.response = None
    st.session_state.tables_data = {}
    st.session_state.selected_subject = configure.selected_subject
    st.session_state.previous_subject = configure.selected_subject

# Define a global variable for selected_subject
# st.session_state.selected_subject = configure.selected_subject
# Display the selected subject area
st.write("You selected:", configure.selected_subject)

# table_details = get_table_details()
# table_details_prompt = f"""Return the names of ALL the SQL tables that MIGHT be relevant to the user question. \
# The tables are:

# {table_details}

# Remember to include ALL POTENTIALLY RELEVANT tables, even if you're not sure that they're needed."""
# print("From main.py Table_details_prompt: ", table_details_prompt)
# table_chain = {"input": itemgetter("question")} | create_extraction_chain_pydantic(Table, llm, system_message=table_details_prompt) | get_tables
models = ['gpt-3.5-turbo', 'gpt-4-turbo', 'gpt-4o']
selected_model = st.selectbox("Select a Model", models)
st.session_state.selected_model = selected_model

# # Initialize chat history
# if "messages" not in st.session_state:
#     # print("Creating session state")
#     st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
selected_subject_input = "What you would like to know about : Subject area - ", configure.selected_subject, "?" 
print(' '.join(selected_subject_input))
selected_subject_final = ' '.join(selected_subject_input)
# Accept user input
# if prompt := st.chat_input("What you would like to know about CI 360 UDM data?"):
if prompt := st.chat_input(selected_subject_final):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Generating response..."):
        response, chosen_tables, tables_data, agent_executor = invoke_chain(prompt, st.session_state.messages, selected_model)
        st.session_state.response = response
        st.session_state.chosen_tables = chosen_tables
        st.session_state.tables_data = tables_data
        x=response.split(";")[0]+";"
        y=response.split(";")[1]
        st.markdown(x)
        st.markdown(y)
        st.markdown(f"*Relevant Tables:* {', '.join(chosen_tables)}")
        # for table, data in tables_data.items():
        #     st.markdown(f"*Data from {table}:*")
        #     st.dataframe(data)
    st.session_state.messages.append({"role": "assistant", "content": response})
def plot_chart(data_df, x_axis, y_axis, chart_type):
    if chart_type == "Line Chart":
        fig = px.line(data_df, x=x_axis, y=y_axis)
    elif chart_type == "Bar Chart":
        fig = px.bar(data_df, x=x_axis, y=y_axis)
    elif chart_type == "Scatter Plot":
        fig = px.scatter(data_df, x=x_axis, y=y_axis)
    elif chart_type == "Pie Chart":
        fig = px.pie(data_df, names=x_axis, values=y_axis)
    elif chart_type == "Histogram":
        fig = px.histogram(data_df, x=x_axis, y=y_axis)
    elif chart_type == "Box Plot":
        fig = px.box(data_df, x=x_axis, y=y_axis)
    elif chart_type == "Heatmap":
        fig = px.density_heatmap(data_df, x=x_axis, y=y_axis)
    elif chart_type == "Violin Plot":
        fig = px.violin(data_df, x=x_axis, y=y_axis)
    elif chart_type == "Area Chart":
        fig = px.area(data_df, x=x_axis, y=y_axis)
    elif chart_type == "Funnel Chart":
        fig = px.funnel(data_df, x=x_axis, y=y_axis)
    else:
        st.write("Unsupported chart type selected")
        return
    
    st.plotly_chart(fig)
def download_as_excel(data, filename="data.xlsx"):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        data.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return output
if "response" in st.session_state and "tables_data" in st.session_state:
    for table, data in st.session_state.tables_data.items():
        st.markdown(f"Data from {table}:")
        st.dataframe(data)
        
        if not data.empty:
            x_axis = st.selectbox(f"Select X-axis", data.columns, key=f"x_axis_{table}")
            y_axis = st.selectbox(f"Select Y-axis", data.columns, key=f"y_axis_{table}")
            chart_type = st.selectbox(
                f"Select Chart Type", 
                ["Line Chart", "Bar Chart", "Scatter Plot", "Pie Chart", "Histogram", 
                 "Box Plot", "Heatmap", "Violin Plot", "Area Chart", "Funnel Chart"], 
                 key=f"chart_type_{table}"
            )
            if st.button(f"Generate Chart", key=f"generate_chart_{table}"):
                plot_chart(data, x_axis, y_axis, chart_type)
        excel_data = download_as_excel(data)
        st.download_button(
            label="Download as Excel",
            data=excel_data,
            file_name=f"{table}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )