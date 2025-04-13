import streamlit as st
import pandas as pd
import duckdb

st.set_page_config(page_title="Data Craft Query Tool", layout="wide", page_icon="🧊", initial_sidebar_state="expanded")
st.title("📊 Data Craft Query Tool")

# Step 1: Upload CSV

with st.sidebar:
    if st.form("csv_ip_fomr"):
        uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
        if uploaded_file:
            st.header("CSV Options")
            # table_name = st.text_input("Table Name", value="df")
            delimiter = st.text_input("Delimiter", value=",")
            header = st.checkbox("First row is header", value=True)
            encoding = st.text_input("Encoding", value="utf-8")
            # load_csv_btn = st.button("Load data")

if uploaded_file:
    try:
        df = pd.read_csv(
            uploaded_file,
            delimiter=delimiter,
            header=0 if header else None,
            encoding=encoding
        )
        st.success("✅ CSV loaded successfully!")

        st.subheader("👀 Data Preview")
        st.dataframe(df.head())

        # Step 2: Adjust Data Types
        with st.expander("Click to Set Data Types of the columns"):
            st.subheader("🧩 Column Data Types")
            st.write('''
                In this section you can set up the data type of the columns
            ''')
        
            col_types = {}
            for col in df.columns:
                inferred_dtype = str(df[col].dtype)
                dtype = st.selectbox(
                    f"Select type for column: {col}",
                    ["string", "int", "float", "bool", "datetime"],
                    index=["string", "int", "float", "bool", "datetime"].index(
                        "string" if "object" in inferred_dtype else (
                            inferred_dtype if inferred_dtype in ["int", "float", "bool"] else "string"
                        )
                    )
                )
                col_types[col] = dtype

            # Apply conversions
            for col, dtype in col_types.items():
                try:
                    if dtype == "int":
                        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
                    elif dtype == "float":
                        df[col] = pd.to_numeric(df[col], errors="coerce")
                    elif dtype == "bool":
                        df[col] = df[col].astype("bool")
                    elif dtype == "datetime":
                        df[col] = pd.to_datetime(df[col], errors="coerce")
                    else:
                        df[col] = df[col].astype("string")
                except Exception as e:
                    st.warning(f"⚠️ Could not convert column {col} to {dtype}: {e}")

        # Step 3: SQL Query Interface
        st.subheader("🔍 Query with SQL")
        query = st.text_area("Write your SQL query below. Use 'df' as the table name.",
                            height=150,
                            value="SELECT * FROM df LIMIT 10")

        if st.button("Run Query"):
            try:
                con = duckdb.connect()
                con.register("df", df)
                result = con.execute(query).df()
                st.success("✅ Query executed successfully!")
                st.dataframe(result)
            except Exception as e:
                st.error(f"❌ Query failed: {e}")
    except Exception as e:
        st.error(f"❌ Failed to load CSV: {e}")
else:
    st.info("📂 Upload a CSV file to get started.")
