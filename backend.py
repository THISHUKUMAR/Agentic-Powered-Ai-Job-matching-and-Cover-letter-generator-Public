import os
import pdfplumber
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, Tool
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
import requests

# 🔑 Load Gemini API key
os.environ["GOOGLE_API_KEY"] = "YOUR_GEMINI_API_KEY"

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.7)

# ------------------------
# Resume Processing
# ------------------------
def load_pdf_text(pdf_file):
    """Extract text from uploaded resume PDF"""
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def extract_resume_skills(resume_text):
    """Extract skills from resume using regex (simple demo)"""
    skills_pattern = re.compile(r"(Python|Java|C\+\+|Machine Learning|Deep Learning|NLP|Data Science|SQL|TensorFlow|PyTorch)", re.IGNORECASE)
    skills = set(re.findall(skills_pattern, resume_text))
    return list(skills)

# ------------------------
# Job Search (Mock API for now)
# ------------------------
def job_search_api(skills):
    """Mock job search API (replace with real Google Search API/SerpAPI later)"""
    jobs = [
        {
            "title": "AI Engineer",
            "company": "Google",
            "location": "Bangalore, India",
            "description": "Work on AI models and LLMs.",
            "link": "https://careers.google.com/jobs/results/"
        },
        {
            "title": "Machine Learning Engineer",
            "company": "Microsoft",
            "location": "Hyderabad, India",
            "description": "Develop scalable ML pipelines.",
            "link": "https://careers.microsoft.com"
        },
        {
            "title": "Data Scientist",
            "company": "TCS",
            "location": "Chennai, India",
            "description": "Build AI solutions for enterprise clients.",
            "link": "https://www.tcs.com/careers"
        }
    ]
    return jobs[:5]

def find_jobs(skills):
    """Find jobs based on extracted resume skills"""
    return job_search_api(skills)

# ------------------------
# Cover Letter Generator
# ------------------------
def generate_cover_letter(resume_text, job):
    """Generate a cover letter using Gemini"""
    prompt_template = PromptTemplate(
        input_variables=["resume", "job_title", "company", "job_description"],
        template="""
        You are an AI career assistant. Write a professional cover letter.
        Use the candidate's resume and the job description.

        Resume:
        {resume}

        Job Title: {job_title}
        Company: {company}
        Job Description: {job_description}

        Format:
        - Greeting
        - Opening paragraph (why applying, enthusiasm)
        - Body (skills, achievements relevant to role)
        - Closing (interest, polite thanks)
        - Signature
        """
    )

    chain = LLMChain(llm=llm, prompt=prompt_template, memory=ConversationBufferMemory())
    return chain.run(
        resume=resume_text,
        job_title=job["title"],
        company=job["company"],
        job_description=job["description"]
    )

# ------------------------
# Tools for Agent
# ------------------------
tools = [
    Tool(
        name="Resume Skill Extractor",
        func=lambda text: ", ".join(extract_resume_skills(text)),
        description="Extract skills from a candidate's resume text."
    ),
    Tool(
        name="Job Finder",
        func=lambda skills: str(find_jobs(skills.split(", "))),
        description="Find top job postings relevant to the given skills."
    ),
    Tool(
        name="Cover Letter Writer",
        func=lambda inputs: generate_cover_letter(inputs.split("||")[0], eval(inputs.split("||")[1])),
        description="Generate a personalized cover letter. Input must be 'resume_text || job_dict'."
    )
]

# ------------------------
# Initialize Agent
# ------------------------
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True
)
