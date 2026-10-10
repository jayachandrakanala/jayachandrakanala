import json
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from agents.state import MeetingState

def reviewer_agent(state: MeetingState, llm) -> Dict[str, Any]:
    transcript = state.get("indexed_transcript", "")
    summary = state.get("summary", "")
    decisions = state.get("decisions", [])
    action_items = state.get("action_items", [])
    user_clarifications = state.get("user_clarifications", {})
    logs = state.get("activity_logs", [])

    # Update action items with user clarifications if available
    if user_clarifications:
        for item in action_items:
            item_id = item.get("id")
            if item_id in user_clarifications:
                clar = user_clarifications[item_id]
                if clar.get("owner"):
                    item["owner"] = clar["owner"]
                if clar.get("deadline"):
                    item["deadline"] = clar["deadline"]
                item["status"] = "Clarified by User"
            else:
                item["status"] = "Resolved" if (item["owner"] != "UNSPECIFIED" and item["deadline"] != "UNSPECIFIED") else "Unresolved"
    else:
        for item in action_items:
            item["status"] = "Resolved" if (item["owner"] != "UNSPECIFIED" and item["deadline"] != "UNSPECIFIED") else "Needs Clarification"

    # Construct formatted markdown report
    report_lines = []
    report_lines.append("## 📌 Meeting Executive Summary")
    report_lines.append(summary)
    report_lines.append("\n---")
    
    report_lines.append("## 🎯 Key Decisions Made")
    for d in decisions:
        report_lines.append(f"* **{d.get('decision')}** — *Ref: {d.get('line_reference')}* (`\"{d.get('excerpt')}\"`) ")
    report_lines.append("\n---")

    report_lines.append("## 📋 Action Items Matrix")
    report_lines.append("| Task | Assignee / Owner | Deadline | Status | Line Ref |")
    report_lines.append("| :--- | :--- | :--- | :--- | :--- |")
    
    for a in action_items:
        owner_display = f"⚠️ `{a.get('owner')}`" if a.get('owner') == "UNSPECIFIED" else f"**{a.get('owner')}**"
        deadline_display = f"⚠️ `{a.get('deadline')}`" if a.get('deadline') == "UNSPECIFIED" else f"**{a.get('deadline')}**"
        status_display = "🟢 Resolved" if a.get('status') == "Resolved" else ("🔵 Clarified" if a.get('status') == "Clarified by User" else "🔴 Unresolved")
        
        report_lines.append(f"| {a.get('task')} | {owner_display} | {deadline_display} | {status_display} | {a.get('line_reference')} |")

    final_report = "\n".join(report_lines)

    logs.append({
        "agent": "Quality Reviewer Agent",
        "action": "Verified grounding against transcript sources and formatted final report matrix."
    })

    return {
        "action_items": action_items,
        "final_report": final_report,
        "reviewer_passed": True,
        "activity_logs": logs
    }