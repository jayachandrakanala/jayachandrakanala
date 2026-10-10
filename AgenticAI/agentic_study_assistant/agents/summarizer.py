from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from agents.state import AgentState

def summarizer_agent(state: AgentState, llm) -> Dict[str, Any]:
    doc_text = state["document_text"]
    topic = state.get("user_topic", "General Topic")
    logs = state.get("activity_logs", [])
    
    prompt = ChatPromptTemplate.from_template("""
    You are an expert Educational Summarize Agent.
    Your task is to read the provided document text and create a comprehensive yet concise summary 
    focused ONLY on the topic: "{topic}".
    
    STRICT RULE: Use ONLY information present in the document. Do not add external information.
    
    Document Text:
    {document_text}
    
    Output a structured summary highlighting core concepts, key terms, and main takeaways.
    """)
    
    chain = prompt | llm
    response = chain.invoke({"document_text": doc_text, "topic": topic})
    
    logs.append({
        "agent": "Summarize Agent",
        "action": "Generated structured summary based on uploaded document."
    })
    
    return {
        "summary": response.content,
        "activity_logs": logs
    }