import os
import streamlit as st
import textwrap
from backend import load_pdf_text, extract_resume_skills, search_jobs, generate_cover_letter

# --- Page config ---
st.set_page_config(
    page_title="Agentic AI Job Assistant",
    page_icon="🤖",
    layout="wide"
)

# --- Styling ---
st.markdown("""
<style>
/* General */
body { font-family: 'Segoe UI', sans-serif; background: #f9fafb; }
h1, h2, h3 { font-weight: 600; }
.stButton>button {
    border-radius: 12px;
    padding: 0.6rem 1rem;
    font-weight: 500;
    border: none;
    background: #2563eb;
    color: white;
}
.stButton>button:hover {
    background: #1d4ed8;
}
.stDownloadButton>button, .stLinkButton>button {
    border-radius: 12px;
    font-weight: 500;
    padding: 0.6rem 1rem;
}

/* Cards */
.card {
  border: 1px solid #e5e7eb;
  padding: 1.25rem;
  border-radius: 16px;
  margin-bottom: 1rem;
  background: #ffffff;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
.job-title { font-size: 1.15rem; font-weight: 600; margin-bottom: 0.3rem; }
.company { font-size: 1rem; font-weight: 500; color: #374151; }
.small-muted { color:#6b7280; font-size:0.9rem; margin-top:0.3rem; }
</style>
""", unsafe_allow_html=True)

# --- Title & Caption ---
st.title("🤖 Agentic AI Job Assistant")
st.caption("Upload your resume → Search jobs → Generate a tailored cover letter with Gemini AI")

# --- Step 1: Upload resume ---
st.header("📄 1) Upload your resume")
resume_file = st.file_uploader("Drag & drop your PDF resume", type=["pdf"])

resume_text = ""
if resume_file:
    resume_text = load_pdf_text(resume_file)
    if not resume_text.strip():
        st.error("Couldn't extract text from this PDF. Try another file.")
    else:
        st.success("✅ Resume loaded successfully!")
        skills = extract_resume_skills(resume_text)
        st.markdown("**Extracted Skills:** " + ", ".join(skills))

# --- Step 2: Search jobs ---
st.header("🔍 2) Search jobs")
col1, col2 = st.columns([2,1])
with col1:
    query_location = st.text_input("Preferred Location", value="India")
with col2:
    limit = st.number_input("Number of Jobs", min_value=3, max_value=15, value=6, step=1)

disable_search = not bool(resume_text.strip())
if st.button("🚀 Search Jobs", disabled=disable_search, use_container_width=True):
    if not resume_text.strip():
        st.warning("Please upload a resume first.")
    else:
        with st.spinner("Fetching jobs..."):
            jobs = search_jobs(skills, location=query_location, limit=limit)
        if not jobs:
            st.warning("No jobs found. Try changing location or upload a richer resume.")
        else:
            st.session_state["jobs"] = jobs

# --- Step 3: Show jobs + cover letter generation ---
jobs = st.session_state.get("jobs", [])
if jobs:
    st.header("💼 3) Recommended Jobs")
    cols = st.columns(2)  # two-column grid
    for idx, job in enumerate(jobs):
        with cols[idx % 2]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"<div class='job-title'>{job['title']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='company'>{job['company']} · {job.get('location','')}</div>", unsafe_allow_html=True)
            
            if job.get("description"):
                st.markdown(
                    f"<div class='small-muted'>{textwrap.shorten(job['description'], width=250, placeholder=' …')}</div>",
                    unsafe_allow_html=True
                )
            
            # Buttons row
            c1, c2 = st.columns(2)
            with c1:
                st.link_button("🌐 Apply", job.get("link", "#"), use_container_width=True)
            with c2:
                if st.button("✍️ Generate Cover Letter", key=f"gen_{idx}", use_container_width=True):
                    with st.spinner("AI is drafting your cover letter…"):
                        letter = generate_cover_letter(resume_text, job)
                    st.session_state[f"letter_{idx}"] = letter

            # Show cover letter if generated
            letter_key = f"letter_{idx}"
            if letter_key in st.session_state:
                st.markdown("**📄 Cover Letter**")
                st.text_area(
                    label=f"Cover Letter for {job['title']} @ {job['company']}",
                    value=st.session_state[letter_key],
                    height=280
                )
                st.download_button(
                    "📥 Download Cover Letter",
                    st.session_state[letter_key],
                    file_name=f"cover_letter_{idx+1}.txt",
                    use_container_width=True
                )

            st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("➡️ Upload your resume and search jobs to see recommendations.")
