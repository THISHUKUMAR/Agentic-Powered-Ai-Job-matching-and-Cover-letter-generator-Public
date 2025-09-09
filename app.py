import streamlit as st
from backend import load_pdf_text, extract_resume_skills, find_jobs, generate_cover_letter

st.set_page_config(page_title="🤖 Agentic AI Job Assistant", layout="wide")

st.title("🤖 Agentic AI Job Assistant")

# Step 1: Upload Resume
st.header("1. Upload Resume")
uploaded_resume = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

resume_text = ""
skills = []
if uploaded_resume:
    resume_text = load_pdf_text(uploaded_resume)
    skills = extract_resume_skills(resume_text)
    st.success("✅ Resume uploaded and processed!")
    st.write("**Extracted Skills:**", ", ".join(skills))

# Step 2: Find Jobs
st.header("2. Find Matching Jobs")
if st.button("🔍 Find Jobs") and resume_text:
    jobs = find_jobs(skills)

    if not jobs:
        st.warning("No jobs found. Try refining your resume or skills.")
    else:
        st.subheader("Top Job Matches")
        for idx, job in enumerate(jobs, start=1):
            with st.expander(f"Job {idx}: {job['title']} at {job['company']}"):
                st.write(f"**Title:** {job['title']}")
                st.write(f"**Company:** {job['company']}")
                st.write(f"**Location:** {job.get('location', 'Not specified')}")
                st.write(f"**Description:** {job['description']}")
                st.markdown(f"[Apply Here]({job['link']})")

                # Step 3: Cover Letter Generator
                if st.button(f"✍️ Generate Cover Letter for {job['company']}", key=f"cl_{idx}"):
                    letter = generate_cover_letter(resume_text, job)
                    st.text_area("Generated Cover Letter", letter, height=300)
                    st.download_button(
                        "📥 Download Cover Letter",
                        letter,
                        file_name=f"cover_letter_{job['company']}.txt"
                    )
