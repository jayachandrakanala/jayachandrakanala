from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.summarizer import summarizer_agent
from agents.quiz_generator import quiz_agent
from agents.reviewer import reviewer_agent

def create_study_assistant_graph(llm):
    workflow = StateGraph(AgentState)
    
    # 1. Bind nodes with LLM
    workflow.add_node("summarizer", lambda state: summarizer_agent(state, llm))
    workflow.add_node("quiz_generator", lambda state: quiz_agent(state, llm))
    workflow.add_node("reviewer", lambda state: reviewer_agent(state, llm))
    
    # 2. Define standard flow
    workflow.set_entry_point("summarizer")
    workflow.add_edge("summarizer", "quiz_generator")
    workflow.add_edge("quiz_generator", "reviewer")
    
    # 3. Conditional Self-Correction Loop (Reviewer -> Quiz Generator)
    def check_review_status(state: AgentState):
        if state.get("user_answers"):
            return END
        if state.get("reviewer_passed", True):
            return END
        else:
            return "quiz_generator" # Loop back to fix questions
            
    workflow.add_conditional_edges(
        "reviewer",
        check_review_status,
        {
            "quiz_generator": "quiz_generator",
            END: END
        }
    )
    
    return workflow.compile()