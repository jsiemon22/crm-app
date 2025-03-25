
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import datetime

st.set_page_config(page_title="CRM Assistant", layout="wide")

# Sidebar Navigation
st.sidebar.title("CRM Assistant")
tool = st.sidebar.radio("Choose a tool:", ["Hygiene", "Report", "Visualize"])

# File Upload
st.sidebar.markdown("### Upload Your CRM File")
uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.write(f"### Data Preview ({uploaded_file.name})")
    st.dataframe(df.head())

    if tool == "Hygiene":
        st.header("🪜 Hygiene: Data Cleaning & Standardization")

        st.subheader("Missing Data")
        missing = df.isnull().sum()
        st.write(missing[missing > 0])

        st.subheader("Duplicate Detection")
        dupes = df[df.duplicated()]
        st.write(dupes if not dupes.empty else "No duplicates found.")

        st.subheader("Standardize Fields")
        st.markdown("Automatically convert all column headers to title case and trim spaces.")
        df.columns = [col.strip().title() for col in df.columns]
        st.success("Standardization complete. Column headers updated.")

        st.subheader("Data Conflicts")
        if 'Email' in df.columns:
            conflicts = df[df.duplicated(subset=['Email'], keep=False)]
            st.write(conflicts if not conflicts.empty else "No conflicts found based on Email.")

    elif tool == "Report":
        st.header("📊 Report: Activity Summary & Recommendations")

        st.subheader("Sentiment Analysis")
        st.markdown("Using custom sentiment categories...")

        sentiment_map = {
            "love": "Advocate",
            "curious": "Engaged",
            "not sure": "Uncertain",
            "budget": "Explore [Budget Concern] Further",
            "interested": "Interested but Missing [Feature]",
            "pass": "Not a Fit"
        }

        if 'Transcript' in df.columns:
            df['Sentiment_Category'] = df['Transcript'].apply(
                lambda x: next((v for k, v in sentiment_map.items() if isinstance(x, str) and k in x.lower()), "Evaluating")
            )
            st.write(df[['Transcript', 'Sentiment_Category']])
        else:
            st.warning("No 'Transcript' column found for sentiment analysis.")

        st.subheader("Recommended Next Steps")
        st.markdown("- Wait for Response Until [Date]  
- Explore [Pain Point] Further  
- Get Clarification on [Point]  
- Client Needs [Specific Need]")

    elif tool == "Visualize":
        st.header("🎯 Visualize: Client Journey & Funnels")

        st.subheader("Conversion Funnel")
        funnel_data = pd.DataFrame({
            'Stage': ['Leads', 'MQLs', 'SQLs', 'Opportunities', 'Closed Won'],
            'Count': [100, 70, 45, 25, 10]
        })
        fig = px.funnel(funnel_data, x='Count', y='Stage', title="Conversion Funnel")
        st.plotly_chart(fig)

        st.subheader("Sentiment Over Time (Simulated)")
        if 'Timestamp' in df.columns and 'Sentiment_Category' in df.columns:
            try:
                df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
                sentiment_count = df.groupby([df['Timestamp'].dt.date, 'Sentiment_Category']).size().unstack().fillna(0)
                st.line_chart(sentiment_count)
            except:
                st.warning("Couldn't generate sentiment trend. Check 'Timestamp' formatting.")
        else:
            st.info("Sentiment timeline requires 'Timestamp' and 'Sentiment_Category' columns.")

else:
    st.info("Upload a CRM file to get started.")
