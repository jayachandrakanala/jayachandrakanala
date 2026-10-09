import time
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

class DisplayResultStreamlit:
    def __init__(self, usecase, graph, user_message):
        self.usecase = usecase
        self.graph = graph
        self.user_message = user_message

    def display_result_on_ui(self):
        usecase = self.usecase
        graph = self.graph
        user_message = self.user_message

        # Render User Message
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(f"**{user_message}**")

        if usecase == "Basic Chatbot":
            start_time = time.time()

            with st.chat_message("assistant", avatar="🤖"):
                status_container = st.status("🧠 **Agent Processing...**", expanded=True)
                
                response_placeholder = st.empty()
                full_response = ""

                # Stream response from graph
                for event in graph.stream({'messages': ("user", user_message)}):
                    for value in event.values():
                        if "messages" in value:
                            msg = value["messages"]
                            content = msg.content if hasattr(msg, "content") else str(msg)
                            full_response = content
                            
                            # Real-time streaming output
                            response_placeholder.markdown(full_response)

                execution_time = round(time.time() - start_time, 2)
                status_container.update(label=f"✅ **Thought complete in {execution_time}s**", state="complete", expanded=False)

        elif usecase == "Chatbot With Web":
            start_time = time.time()

            # Dynamic Agent Execution Trace Box
            with st.status("🛸 **LangGraph Agent Pipeline Active**", expanded=True) as status:
                st.write("🔄 **State Initialized** ➔ Querying graph nodes...")
                initial_state = {"messages": [user_message]}
                res = graph.invoke(initial_state)

                tool_calls_count = 0
                for message in res.get('messages', []):
                    if isinstance(message, ToolMessage):
                        tool_calls_count += 1
                        st.write(f"🌐 **Web Search Executed** (Tool Call #{tool_calls_count})")
                        with st.expander("🔍 View Raw Search Context & Retrieval", expanded=False):
                            st.code(message.content, language="json")

                execution_time = round(time.time() - start_time, 2)
                status.update(
                    label=f"⚡ **Execution Complete ({execution_time}s • {tool_calls_count} Tool Call/s)**",
                    state="complete",
                    expanded=False
                )

            # Display final conversation results
            for message in res.get('messages', []):
                if isinstance(message, AIMessage) and message.content:
                    with st.chat_message("assistant", avatar="🧠"):
                        st.markdown(message.content)

                        # Extra Visual Delight: Quick action bar under response
                        col1, col2 = st.columns([1, 5])
                        with col1:
                            st.caption(f"⏱️ {execution_time}s")