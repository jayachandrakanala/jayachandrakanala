import streamlit as st
import os
import time

from langgraph.types import Command
from langgraph.errors import GraphInterrupt

from styles.custom_css import apply_custom_theme
from utils.transcript_parser import index_transcript
from utils.document_parser import parse_uploaded_file
from graph.workflow import create_meeting_assistant_graph

from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

# Streamlit Page Config
st.set_page_config(page_title="AI Meeting Assistant", page_icon="🎙️", layout="wide")
apply_custom_theme()

# Default Sample Transcript
DEFAULT_TRANSCRIPT = """Ravi: I will complete the API testing by Friday.
Priya: I will update the design document by Monday.
Ravi: We also need someone to review security.
Ankit: I can take up the security review, but I am not sure when I can finish it.
Priya: We decided to adopt PostgreSQL for our primary database architecture."""

# Initialize Session State Variables
if "thread_id" not in st.session_state:
    st.session_state.thread_id = "meeting_session_1"
if "app_graph" not in st.session_state:
    st.session_state.app_graph = None
if "unresolved_items" not in st.session_state:
    st.session_state.unresolved_items = []
if "final_report" not in st.session_state:
    st.session_state.final_report = None
if "activity_logs" not in st.session_state:
    st.session_state.activity_logs = []
if "graph_paused" not in st.session_state:
    st.session_state.graph_paused = False
if "transcript_text" not in st.session_state:
    st.session_state.transcript_text = DEFAULT_TRANSCRIPT

# Status Tracking
if "status_summarizer" not in st.session_state:
    st.session_state.status_summarizer = "⏳ Waiting"
if "status_action_items" not in st.session_state:
    st.session_state.status_action_items = "⏳ Waiting"
if "status_reviewer" not in st.session_state:
    st.session_state.status_reviewer = "⏳ Waiting"
if "progress_val" not in st.session_state:
    st.session_state.progress_val = 0
if "progress_text" not in st.session_state:
    st.session_state.progress_text = "Ready to start workflow."

