examples = [
   {
        "input": "list all the employees",
        "query": "select * from lz_employee"
   },
#     {
#         "input": "what items people are searching for",
#         "query": "SELECT distinct(search_name) FROM fin_dbt_search"
#     },
#     {
#         "input": "Count of people with various Origination interaction ",
#         "query": "SELECT COUNT(INTERACTION) as count, interaction FROM fin_abt_attribution  group by interaction"
#     },
#     {
#         "input": "Count of landing Ad campaign visitors from location like city , country ",
#         "query": "SELECT COUNT(CU_CUSTOMER_ID), GE_CITY, GE_COUNTRY FROM FIN_DBT_ADV_CAMPAIGN_VISITORS group by GE_CITY, GE_COUNTRY"
#     },
#     {
#         "input": "Average time spent by visitors on web page or mobile session.",
#         "query": "SELECT AVG(ACTIVE_PAGE_VIEW_TIME) from FIN_DBT_CONTENT "
#     },
#     {
#         "input": "How many product view by products in last week",
#         # "query": "SELECT count(product_views), product_id FROM fin_dbt_ecommerce where WEEK(session_start_dttm_tz) = WEEK(CURRENT_DATE) - 1 group by product_id"
#         "query": "SELECT product_id, COUNT(product_views) AS total_product_views,DATE_TRUNC('WEEK', session_start_dttm_tz) as CurrentWeek FROM fin_dbt_ecommerce WHERE  CurrentWeek BETWEEN DATEADD('WEEK', -2, CURRENT_DATE()) AND CURRENT_DATE() GROUP BY product_id, CurrentWeek ;"
#     },
#     {
#      'input':"List all abandon forms in current month",
#      "query": "SELECT forms_started, forms_not_submitted , date_trunc('MONTH',session_start_dttm_tz ) as  CurrentMonth FROM fin_dbt_forms WHERE forms_started = 1 and forms_not_submitted=1 and  CurrentMonth between  DATEADD('MONTH', -1, CURRENT_DATE() ) and CURRENT_DATE() "   
#     },
#     {
#       'input':"How many emails have we send in each of the past 6 months?" ,
#       "query":"SELECT DATE_TRUNC ('MONTH', email_send_dttm) AS month,  COUNT(*) AS email_count FROM fin_email_send WHERE  email_send_dttm >= DATEADD (MONTH, -6, CURRENT_DATE) GROUP BY  month ORDER BY  month;"
#     },
#     {
#       'input':"How many emails have we send in last 6 months?" ,
#       "query":"SELECT  COUNT(*) AS email_count FROM  fin_email_send WHERE  fin_email_send.email_send_dttm >= DATEADD (MONTH, -6, CURRENT_DATE);"
#     },
#     {
#       'input':"How many emails have we send in last year?" ,
#       "query":"SELECT  COUNT(*) AS email_count FROM  fin_email_send WHERE  fin_email_send.email_send_dttm >= DATEADD (YEAR, -1, CURRENT_DATE);"
#     },
#     {
#       'input':"How many emails have we send in last quarter?" ,
#       "query":"SELECT COUNT(*) AS email_count , DATEADD (QUARTER, -1, CURRENT_DATE) as LAST_QUARTER FROM  fin_email_send WHERE fin_email_send.email_send_dttm >= DATEADD (QUARTER, -1, CURRENT_DATE) group by LAST_QUARTER;"
#     },
#     {
#       'input':"How many emails have we send in last 2 weeks?" ,
#       "query":"SELECT COUNT(*) AS email_count , DATEADD (WEEK, -2, CURRENT_DATE) as LAST_2_WEEKS FROM  fin_email_send WHERE  fin_email_send.email_send_dttm >= DATEADD (WEEK, -2, CURRENT_DATE) GROUP BY LAST_2_WEEKS;"
#     },
#     {
#       'input':"How many emails have we send between the today and 1st Apr 2024" ,
#       "query":"SELECT  COUNT(*) AS email_count FROM  fin_email_send WHERE  fin_email_send.email_send_dttm >= TO_DATE ('2024-04-01', 'YYYY-MM-DD')  AND fin_email_send.email_send_dttm < CURRENT_DATE;"
#     }

    
]

from langchain_community.vectorstores import Chroma
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings
import streamlit as st

@st.cache_resource
def get_example_selector():
    example_selector = SemanticSimilarityExampleSelector.from_examples(
        examples,
        OpenAIEmbeddings(),
        Chroma,
        k=2,
        input_keys=["input"],
    )
    return example_selector