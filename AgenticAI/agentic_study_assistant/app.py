import streamlit as st
import os
import time

from styles.custom_css import apply_custom_theme
from utils.document_parser import parse_uploaded_file
from graph.workflow import create_study_assistant_graph

from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

# Streamlit Page Config
st.set_page_config(page_title="LangGraph: Stateful Agentic AI", page_icon="🤖", layout="wide")

# --- INITIALIZE PERSISTENT SESSION STATES ---
if "summary" not in st.session_state:
    st.session_state.summary = None
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = None
if "activity_logs" not in st.session_state:
    st.session_state.activity_logs = []
if "evaluation_report" not in st.session_state:
    st.session_state.evaluation_report = None
if "corrections_made" not in st.session_state:
    st.session_state.corrections_made = []
if "quiz_start_time" not in st.session_state:
    st.session_state.quiz_start_time = None
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

# Status Tracking
if "agent_state_summary" not in st.session_state:
    st.session_state.agent_state_summary = "⏳ Waiting"
if "agent_state_quiz" not in st.session_state:
    st.session_state.agent_state_quiz = "⏳ Waiting"
if "agent_state_reviewer" not in st.session_state:
    st.session_state.agent_state_reviewer = "⏳ Waiting"
if "execution_progress" not in st.session_state:
    st.session_state.execution_progress = 0
if "progress_text" not in st.session_state:
    st.session_state.progress_text = "Ready to start workflow."

