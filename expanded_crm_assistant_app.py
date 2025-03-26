
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

        st.subheader("Sentiment Analysis (Context-Aware)")
        sentiment_map = {
            "love": "Advocate",
            "curious": "Engaged",
            "not sure": "Uncertain",
            "budget": "Explore [Budget Concern] Further",
            "interested": "Interested but Missing [Feature]",
            "pass": "Not a Fit",
            "scope": "Transactional",
            "timeline": "Transactional",
            "pricing": "Transactional"
        }

        if 'Transcript' in df.columns or 'Notes' in df.columns:
            text_col = 'Transcript' if 'Transcript' in df.columns else 'Notes'

            def assign_sentiment(text):
                text_lower = str(text).lower()
                for k, v in sentiment_map.items():
                    if k in text_lower:
                        return v
                return "Evaluating"

            def narrative_summary(sentiment, text):
                text = text.lower()
                if sentiment == "Engaged":
                    return "Client expressed curiosity and participated in idea exploration."
                elif sentiment == "Evaluating":
                    return "Client is weighing options and mentioned areas of uncertainty."
                elif sentiment == "Advocate":
                    return "Client expressed clear enthusiasm or agreement."
                elif sentiment == "Transactional":
                    return "Client directed the conversation toward cost, scope, or terms."
                elif sentiment == "Uncertain":
                    return "Client seemed unsure or lacked clarity on next steps."
                elif sentiment == "Skeptical":
                    return "Client challenged the solution or requested validation."
                elif sentiment == "Distant":
                    return "Client engaged passively or gave minimal responses."
                elif sentiment == "Unreceptive":
                    return "Client indicated disinterest or resistance."
                elif "missing" in sentiment:
                    return "Client interested, but noted a key missing feature or gap."
                elif "pain point" in sentiment:
                    return "Client described an ongoing issue or business challenge."
                else:
                    return "Client engagement type unclear, possibly neutral."

            df["Sentiment_Category"] = df[text_col].apply(assign_sentiment)
            df["Narrative_Summary"] = df.apply(lambda row: narrative_summary(row["Sentiment_Category"], row[text_col]), axis=1)
            st.dataframe(df[[text_col, "Sentiment_Category", "Narrative_Summary"]])

            lifetime_summary = "\n".join(df["Narrative_Summary"].unique())
            st.subheader("Lifetime Summary (Account-Level View)")
            st.text(lifetime_summary)
        else:
            st.warning("No 'Transcript' or 'Notes' column found for sentiment analysis.")

        st.subheader("Recommended Next Steps")
        st.markdown("""
- Wait for Response Until [Date]  
- Explore [Pain Point] Further  
- Get Clarification on [Point]  
- Client Needs [Specific Need]  
- May Be Responsive to Promotions  
- Interested but Missing [Feature]  
- Not a Fit – Consider Removing  
- High Intent – Prioritize Outreach  
- Loop in [Relevant Internal Role]  
- Re-engagement Opportunity  
- Deal at Risk – Escalate Internally
""")

    elif tool == "Visualize":
        st.header("🎯 Visualize: Client Journey & Funnels")

        chart_type = st.selectbox("Choose Chart Type", ["Line", "Bar", "Area", "Funnel"])
        color_scheme = st.color_picker("Pick a Chart Color", "#1f77b4")

        if 'Timestamp' in df.columns and 'Sentiment_Category' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
            timeline_data = df.dropna(subset=['Timestamp']).groupby([df['Timestamp'].dt.date, 'Sentiment_Category']).size().unstack(fill_value=0)

            if chart_type == "Line":
                st.line_chart(timeline_data)
            elif chart_type == "Bar":
                st.bar_chart(timeline_data)
            elif chart_type == "Area":
                st.area_chart(timeline_data)
        else:
            st.info("Sentiment visualization requires 'Timestamp' and 'Sentiment_Category' columns.")

        if chart_type == "Funnel":
            st.subheader("Conversion Funnel")
            funnel_data = pd.DataFrame({
                'Stage': ['Leads', 'MQLs', 'SQLs', 'Opportunities', 'Closed Won'],
                'Count': [100, 70, 45, 25, 10]
            })
            fig = px.funnel(funnel_data, x='Count', y='Stage', title="Conversion Funnel", color_discrete_sequence=[color_scheme])
            st.plotly_chart(fig)

else:
    st.info("Upload a CRM file to get started.")


    elif tool == "Report" and 'Sentiment_Category' in df.columns and 'Narrative_Summary' in df.columns:
        st.subheader("📥 Export Summary Report")
        if st.button("Generate CRM PDF Report"):
            from fpdf import FPDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="CRM Health & Account Insights Report", ln=True, align='C')
            pdf.ln(10)

            # Hygiene section (example)
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, txt="1. Data Hygiene Summary", ln=True)
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 8, txt="""- Hygiene tasks completed via app logic.
- Missing values flagged.
""")

            # Account summaries
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, txt="2. Account-Level Summaries", ln=True)
            pdf.set_font("Arial", size=11)
            for i, row in df[[text_col, "Sentiment_Category", "Narrative_Summary"]].iterrows():
                summary = row["Narrative_Summary"]
                pdf.multi_cell(0, 8, txt=f"- {summary}")
                pdf.ln(1)

            pdf_output_path = "generated_crm_report.pdf"
            pdf.output(pdf_output_path)
            with open(pdf_output_path, "rb") as f:
                st.download_button("Download PDF", f, file_name="CRM_Report_Summary.pdf")



    elif tool == "Report":
        st.subheader("📘 Branded Report Export")
        st.markdown("Customize and export reports with branding and improved formatting.")

        # Branding
        st.markdown("### 🔷 [Your Company CRM Assistant]")
        st.image("https://upload.wikimedia.org/wikipedia/commons/a/ab/Logo_TV_2015.png", width=100)
        st.markdown("_CRM Summary Report generated with your branding_")

        # Select specific account to export
        selected_account = st.selectbox("Select an Account for Export", df["account"].dropna().unique() if "account" in df.columns else [])

        if st.button("Generate PDF for Selected Account"):
            from fpdf import FPDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="Account Summary Report", ln=True, align='C')
            pdf.set_font("Arial", size=12)
            pdf.ln(10)

            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, txt=f"Account: {selected_account}", ln=True)
            pdf.set_font("Arial", size=11)
            subset = df[df["account"] == selected_account] if "account" in df.columns else df

            for _, row in subset.iterrows():
                summary = row.get("Narrative_Summary", "No narrative available")
                sentiment = row.get("Sentiment_Category", "N/A")
                transcript = row.get(text_col, "")

                pdf.set_font("Arial", 'B', 11)
                pdf.cell(0, 8, f"• Sentiment: {sentiment}", ln=True)
                pdf.set_font("Arial", size=11)
                pdf.multi_cell(0, 7, f"  Summary: {summary}")
                if transcript:
                    pdf.multi_cell(0, 6, f"  Notes: {transcript}")
                pdf.ln(3)

            pdf_output_path = "selected_account_report.pdf"
            pdf.output(pdf_output_path)
            with open(pdf_output_path, "rb") as f:
                st.download_button("Download Account PDF", f, file_name=f"{selected_account}_summary.pdf")
