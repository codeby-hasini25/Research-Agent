import streamlit as st
import os
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

# =========================
# LOAD ENV
# =========================
load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# =========================
# LOGGING SYSTEM
# =========================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("INSIGHTAI")

# =========================
# CHECK KEYS
# =========================
if not OPENAI_KEY:
    st.error("❌ OPENAI API KEY missing")
    st.stop()

if not GEMINI_KEY:
    st.error("❌ GEMINI API KEY missing")
    st.stop()

# =========================
# AI MODELS
# =========================
openai_llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.3
)

gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.1
)

# =========================
# CORE FUNCTIONS
# =========================

def generate_openai_draft(query):
    system_prompt = """
    You are a senior AI research analyst.
    Generate a detailed, structured, deep explanation.
    """

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=query)
    ]

    result = openai_llm.invoke(messages)
    return result.content


def generate_gemini_review(query, draft):
    review_prompt = f"""
    You are a strict AI reviewer.

    Question: {query}

    Answer:
    {draft}

    Provide:
    1. Accuracy score (1-5)
    2. Missing points
    3. Improvements
    """

    result = gemini_llm.invoke([HumanMessage(content=review_prompt)])
    return result.content


def synthesize_final(query, draft, review):
    final_prompt = f"""
    Create final improved report.

    TOPIC: {query}

    DRAFT:
    {draft}

    REVIEW:
    {review}

    Structure:
    1. Executive Summary
    2. Detailed Explanation
    3. Improvements Applied
    4. Final Insights
    """

    result = openai_llm.invoke([HumanMessage(content=final_prompt)])
    return result.content


# =========================
# STREAMLIT UI
# =========================
st.set_page_config(page_title="InsightAI", layout="wide")

st.title("⚡ INSIGHTAI MULTI AI SYSTEM")
st.caption("OpenAI + Gemini Dual Intelligence Engine")

query = st.text_input("Enter your question")

col1, col2 = st.columns(2)

run_btn = col1.button("🚀 Run Analysis")
clear_btn = col2.button("🧹 Clear")

if clear_btn:
    st.rerun()

# =========================
# SESSION STATE
# =========================
if "history" not in st.session_state:
    st.session_state.history = []

# =========================
# MAIN PROCESS
# =========================
if run_btn and query:

    start_time = time.time()

    st.info("🧠 Step 1: OpenAI generating draft...")
    draft = generate_openai_draft(query)

    st.success("Draft Ready")

    st.subheader("📄 OPENAI DRAFT")
    st.write(draft)

    st.info("🔍 Step 2: Gemini reviewing...")
    review = generate_gemini_review(query, draft)

    st.subheader("🧾 GEMINI REVIEW")
    st.write(review)

    st.info("⚡ Step 3: Final synthesis...")
    final_output = synthesize_final(query, draft, review)

    st.subheader("🏁 FINAL OUTPUT")
    st.write(final_output)

    end_time = time.time()

    # Save history
    st.session_state.history.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "query": query,
        "draft": draft,
        "review": review,
        "final": final_output
    })

    st.success(f"Completed in {round(end_time - start_time, 2)} sec")

    # Download button
    file_content = f"""
    QUERY: {query}

    ======================
    DRAFT
    ======================
    {draft}

    ======================
    REVIEW
    ======================
    {review}

    ======================
    FINAL
    ======================
    {final_output}
    """

    st.download_button(
        label="📥 Download Report",
        data=file_content,
        file_name="insightai_report.txt"
    )

# =========================
# HISTORY PANEL
# =========================
st.sidebar.title("📜 History")

for item in reversed(st.session_state.history[-10:]):
    st.sidebar.write("----")
    st.sidebar.write("🕒", item["time"])
    st.sidebar.write("❓", item["query"])

# =========================
# FOOTER
# =========================
st.markdown("---")
st.caption("⚡ InsightAI System Running with OpenAI + Gemini")
