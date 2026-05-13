import streamlit as st
import pandas as pd
import plotly.express as px
from Agent import agent_main
import os


# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(
    page_title="JobFit AI",
    page_icon="🤖",
    layout="wide"
)

# ---------------- HEADER ---------------- #
st.title("🤖 JobFit AI — Resume–Job Matching Analytics System")
st.caption("Upload your resume and discover how well jobs match your profile")

st.divider()

# ---------------- INPUT SECTION ---------------- #
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    upload_resume = st.file_uploader(
        "📄 Upload Your Resume",
        type=["txt", "pdf"]
    )

with col2:
    position = st.text_input(
        "💼 Job Role",
        placeholder="AI Engineer"
    )

with col3:
    location = st.text_input(
        "📍 Location",
        placeholder="India"
    )

st.markdown("""
    <style>
    /* Target the 'Analyze Jobs' button */
    div.stButton > button {
        background-color: #FF4500 !important; /* OrangeRed */
        color: white !important;
        border-radius: 8px;
        border: none;
    }
    
    /* Target the 'Download' button specifically */
    div.stDownloadButton > button {
        background-color: #FF6347 !important; /* Tomato (Slightly lighter orange-red) */
        color: white !important;
        border-radius: 8px;
        border: none;
    }

    /* Hover effects */
    div.stButton > button:hover, div.stDownloadButton > button:hover {
        background-color: #FF7F50 !important; /* Coral */
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)
run_btn = st.button("🚀 Analyze Jobs", use_container_width=True)

# ---------------- JOB CARD FUNCTION ---------------- #
def render_job_cards(df, title, bg_color):
    st.subheader(title)

    if df.empty:
        st.info("No jobs found")
        return

    for _, row in df.iterrows():
        st.markdown(
            f"""
            <div style="
                background-color:{bg_color};
                padding:16px;
                border-radius:12px;
                margin-bottom:14px;
                box-shadow:0px 2px 8px rgba(0,0,0,0.08);
            ">
                <h4 style="margin-bottom:4px;">🏢 {row['company_name']}</h4>
                <p style="margin:0;">📍 {row['location']}</p>
                <a href="{row['company_url']}" target="_blank">🔗 View Job</a>
            </div>
            """,
            unsafe_allow_html=True
        )

# ---------------- PROCESS ---------------- #
if run_btn and upload_resume and position and location:

    with st.spinner("🔍 Fetching jobs & analyzing fit..."):
        is_txt = upload_resume.type == "text/plain"
        upload_resume.seek(0)
        if upload_resume.type == "text/plain":
            results = agent_main(upload_resume, position, location, is_txt)
        else:
            with open("resume.pdf", "wb") as file:
                file.write(upload_resume.getbuffer())
            results = agent_main("/home/arun-raja/Documents/VSC/resume.pdf", position, location, is_txt)
            

    st.success("✅ Analysis Completed")

    data = results["data"]

    # ---------------- KPI METRICS ---------------- #
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Jobs", results["total fetched"])
    col2.metric("Fit Jobs", results["jobs fit"])
    col3.metric("Not Fit Jobs", results["jobs nofit"])
    col4.metric("Avg Fit %", f"{results['fit mean']:.2f}")

    st.divider()

    # ---------------- CHARTS ---------------- #
    col1, col2 = st.columns(2)

    with col1:
        pie_fig = px.pie(
            data,
            names="prediction",
            title="Fit vs No-Fit Distribution",
            color_discrete_sequence=["#2ecc71", "#e74c3c"]
        )
        st.plotly_chart(pie_fig, use_container_width=True)

    with col2:
        company_counts = data["company_name"].value_counts().head(10)
        bar_fig = px.bar(
            company_counts,
            title="Top Hiring Companies",
            labels={"value": "Job Count", "index": "Company"}
        )
        st.plotly_chart(bar_fig, use_container_width=True)

    st.divider()

    # ---------------- JOB RESULTS ---------------- #
    tab1, tab2 = st.tabs(["✅ Best Matches", "❌ Not a Fit"])

    with tab1:
        fit_jobs = data[data["prediction"] == "Fit"]
        render_job_cards(
            fit_jobs,
            title="Jobs That Match Your Resume",
            bg_color="#eafaf1"
        )

    with tab2:
        nofit_jobs = data[data["prediction"] == "No Fit"]
        render_job_cards(
            nofit_jobs,
            title="Jobs That Didn't Match",
            bg_color="#fdecea"
        )

    # ---------------- DOWNLOAD BUTTON ---------------- #
    st.divider()

    csv_data = data.to_csv(index=False).encode("utf-8")
    
    st.download_button(
        label="⬇️ Download Job Match Results (CSV)",
        data=csv_data,
        file_name="job_fit_results.csv",
        mime="text/csv",
        use_container_width=True
    )

# ---------------- FOOTER ---------------- #
st.divider()
st.caption("🔐 Your resume is processed securely and never stored.")
