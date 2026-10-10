from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.types import interrupt
from langgraph.checkpoint.memory import MemorySaver

from agents.state import MeetingState
from agents.summarizer import summarizer_agent
from agents.action_items import action_items_agent
from agents.reviewer import reviewer_agent

def human_clarification_node(state: MeetingState) -> Dict[str, Any]:
    """
    NATIVE HUMAN-IN-THE-LOOP INTERRUPT NODE:
    Pauses graph execution if unresolved items exist.
    """
    unresolved = state.get("unresolved_items", [])
    logs = state.get("activity_logs", [])

    if unresolved:
        logs.append({
            "agent": "Human-in-the-Loop",
            "action": f"⏸️ Graph paused via interrupt(). Awaiting user clarification for {len(unresolved)} items."
        })
        
        # Native interrupt pauses execution thread
        user_responses = interrupt({
            "message": "Action items missing owner/deadline require clarification.",
            "unresolved_items": unresolved
        })
        
        return {
            "user_clarifications": user_responses,
            "activity_logs": logs
        }
    
    return {"user_clarifications": {}, "activity_logs": logs}

def create_meeting_assistant_graph(llm):
    workflow = StateGraph(MeetingState)

    # 1. Register Nodes
    workflow.add_node("summarizer", lambda state: summarizer_agent(state, llm))
    workflow.add_node("action_extractor", lambda state: action_items_agent(state, llm))
    workflow.add_node("human_clarification", human_clarification_node)
    workflow.add_node("reviewer", lambda state: reviewer_agent(state, llm))

    # 2. Define Workflow Connections
    workflow.set_entry_point("summarizer")
    workflow.add_edge("summarizer", "action_extractor")
    workflow.add_edge("action_extractor", "human_clarification")
    workflow.add_edge("human_clarification", "reviewer")
    workflow.add_edge("reviewer", END)

    # MemorySaver Checkpointer is REQUIRED for interrupt/resume functionality
    checkpointer = MemorySaver()
    
    return workflow.compile(checkpointer=checkpointer)