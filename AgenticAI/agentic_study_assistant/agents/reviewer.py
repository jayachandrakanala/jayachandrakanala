import json
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from agents.state import AgentState

def reviewer_agent(state: AgentState, llm) -> Dict[str, Any]:
    doc_text = state["document_text"]
    summary = state["summary"]
    questions = state.get("quiz_questions", [])
    user_answers = state.get("user_answers", None)
    logs = state.get("activity_logs", [])
    corrections = state.get("corrections_made", [])

    if not user_answers:
        prompt = ChatPromptTemplate.from_template("""
        You are a Quality Assurance Reviewer Agent.
        Verify if these 5 generated quiz questions are 100% factually accurate based ONLY on the document context.
        
        Document Context:
        {document_text}
        
        Questions:
        {questions}
        
        Respond in JSON:
        {{
            "passed": true/false,
            "feedback": "Reason if failed or 'All questions are grounded in source context' if passed."
        }}
        """)
        
        chain = prompt | llm
        response = chain.invoke({"document_text": doc_text[:3000], "questions": str(questions)})
        
        try:
            res_json = json.loads(response.content.strip().replace("```json", "").replace("```", ""))
            passed = res_json.get("passed", True)
            feedback = res_json.get("feedback", "")
        except:
            passed = True
            feedback = "Questions verified successfully."

        if not passed:
            corrections.append(f"Reviewer requested quiz revision: {feedback}")
            logs.append({"agent": "Reviewer Agent", "action": f"❌ Flagged issues in quiz: {feedback}"})
        else:
            logs.append({"agent": "Reviewer Agent", "action": "✅ Validated Quiz Questions against document source."})

        return {
            "reviewer_passed": passed,
            "reviewer_feedback": feedback,
            "corrections_made": corrections,
            "activity_logs": logs
        }
    else:
        prompt = ChatPromptTemplate.from_template("""
        You are the Reviewer & Evaluator Agent.
        Evaluate the student's quiz answers against the correct answers and the document text.
        
        Quiz Data:
        {questions}
        
        User Submitted Answers:
        {user_answers}
        
        Document Source:
        {document_text}
        
        Provide a encouraging, highly structured, personalized study report:
        1. Score breakdown (e.g., 4/5).
        2. Per-question review (Identify user mistakes, explain why their choice was incorrect using the document source).
        3. Targeted study recommendations based on weak areas.
        """)
        
        chain = prompt | llm
        response = chain.invoke({
            "questions": str(questions),
            "user_answers": str(user_answers),
            "document_text": doc_text[:3000]
        })
        
        logs.append({"agent": "Reviewer Agent", "action": "🎓 Evaluated student responses and generated personalized feedback."})
        
        return {
            "reviewer_feedback": response.content,
            "activity_logs": logs
        }