import os
import pdfplumber
from typing import List, Dict, Any, Optional
# from serpapi import GoogleSearch
from serpapi import GoogleSearch
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# === Keys: read from environment ===
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # required
# SERPAPI_KEY = os.getenv("SERPAPI_KEY")        # required
GEMINI_API_KEY = "AIzaSyDbTr9ZzB3Ea5QjZOHjgI0zbwrns28F0QU"
SERPAPI_KEY = "138748f5f94c38001b07d51b3b2958a99e745b136d17c97f9120658ede679e41"

# --- Guard rails ---
# if not SERPAPI_KEY:
#     raise RuntimeError("Missing SERPAPI_KEY env var.")
# if not GEMINI_API_KEY:
#     raise RuntimeError("Missing GEMINI_API_KEY env var.")

# ---------------- PDF Loader ----------------
def load_pdf_text(uploaded_file) -> str:
    """Extract text from a PDF file-like object."""
    text = []
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text() or ""
            text.append(extracted)
    return "\n".join(text).strip()

# ---------------- Resume Skills Extractor (simple) ----------------
def extract_resume_skills(resume_text: str) -> List[str]:
    keywords = [
        "python","java","c++","sql","ai","ml","nlp","deep learning",
        "pytorch","tensorflow","cloud","aws","gcp","azure","data science",
        "react","node","docker","kubernetes","streamlit"
    ]
    found = [k for k in keywords if k in resume_text.lower()]
    # Title-case for display
    return [k.title() if not k.isupper() else k for k in found] or ["Software Engineer"]

# ---------------- Job Search via SerpAPI (Google Jobs) ----------------
def search_jobs(skills: List[str], location: str = "India", limit: int = 8) -> List[Dict[str, Any]]:
    """Use SerpAPI Google Jobs to fetch live jobs."""
    query = " ".join(skills[:5]) + " jobs"
    params = {
        "engine": "google_jobs",
        "q": query,
        "hl": "en",
        "gl": "in",              # tune as needed
        "location": location,    # SerpAPI will try to bias results
        "api_key": SERPAPI_KEY,
    }
    search = GoogleSearch(params)
    results = search.get_dict()

    jobs = []
    for job in results.get("jobs_results", [])[:limit]:
        title = job.get("title", "Untitled")
        company = job.get("company_name", "Unknown")
        loc = job.get("location", "")
        # Prefer full description if present, else snippet
        desc = (
            job.get("description")
            or job.get("description_snippet")
            or ""
        )
        # Apply link (first option if present)
        apply_link = "#"
        apply_options = job.get("apply_options") or []
        if isinstance(apply_options, list) and apply_options:
            apply_link = apply_options[0].get("link") or "#"

        jobs.append({
            "title": title,
            "company": company,
            "location": loc,
            "description": desc,
            "link": apply_link
        })

    return jobs
import re

def extract_resume_details(resume_text: str) -> dict:
    details = {}



    # Try to capture name (first line or near top)
    first_line = resume_text.split("\n")[0].strip()
    details["name"] = first_line if len(first_line.split()) <= 4 else "Candidate Name"

    # Phone number
    phone_match = re.search(r"\+?\d[\d\s-]{8,}\d", resume_text)
    details["phone"] = phone_match.group(0) if phone_match else "[Phone Number]"

    # Email
    email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", resume_text)
    details["email"] = email_match.group(0) if email_match else "[Email Address]"

    return details


# ---------------- Cover Letter Generator (no vector store) ----------------
def generate_cover_letter(resume_text: str, job: dict) -> str:
    details = extract_resume_details(resume_text)

    company_name = job.get("company", "Unknown Company")
    job_desc = job.get("description", "")
    job_title = job.get("title", "the role")

    final_prompt = f"""
    Write a professional cover letter for the job description below.
    Use the candidate's real details from their resume.

    Candidate Information:
    Name: {details['name']}
    Phone: {details['phone']}
    Email: {details['email']}

    Resume:
    {resume_text[:2000]}

    Job Title: {job_title}
    Job Description:
    {job_desc}

    Company: {company_name}

    The cover letter should follow this format:
    {details['name']}
    [Candidate Address]
    {details['phone']}
    {details['email']}

    [Date]

    Hiring Manager
    {company_name}

    Dear Hiring Manager,

    [Opening paragraph: Express interest in the role and company]
    [Body paragraph: Show alignment between candidate’s skills and job requirements]
    [Body paragraph: Highlight achievements/projects from resume]
    [Closing paragraph: Express enthusiasm and availability]

    Sincerely,
    {details['name']}
    """

    llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key="AIzaSyDbTr9ZzB3Ea5QjZOHjgI0zbwrns28F0QU"
    )

    # llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    response = llm.invoke(final_prompt)
    return response.content

