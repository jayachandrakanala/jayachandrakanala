import json
import re
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from agents.state import MeetingState

def action_items_agent(state: MeetingState, llm) -> Dict[str, Any]:
    indexed_transcript = state.get("indexed_transcript", "")
    logs = state.get("activity_logs", [])

    prompt = ChatPromptTemplate.from_template("""
    You are an Action Item Extraction Agent.
    Identify every task or action item mentioned in the meeting transcript.
    
    CRITICAL RULE:
    - If a task has no clear owner mentioned, set "owner" to "UNSPECIFIED".
    - If a task has no clear deadline mentioned, set "deadline" to "UNSPECIFIED".
    - DO NOT invent deadlines or owners under any circumstances.
    - Reference exact line numbers and excerpts for grounding.

    Indexed Transcript:
    {transcript}

    Return ONLY a valid JSON array of objects:
    [
      {{
        "id": "item_1",
        "task": "Task description",
        "owner": "Name or UNSPECIFIED",
        "deadline": "Date/Day or UNSPECIFIED",
        "line_reference": "Line 01",
        "excerpt": "Exact quote"
      }}
    ]
    """)

    chain = prompt | llm.bind(max_tokens=1200)
    
    try:
        response = chain.invoke({"transcript": indexed_transcript})
        raw = response.content.strip()
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        items = json.loads(match.group(0)) if match else json.loads(raw)
    except Exception:
        items = []

    unresolved = [
        item for item in items 
        if item.get("owner") == "UNSPECIFIED" or item.get("deadline") == "UNSPECIFIED"
    ]

    logs.append({
        "agent": "Action Items Agent",
        "action": f"Identified {len(items)} action items ({len(unresolved)} require clarification)."
    })

    return {
        "action_items": items,
        "unresolved_items": unresolved,
        "activity_logs": logs
    }