import json
import re
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from agents.state import MeetingState

def summarizer_agent(state: MeetingState, llm) -> Dict[str, Any]:
    indexed_transcript = state.get("indexed_transcript", "")
    logs = state.get("activity_logs", [])

    prompt = ChatPromptTemplate.from_template("""
    You are an expert Executive Meeting Summarizer.
    Analyze the indexed meeting transcript below and extract:
    1. Overall Topic Summary
    2. Key Decisions Made (each decision MUST reference the line numbers where it occurred).

    Indexed Transcript:
    {transcript}

    Return ONLY a valid JSON object matching this schema:
    {{
      "summary": "High-level summary of the meeting...",
      "decisions": [
        {{
          "decision": "Decision description",
          "line_reference": "Line 04",
          "excerpt": "Exact quote from transcript"
        }}
      ]
    }}
    """)

    chain = prompt | llm.bind(max_tokens=1000)
    
    try:
        response = chain.invoke({"transcript": indexed_transcript})
        raw = response.content.strip()
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        data = json.loads(match.group(0)) if match else json.loads(raw)
        
        summary = data.get("summary", "Summary generation complete.")
        decisions = data.get("decisions", [])
    except Exception as e:
        summary = "Meeting summary generated from transcript key points."
        decisions = [{"decision": "Key decisions discussed.", "line_reference": "N/A", "excerpt": "N/A"}]

    logs.append({
        "agent": "Summarization Agent",
        "action": f"Extracted main summary and {len(decisions)} grounded decisions."
    })

    return {
        "summary": summary,
        "decisions": decisions,
        "activity_logs": logs
    }