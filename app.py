import os

import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv()

st.set_page_config(page_title="AI Career Roadmap & Skill Gap Finder", page_icon="🧭")
st.title("AI Career Roadmap & Skill Gap Finder")
st.write("Tell us your current skills and target role, and get a personalised 8-week plan.")


def get_api_key():
    """Read the Gemini key from .env first, then from Streamlit secrets."""
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        try:
            key = st.secrets["GEMINI_API_KEY"]
        except Exception:
            key = None
    return key


PROMPT_TEMPLATE = """You are an experienced career coach and technical mentor.

A student has the following profile:
- Current skills: {skills}
- Target job role: {role}
- Hours available per week: {hours}

Respond using EXACTLY this structure in Markdown. Do not add any text before or after it.

## Skill Gap Analysis

| Skill | Status | Notes |
|-------|--------|-------|

Fill the table with 6 to 10 rows covering the key skills for the role. Status must be either "Have" or "Need to learn".

## 8-Week Roadmap

### Week 1: <short title>
- **Goals:** ...
- **Topics:** ...
- **Milestone:** ...

Repeat this format for Weeks 2 through 8. Each week's workload must fit within {hours} hours per week.

## 3 Mini Project Ideas

1. **<Project name>**: one-sentence description and the skills it practises.
2. **<Project name>**: one-sentence description and the skills it practises.
3. **<Project name>**: one-sentence description and the skills it practises.
"""

with st.form("roadmap_form"):
    skills = st.text_input(
        "Current skills (comma-separated)",
        placeholder="e.g. C, basic Python, HTML",
    )
    role = st.text_input("Target job role", placeholder="e.g. Data Scientist")
    hours = st.number_input(
        "Hours you can study per week", min_value=1, max_value=60, value=10, step=1
    )
    submitted = st.form_submit_button("Generate roadmap")

if submitted:
    if not skills.strip() or not role.strip():
        st.warning("Please enter your current skills and a target role.")
    else:
        api_key = get_api_key()
        if not api_key:
            st.error("No Gemini API key found. Add GEMINI_API_KEY to your .env file or Streamlit secrets.")
            st.stop()

        prompt = PROMPT_TEMPLATE.format(skills=skills, role=role, hours=int(hours))

        with st.spinner("Building your roadmap..."):
            try:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Something went wrong while calling Gemini: {e}")
