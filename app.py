# app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

# --- Helper Function to read files ---
def load_data(file):
    """Function to load data based on file extension."""
    try:
        if file.name.endswith('.csv'):
            return pd.read_csv(file)
        elif file.name.endswith(('.xls', '.xlsx')):
            # Requires the 'openpyxl' library
            return pd.read_excel(file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None

# --- Page Configuration ---
st.set_page_config(page_title="Advanced Data Analysis Tool", layout="wide")
st.title("📊 Advanced Data Analysis Tool")

# --- Sidebar for File Upload ---
with st.sidebar:
    st.header("Upload Your Data")
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xls", "xlsx"])

# --- Main Page ---
if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    if df is not None:
        st.success("File successfully uploaded and loaded! 🎉")
        
        # --- Display Data and Basic Info ---
        st.header("1. Data Overview")
        st.dataframe(df.head())
        
        st.write("Data Shape:", df.shape)
        
        buffer = io.StringIO()
        df.info(buf=buffer)
        s = buffer.getvalue()
        st.text_area("Data Info:", s, height=250)
        
        st.header("2. Descriptive Statistics")
        st.dataframe(df.describe())

        # --- Data Cleaning Section ---
        st.header("3. Data Cleaning")
        
        # Handling Missing Values
        st.subheader("Handle Missing Values")
        if df.isnull().sum().sum() > 0:
            col1, col2 = st.columns(2)
            with col1:
                st.write("Missing Values Count:")
                st.dataframe(df.isnull().sum()[df.isnull().sum() > 0])
            with col2:
                missing_cols = df.columns[df.isnull().any()].tolist()
                selected_col_missing = st.selectbox("Select column to fill:", missing_cols)
                fill_method = st.radio("Choose method:", ('Mean', 'Median', 'Mode', 'Drop Rows'))
                
                if st.button("Apply Cleaning"):
                    if fill_method == 'Drop Rows':
                        df.dropna(subset=[selected_col_missing], inplace=True)
                    else:
                        if df[selected_col_missing].dtype in ['int64', 'float64']:
                            if fill_method == 'Mean':
                                fill_value = df[selected_col_missing].mean()
                            elif fill_method == 'Median':
                                fill_value = df[selected_col_missing].median()
                            else: # Mode
                                fill_value = df[selected_col_missing].mode()[0]
                            df[selected_col_missing].fillna(fill_value, inplace=True)
                        else: # For categorical columns
                            fill_value = df[selected_col_missing].mode()[0]
                            df[selected_col_missing].fillna(fill_value, inplace=True)
                    st.success(f"Cleaned column '{selected_col_missing}' using {fill_method}.")
        else:
            st.info("No missing values found in the dataset.")
            
        # Removing Duplicates
        st.subheader("Remove Duplicates")
        if df.duplicated().sum() > 0:
            st.write(f"Found {df.duplicated().sum()} duplicate rows.")
            if st.button("Remove Duplicate Rows"):
                df.drop_duplicates(inplace=True)
                st.success("Duplicate rows removed.")
        else:
            st.info("No duplicate rows found.")

        # --- Visualization Section ---
        st.header("4. Data Visualization")
        
        plot_type = st.selectbox("Select Plot Type", ["Histogram", "Bar Chart", "Scatter Plot", "Box Plot"])
        
        all_columns = df.columns.tolist()
        
        fig, ax = plt.subplots(figsize=(10, 6))

        if plot_type == "Histogram":
            num_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
            selected_col = st.selectbox("Select a numerical column:", num_cols)
            if selected_col:
                sns.histplot(df[selected_col], kde=True, ax=ax)
                st.pyplot(fig)

        elif plot_type == "Bar Chart":
            cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            selected_col = st.selectbox("Select a categorical column:", cat_cols)
            if selected_col:
                sns.countplot(x=df[selected_col], ax=ax)
                plt.xticks(rotation=45)
                st.pyplot(fig)
                
        elif plot_type == "Scatter Plot":
            num_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
            col_x = st.selectbox("Select X-axis column:", num_cols, index=0)
            col_y = st.selectbox("Select Y-axis column:", num_cols, index=1 if len(num_cols)>1 else 0)
            if col_x and col_y:
                sns.scatterplot(data=df, x=col_x, y=col_y, ax=ax)
                st.pyplot(fig)
        
        elif plot_type == "Box Plot":
            num_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
            selected_col = st.selectbox("Select a numerical column:", num_cols)
            if selected_col:
                sns.boxplot(y=df[selected_col], ax=ax)
                st.pyplot(fig)

else:
    st.info("Upload a file in the sidebar to get started.")
    st.image("https://i.imgur.com/3ZMLa42.png", caption="Data Analysis Workflow") # A generic placeholder image