# --- SIDEBAR CONTROL CENTER ---
with st.sidebar:
    st.title("⚙️ Control Center")
    llm_provider = st.selectbox("🧠 Select LLM Provider", ["Groq", "OpenAI"])
    
    if llm_provider == "Groq":
        model_engine = st.selectbox("⚡ Model Engine", ["qwen/qwen3.8-27b", "llama-3.3-70b-versatile", "mixtral-8x7b-32768"])
        api_key = st.text_input("🔑 Groq API Key", type="password", value=os.getenv("GROQ_API_KEY", ""), placeholder="gsk_...")
    else:
        model_engine = st.selectbox("⚡ Model Engine", ["gpt-4o", "gpt-4o-mini"])
        api_key = st.text_input("🔑 OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""), placeholder="sk-...")

def get_llm():
    if not api_key:
        st.error("Please provide a valid API Key in the sidebar.")
        st.stop()
    if llm_provider == "Groq":
        return ChatGroq(groq_api_key=api_key, model_name=model_engine, temperature=0.1)
    else:
        return ChatOpenAI(openai_api_key=api_key, model_name=model_engine, temperature=0.1)

def get_graph():
    llm = get_llm()
    if st.session_state.app_graph is None:
        st.session_state.app_graph = create_meeting_assistant_graph(llm)
    return st.session_state.app_graph

# Header
st.markdown("<h1 class='main-title'>🎙️ Multi-Agent AI Meeting Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Enterprise-Grade Grounded Meeting Summarizer & Task Extractor with Native Human-in-the-Loop Interrupts</p>", unsafe_allow_html=True)

# st.divider()

# --- FULL WIDTH TRANSCRIPT TEXT AREA ---
transcript_area = st.text_area(
    "📝 Meeting Transcript Input", 
    value=st.session_state.transcript_text, 
    height=200
)
st.session_state.transcript_text = transcript_area

# --- SINGLE LINE ACTION ROW: COMPACT FILE UPLOADER + RUN BUTTON ---
# Changed ratio to [1, 1] to cut file uploader width in half
col_file, col_btn = st.columns([1, 1], vertical_alignment="bottom")

with col_file:
    uploaded_file = st.file_uploader(
        "📂 Import Transcript File (.txt, .pdf, .docx)", 
        type=["txt", "pdf", "docx"], 
        label_visibility="visible"
    )
    if uploaded_file is not None:
        parsed_text = parse_uploaded_file(uploaded_file)
        if parsed_text and parsed_text != st.session_state.transcript_text:
            st.session_state.transcript_text = parsed_text
            st.success(f"Loaded '{uploaded_file.name}'!")
            st.rerun()

with col_btn:
    start_execution = st.button("🚀 Process Transcript & Run Agents", use_container_width=True)

st.divider()

# --- LIVE WORKFLOW PROGRESS CONSOLE ---
st.markdown("### 📡 Live Multi-Agent Workflow Execution")
progress_bar = st.progress(st.session_state.progress_val, text=st.session_state.progress_text)

c1, c2, c3 = st.columns(3)

def render_status_card(agent_title, status_str):
    color = "#a0a0b0"
    border = "#2d1b4e"
    if any(k in status_str for k in ["Processing", "Extracting", "Reviewing", "Verifying"]):
        color = "#ff007f"
        border = "#ff007f"
    elif any(k in status_str for k in ["Completed", "Verified", "Submitted"]):
        color = "#00ff66"
        border = "#00f0ff"
    elif "Paused" in status_str:
        color = "#ffaa00"
        border = "#ffaa00"
        
    return f"""
    <div class="status-card" style="border: 1px solid {border};">
        <b style="color: #ffffff; font-size: 1.05rem;">{agent_title}</b><br>
        <span style="color: {color}; font-weight: 700; font-size: 0.95rem;">Status: {status_str}</span>
    </div>
    """

with c1:
    summarizer_card = st.empty()
    summarizer_card.markdown(render_status_card("Agent 1: Summarize Agent", st.session_state.status_summarizer), unsafe_allow_html=True)
with c2:
    action_card = st.empty()
    action_card.markdown(render_status_card("Agent 2: Action Items Agent", st.session_state.status_action_items), unsafe_allow_html=True)
with c3:
    reviewer_card = st.empty()
    reviewer_card.markdown(render_status_card("Agent 3: QA Reviewer Agent", st.session_state.status_reviewer), unsafe_allow_html=True)

st.write(" ")

# --- NATIVE WORKSPACE TABS IN CHRONOLOGICAL ORDER ---
tab1, tab2, tab3 = st.tabs([
    "📡 Live Agent Console", 
    "🕵 User Clarifications (HITL)", 
    "📊 Reviewed Executive Report"
])

# --- TAB 1: LIVE AGENT CONSOLE ---
with tab1:
    st.subheader("📡 Real-Time Execution Logs")
    terminal_log_placeholder = st.empty()
    if st.session_state.activity_logs:
        log_text = "".join([f"⚡ [{entry['agent']}]: {entry['action']}\n" for entry in st.session_state.activity_logs])
        terminal_log_placeholder.code(log_text, language="bash")
    else:
        terminal_log_placeholder.info("Click 'Process Transcript & Run Agents' above to initiate agent workflow.")

# --- TAB 2: HUMAN-IN-THE-LOOP FORM ---
with tab2:
    st.subheader("🕵 User Clarifications (Human-in-the-Loop)")
    clarification_placeholder = st.empty()

    if st.session_state.graph_paused or (st.session_state.unresolved_items and not st.session_state.final_report):
        with clarification_placeholder.container():
            st.warning("⚠️ **Action items missing explicit details were detected in the transcript.**")
            st.info("Fill in missing Assignee or Deadline details below. Any field left blank will be recorded as 'UNSPECIFIED' in the final report.")

            with st.form("clarification_form"):
                user_responses = {}
                for idx, item in enumerate(st.session_state.unresolved_items, 1):
                    task_desc = item.get('task', f'Task {idx}')
                    line_ref = item.get('line_reference', 'N/A')
                    st.markdown(f"**Task {idx}: {task_desc}** *(Ref: {line_ref})*")
                    
                    curr_owner = item.get("owner", "UNSPECIFIED")
                    curr_deadline = item.get("deadline", "UNSPECIFIED")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        owner_val = st.text_input(
                            f"Assignee / Owner for Task {idx}:", 
                            value="" if curr_owner == "UNSPECIFIED" else curr_owner,
                            key=f"owner_{idx}"
                        )
                    with col_b:
                        deadline_val = st.text_input(
                            f"Deadline for Task {idx}:", 
                            value="" if curr_deadline == "UNSPECIFIED" else curr_deadline,
                            key=f"deadline_{idx}"
                        )
                    
                    item_id = str(item.get("id", f"item_{idx}"))
                    user_responses[item_id] = {
                        "owner": owner_val.strip() if owner_val.strip() else "UNSPECIFIED",
                        "deadline": deadline_val.strip() if deadline_val.strip() else "UNSPECIFIED"
                    }
                    st.divider()

                submit_clarification = st.form_submit_button("📩 Submit Clarifications & Resume LangGraph Thread")

            if submit_clarification:
                app_graph = get_graph()
                config = {"configurable": {"thread_id": st.session_state.thread_id}}
                
                st.session_state.status_reviewer = "🔄 Verifying & Evaluating Matrix..."
                st.session_state.progress_val = 85
                st.session_state.progress_text = "Resuming graph thread via Command(resume=...)..."
                
                with st.spinner("Passing Command(resume=...) to Reviewer Agent..."):
                    try:
                        for output in app_graph.stream(Command(resume=user_responses), config=config):
                            for node_name, node_state in output.items():
                                if "activity_logs" in node_state:
                                    st.session_state.activity_logs = node_state["activity_logs"]
                                if "final_report" in node_state and node_state["final_report"]:
                                    st.session_state.final_report = node_state["final_report"]
                                    st.session_state.status_reviewer = "✅ Verified & Generated"
                                    st.session_state.progress_val = 100
                                    st.session_state.progress_text = "Meeting analysis completed!"

                        st.session_state.graph_paused = False
                        st.rerun()
                    except Exception as ex:
                        st.error(f"Error resuming graph thread: {str(ex)}")

    elif st.session_state.final_report:
        clarification_placeholder.success("✅ Clarification phase completed! The final report matrix is ready in Tab 3.")
    else:
        clarification_placeholder.info("⏳ Awaiting graph execution. Unresolved items will appear here for clarification.")

# --- TAB 3: EXECUTIVE REPORT ---
with tab3:
    st.subheader("📊 Reviewed Executive Report")
    report_placeholder = st.empty()
    if st.session_state.final_report:
        report_placeholder.markdown(st.session_state.final_report)
    elif st.session_state.graph_paused:
        report_placeholder.info("⏳ Workflow paused via interrupt(). Provide missing details in **Tab 2 (User Clarifications)** to view final report.")
    else:
        report_placeholder.info("⏳ Click 'Process Transcript & Run Agents' above to analyze transcript.")


# --- GRAPH EXECUTION TRIGGER ---
if start_execution:
    if not st.session_state.transcript_text.strip():
        st.error("Please enter or upload a transcript first.")
    else:
        # Reset Session Variables
        st.session_state.thread_id = f"session_{int(time.time())}"
        st.session_state.app_graph = None
        st.session_state.activity_logs = []
        st.session_state.final_report = None
        st.session_state.unresolved_items = []
        st.session_state.graph_paused = False

        st.session_state.status_summarizer = "🔄 Processing..."
        st.session_state.status_action_items = "⏳ Waiting"
        st.session_state.status_reviewer = "⏳ Waiting"
        st.session_state.progress_val = 15
        st.session_state.progress_text = "Summarizer Agent extracting core topics & decisions..."

        app_graph = get_graph()
        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        indexed_text = index_transcript(st.session_state.transcript_text)

        initial_state = {
            "raw_transcript": st.session_state.transcript_text,
            "indexed_transcript": indexed_text,
            "summary": "",
            "decisions": [],
            "action_items": [],
            "unresolved_items": [],
            "user_clarifications": None,
            "final_report": "",
            "activity_logs": []
        }

        try:
            for output in app_graph.stream(initial_state, config=config):
                for node_name, node_state in output.items():
                    if "activity_logs" in node_state:
                        st.session_state.activity_logs = node_state["activity_logs"]
                    if "unresolved_items" in node_state:
                        st.session_state.unresolved_items = node_state["unresolved_items"]

                    if node_name == "summarizer":
                        st.session_state.status_summarizer = "✅ Completed"
                        st.session_state.status_action_items = "🔄 Extracting Tasks..."
                        st.session_state.progress_val = 45
                        st.session_state.progress_text = "Action Items Agent scanning assignees and deadlines..."

                    elif node_name == "action_extractor":
                        st.session_state.status_action_items = "✅ Completed"
                        st.session_state.progress_val = 75
                        
                        if st.session_state.unresolved_items:
                            st.session_state.status_reviewer = "⏸️ Paused via interrupt()"
                            st.session_state.progress_text = "Graph thread paused via interrupt(). Action items require clarification!"

                    # Live updates for status cards & logs
                    summarizer_card.markdown(render_status_card("Agent 1: Summarize Agent", st.session_state.status_summarizer), unsafe_allow_html=True)
                    action_card.markdown(render_status_card("Agent 2: Action Items Agent", st.session_state.status_action_items), unsafe_allow_html=True)
                    reviewer_card.markdown(render_status_card("Agent 3: QA Reviewer Agent", st.session_state.status_reviewer), unsafe_allow_html=True)

                    if st.session_state.activity_logs:
                        log_text = "".join([f"⚡ [{e['agent']}]: {e['action']}\n" for e in st.session_state.activity_logs])
                        terminal_log_placeholder.code(log_text, language="bash")

                    progress_bar.progress(st.session_state.progress_val, text=st.session_state.progress_text)
                    time.sleep(1.0)

            st.rerun()

        except GraphInterrupt:
            st.session_state.graph_paused = True
            st.session_state.status_reviewer = "⏸️ Paused via interrupt()"
            st.rerun()

        except Exception as e:
            if "429" in str(e) or "RateLimitError" in str(e):
                st.warning("⚠️ Rate limit encountered. Pausing 10s for quota reset...")
                time.sleep(10)
                st.rerun()
            else:
                st.error(f"Execution Error: {str(e)}")