import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import os
import re
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

# 🔐 Load API Key from Streamlit Secrets
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# 🤖 Load LLM
llm = ChatGroq(model_name="llama-3.1-8b-instant")

# 🧠 Prompt
prompt = PromptTemplate(
    input_variables=["question"],
    template="""
You are a SQL expert.

Table name: sales_data

Columns:
- "Product Name"
- Sales
- Category
- Profit

Rules:
- ALWAYS use exact column names
- ALWAYS wrap "Product Name" in quotes
- For product/category queries:
  → use GROUP BY
  → use ORDER BY DESC
  → LIMIT 10
- Return ONLY SQL query (no explanation, no markdown)

Question:
{question}
"""
)

# 🔍 SQL Generator
def generate_sql(question):
    formatted_prompt = prompt.format(question=question)
    response = llm.invoke(formatted_prompt)
    sql_query = response.content.strip()

    sql_query = re.sub(r"sql\s*|", "", sql_query)
    sql_query = sql_query.split("OR")[0].strip()

    return sql_query

# 🎨 PAGE CONFIG
st.set_page_config(page_title="AI SQL Analyst", layout="wide")

st.title("📊 AI SQL Data Analyst")

# 📂 SIDEBAR
st.sidebar.header("Upload & Query")

uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])
question = st.sidebar.text_input("Ask your question")
run = st.sidebar.button("Run Query")

# 📊 MAIN APP
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    conn = sqlite3.connect("data.db")
    df.to_sql("sales_data", conn, if_exists="replace", index=False)
    
    st.success("✅ Data uploaded successfully!")

    # 🔍 Data Preview
    st.subheader("📄 Data Preview")
    st.dataframe(df.head())

    if run and question:
        try:
            sql_query = generate_sql(question)

            st.subheader("🧾 Generated SQL")
            st.code(sql_query)

            df_result = pd.read_sql_query(sql_query, conn)

            st.subheader("📊 Results")
            st.dataframe(df_result)

            # 📈 Chart
            if df_result.shape[1] == 2:
                st.subheader("📈 Visualization")
                fig, ax = plt.subplots()
                ax.bar(df_result.iloc[:, 0], df_result.iloc[:, 1])
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                st.pyplot(fig)

        except Exception as e:
            st.error(f"❌ Error: {e}")

# 📌 FOOTER
st.markdown("---")
st.markdown("Built with ❤️ using AI + SQL + Streamlit")