# --- SIDEBAR CONTROL CENTER ---
with st.sidebar:
    st.title("⚙️ Control Center")
    
    theme_choice = st.selectbox("🎨 UI Theme", ["Cyberpunk", "Dark Modern", "Neon Matrix"])
    apply_custom_theme(theme_choice)
    
    st.divider()
    
    llm_provider = st.selectbox("🧠 Select LLM", ["Groq", "OpenAI"])
    
    if llm_provider == "Groq":
        model_engine = st.selectbox("⚡ Model Engine", ["qwen/qwen3.8-27b", "qwen-2.5-32b", "llama-3.3-70b-versatile", "mixtral-8x7b-32768"])
        api_key = st.text_input("🔑 Groq API Key", type="password", value=os.getenv("GROQ_API_KEY", ""), placeholder="gsk_...")
        if not api_key:
            st.warning("⚠️ Enter GROQ API Key to initiate agents.")
    else:
        model_engine = st.selectbox("⚡ Model Engine", ["gpt-4o", "gpt-4o-mini"])
        api_key = st.text_input("🔑 OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""), placeholder="sk-...")
        if not api_key:
            st.warning("⚠️ Enter OpenAI API Key to initiate agents.")

    st.divider()
    agent_mode = st.selectbox("🚀 Agentic Workflow", ["Study Assistant (3-Agent)", "Summarizer Only", "Quiz Only"])

def get_llm():
    if not api_key:
        st.error("Please provide a valid API Key in the sidebar.")
        st.stop()
    if llm_provider == "Groq":
        return ChatGroq(
            groq_api_key=api_key, 
            model_name=model_engine, 
            temperature=0.1,
            max_retries=5,
            request_timeout=60.0
        )
    else:
        return ChatOpenAI(
            openai_api_key=api_key, 
            model_name=model_engine, 
            temperature=0.1,
            max_retries=5
        )

# --- MAIN HEADER ---
st.markdown("<h1 class='main-title'>🤖 Multi-Agent Study Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>⚡ Powered by LangGraph Stateful • Streamlit UI Architecture</p>", unsafe_allow_html=True)

st.divider()

col1, col2 = st.columns([1, 1])

with col1:
    uploaded_file = st.file_uploader("📂 Upload Study Material (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])

with col2:
    topic_prompt = st.text_input("🎯 Study Topic / Focus Area", value="Generative AI")
    user_query = st.text_area("💬 Specific Request", value="Help me understand Generative AI using the topic in this document, and test my understanding.", height=68)

start_execution = st.button("🚀 Process Document & Run Agents")

st.divider()

# --- PERMANENT LIVE EXECUTION CONSOLE ---
st.markdown("### 📡 Multi-Agent Workflow Execution Console")

progress_bar = st.progress(st.session_state.execution_progress, text=st.session_state.progress_text)

c1, c2, c3 = st.columns(3)

def render_status_card(agent_title, status_str):
    color = "#a0a0b0"
    border = "#2d1b4e"
    if any(k in status_str for k in ["Processing", "Generating", "Validating"]):
        color = "#ff007f"
        border = "#ff007f"
    elif any(k in status_str for k in ["Completed", "Validated", "Submitted"]):
        color = "#00ff66"
        border = "#00f0ff"
        
    return f"""
    <div style="background-color: #181224; padding: 12px; border-radius: 8px; border: 1px solid {border};">
        <b>{agent_title}</b><br>
        <span style="color: {color};">Status: {status_str}</span>
    </div>
    """

with c1:
    summarizer_status_placeholder = st.empty()
    summarizer_status_placeholder.markdown(render_status_card("Agent 1: Summarize Agent", st.session_state.agent_state_summary), unsafe_allow_html=True)

with c2:
    quiz_status_placeholder = st.empty()
    quiz_status_placeholder.markdown(render_status_card("Agent 2: Quiz Agent", st.session_state.agent_state_quiz), unsafe_allow_html=True)

with c3:
    reviewer_status_placeholder = st.empty()
    reviewer_status_placeholder.markdown(render_status_card("Agent 3: Reviewer Agent", st.session_state.agent_state_reviewer), unsafe_allow_html=True)

st.write(" ")
terminal_log_placeholder = st.empty()

if st.session_state.activity_logs:
    terminal_text = "".join([f"⚡ [{entry['agent']}]: {entry['action']}\n" for entry in st.session_state.activity_logs])
    terminal_log_placeholder.code(terminal_text, language="bash")


# --- HELPER FUNCTIONS FOR INTERACTIVE RENDERING ---
def run_reviewer_evaluation(user_answers):
    llm = get_llm()
    from agents.reviewer import reviewer_agent
    
    eval_state = {
        "document_text": "",
        "summary": st.session_state.summary,
        "quiz_questions": st.session_state.quiz_questions,
        "user_answers": user_answers,
        "activity_logs": st.session_state.activity_logs,
        "corrections_made": st.session_state.corrections_made
    }
    
    try:
        result = reviewer_agent(eval_state, llm)
        st.session_state.evaluation_report = result["reviewer_feedback"]
        st.session_state.activity_logs = result["activity_logs"]
        st.session_state.quiz_submitted = True
        st.session_state.agent_state_reviewer = "✅ Validated & Evaluated"
        st.session_state.execution_progress = 100
        st.session_state.progress_text = "Reviewer Agent completed answer evaluation."
    except Exception as ex:
        st.error(f"Evaluation Error: {str(ex)}")


def render_quiz_form_ui(target_container):
    with target_container.container():
        if st.session_state.quiz_questions and len(st.session_state.quiz_questions) > 0:
            if not st.session_state.quiz_submitted:
                elapsed = time.time() - st.session_state.quiz_start_time if st.session_state.quiz_start_time else 0
                remaining = max(0, 180 - int(elapsed))
                mins, secs = divmod(remaining, 60)
                
                if remaining > 0:
                    st.warning(f"⏳ **Time Remaining:** {mins:02d}:{secs:02d} (Auto-submits in 3 minutes)")
                else:
                    st.error("⏰ Time Expired! Auto-submitting current answers...")

                with st.form("quiz_form"):
                    user_selected_answers = {}
                    for idx, q in enumerate(st.session_state.quiz_questions, 1):
                        q_text = str(q.get('question', f'Question {idx}')).replace("###", "").replace("**", "").strip()
                        st.markdown(f"**Q{idx}: {q_text}**")
                        
                        opts = q.get('options', {})
                        options_list = [f"{k}: {v}" for k, v in opts.items()] if isinstance(opts, dict) else ["A: Option A", "B: Option B", "C: Option C", "D: Option D"]
                        
                        choice = st.radio(f"Select answer for Q{idx}:", options_list, key=f"q_{idx}")
                        user_selected_answers[idx] = choice.split(":")[0]
                        st.divider()
                    
                    submit_quiz = st.form_submit_button("📩 Submit Answers for Reviewer Evaluation")
                
                if submit_quiz or remaining == 0:
                    with st.spinner("Reviewer Agent evaluating your answers..."):
                        run_reviewer_evaluation(user_selected_answers)
                        st.rerun()
            else:
                st.success("✅ Assessment Submitted! Check the **'Reviewer Corrections'** tab for your personalized score and feedback.")
        else:
            st.info("⏳ Awaiting Quiz Agent completion...")


# --- DECLARE WORKSPACE TABS ---
st.divider()
tab1, tab2, tab3, tab4 = st.tabs([
    "📑 Topic Summary (Agent 1)", 
    "📝 Quiz Assessment (Agent 2)", 
    "🕵️ Reviewer Corrections (Agent 3)",
    "⚙️ Agent Logs"
])

with tab1:
    st.subheader("Summarize Agent Output")
    tab1_placeholder = st.empty()
    if st.session_state.summary:
        tab1_placeholder.markdown(st.session_state.summary)
    else:
        tab1_placeholder.info("⏳ Summarize Agent has not run yet. Click 'Process Document & Run Agents' above.")

with tab2:
    st.subheader("Quiz Assessment (5 Questions)")
    tab2_placeholder = st.empty()
    render_quiz_form_ui(tab2_placeholder)

with tab3:
    st.subheader("Reviewer Evaluation & Personalised Feedback")
    tab3_placeholder = st.empty()
    if st.session_state.evaluation_report:
        tab3_placeholder.markdown(st.session_state.evaluation_report)
    elif st.session_state.quiz_questions and not st.session_state.quiz_submitted:
        tab3_placeholder.info("⏳ Complete and submit the Quiz in Tab 2 to view Reviewer corrections and marks.")
    else:
        tab3_placeholder.info("⏳ Reviewer feedback will appear here after quiz submission.")

with tab4:
    st.subheader("⚙️ Agent Execution Logs")
    tab4_placeholder = st.empty()
    if st.session_state.activity_logs:
        log_html = "".join([f"<div class='log-box'><b>[{log['agent']}]</b>: {log['action']}</div>" for log in st.session_state.activity_logs])
        tab4_placeholder.markdown(log_html, unsafe_allow_html=True)
    else:
        tab4_placeholder.info("No activity logs recorded yet.")


# --- WORKFLOW TRIGGER EXECUTION ---
if start_execution:
    if not uploaded_file:
        st.error("Please upload a document first.")
    else:
        # Reset Session State
        st.session_state.summary = None
        st.session_state.quiz_questions = None
        st.session_state.activity_logs = []
        st.session_state.evaluation_report = None
        st.session_state.corrections_made = []
        st.session_state.quiz_start_time = None
        st.session_state.quiz_submitted = False
        
        st.session_state.agent_state_summary = "🔄 Processing..."
        st.session_state.agent_state_quiz = "⏳ Waiting"
        st.session_state.agent_state_reviewer = "⏳ Waiting"
        st.session_state.execution_progress = 10
        st.session_state.progress_text = "Summarize Agent extracting core concepts..."
        
        progress_bar.progress(10, text=st.session_state.progress_text)
        summarizer_status_placeholder.markdown(render_status_card("Agent 1: Summarize Agent", st.session_state.agent_state_summary), unsafe_allow_html=True)

        doc_text = parse_uploaded_file(uploaded_file)
        llm = get_llm()
        
        app_graph = create_study_assistant_graph(llm)
        
        initial_state = {
            "document_text": doc_text,
            "user_topic": topic_prompt,
            "user_answers": None,
            "summary": "",
            "quiz_questions": [],
            "reviewer_passed": True,
            "reviewer_feedback": "",
            "corrections_made": [],
            "activity_logs": []
        }

        try:
            for output in app_graph.stream(initial_state):
                for node_name, node_state in output.items():
                    if "activity_logs" in node_state:
                        st.session_state.activity_logs = node_state["activity_logs"]

                    if node_name == "summarizer":
                        summary_res = node_state.get("summary")
                        st.session_state.summary = summary_res
                        st.session_state.agent_state_summary = "✅ Completed"
                        st.session_state.agent_state_quiz = "🔄 Generating 5 MCQs..."
                        st.session_state.execution_progress = 40
                        st.session_state.progress_text = "Summarize Agent completed. Tab 1 Populated!"
                        
                        # RENDER TAB 1 IMMEDIATELY
                        tab1_placeholder.markdown(summary_res)
                        time.sleep(2.5) # Prevent Groq Rate Limit (HTTP 429)

                    elif node_name == "quiz_generator":
                        questions = node_state.get("quiz_questions", [])
                        st.session_state.quiz_questions = questions
                        st.session_state.quiz_start_time = time.time()
                        st.session_state.agent_state_quiz = "✅ Completed"
                        st.session_state.agent_state_reviewer = "⏳ Awaiting Student Submission"
                        st.session_state.execution_progress = 70
                        st.session_state.progress_text = "Quiz Agent completed. 5 MCQs Ready in Tab 2!"
                        
                        # RENDER TAB 2 IMMEDIATELY
                        render_quiz_form_ui(tab2_placeholder)
                        time.sleep(2.5)

                    elif node_name == "reviewer":
                        st.session_state.execution_progress = 100
                        st.session_state.agent_state_reviewer = "✅ Validated Quiz"
                        st.session_state.progress_text = "Workflow execution completed."

                    # Render terminal log and status cards live
                    terminal_text = "".join([f"⚡ [{entry['agent']}]: {entry['action']}\n" for entry in st.session_state.activity_logs])
                    terminal_log_placeholder.code(terminal_text, language="bash")

                    progress_bar.progress(st.session_state.execution_progress, text=st.session_state.progress_text)
                    summarizer_status_placeholder.markdown(render_status_card("Agent 1: Summarize Agent", st.session_state.agent_state_summary), unsafe_allow_html=True)
                    quiz_status_placeholder.markdown(render_status_card("Agent 2: Quiz Agent", st.session_state.agent_state_quiz), unsafe_allow_html=True)
                    reviewer_status_placeholder.markdown(render_status_card("Agent 3: Reviewer Agent", st.session_state.agent_state_reviewer), unsafe_allow_html=True)

            st.rerun()

        except Exception as e:
            if "429" in str(e) or "RateLimitError" in str(e):
                st.warning("⚠️ Groq Rate Limit reached. Pausing 20 seconds for quota reset...")
                time.sleep(20)
                st.rerun()
            else:
                st.error(f"Execution Error: {str(e)}")
                st.stop()