from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    # Inputs
    document_text: str
    user_topic: str
    user_answers: Optional[Dict[int, str]] # e.g. {1: "A", 2: "C", ...}
    
    # Agent Intermediaries & Outputs
    summary: str
    quiz_questions: List[Dict[str, Any]]
    
    # Reviewer Validation & Self-Correction
    reviewer_passed: bool
    reviewer_feedback: str
    corrections_made: List[str]
    
    # Execution Tracking
    activity_logs: List[Dict[str, str]]