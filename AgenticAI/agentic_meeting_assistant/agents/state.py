from typing import TypedDict, List, Dict, Any, Optional

class MeetingState(TypedDict):
    # Inputs
    raw_transcript: str
    indexed_transcript: str  # Transcript with line numbers added
    
    # Intermediary outputs
    summary: str
    decisions: List[Dict[str, Any]]
    action_items: List[Dict[str, Any]]
    
    # Reviewer & Clarification state
    reviewer_passed: bool
    unresolved_items: List[Dict[str, Any]]  # Items missing owner/deadline
    user_clarifications: Optional[Dict[str, Any]]
    
    # Final Output Report & Logging
    final_report: str
    activity_logs: List[Dict[str, str]]