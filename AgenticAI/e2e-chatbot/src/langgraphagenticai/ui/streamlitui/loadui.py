import streamlit as st
import os

from src.langgraphagenticai.ui.uiconfigfile import Config

class LoadStreamlitUI:
    def __init__(self):
        self.config = Config()
        self.user_controls = {}

    def _apply_theme(self, theme_name: str):
        """Inject futuristic glassmorphism and glowing UI CSS styles."""
        if theme_name == "Cyberpunk":
            st.markdown(
                """
                <style>
                /* App Background with Subtle Mesh Gradient */
                .stApp {
                    background: linear-gradient(135deg, #0d0221 0%, #050014 50%, #15002a 100%);
                    color: #00f5d4;
                }
                /* Sidebar Styling */
                [data-testid="stSidebar"] {
                    background: rgba(36, 0, 70, 0.4);
                    backdrop-filter: blur(12px);
                    border-right: 1px solid rgba(0, 245, 212, 0.2);
                }
                /* Glow Headers */
                h1, h2, h3 {
                    background: linear-gradient(90deg, #00f5d4, #7b2cbf, #f72585);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    font-weight: 800 !important;
                }
                /* Styled Buttons & Inputs */
                .stTextInput > div > div > input, .stSelectbox > div > div {
                    border-radius: 10px;
                    border: 1px solid rgba(0, 245, 212, 0.3);
                    background: rgba(20, 0, 40, 0.6);
                    color: #00f5d4;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
        elif theme_name == "Dark":
            st.markdown(
                """
                <style>
                .stApp {
                    background-color: #0e1117;
                    color: #e0e0e0;
                }
                [data-testid="stSidebar"] {
                    background-color: #161b22;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
        elif theme_name == "Light":
            st.markdown(
                """
                <style>
                .stApp {
                    background-color: #f8f9fa;
                    color: #212529;
                }
                [data-testid="stSidebar"] {
                    background-color: #ffffff;
                    border-right: 1px solid #e9ecef;
                }
                </style>
                """,
                unsafe_allow_html=True
            )

    def load_streamlit_ui(self):
        st.set_page_config(
            page_title="🤖 " + self.config.get_page_title(),
            page_icon="⚡",
            layout="wide"
        )

        with st.sidebar:
            st.markdown("### ⚙️ Control Center")

            # Theme selection
            theme_options = ["Cyberpunk", "Dark", "Light", "Default"]
            self.user_controls["selected_theme"] = st.selectbox("🎨 UI Theme", theme_options)

            # Apply CSS theme styling
            if self.user_controls["selected_theme"] != "Default":
                self._apply_theme(self.user_controls["selected_theme"])

            st.markdown("---")

            # Get options from config
            llm_options = self.config.get_llm_options()
            usecase_options = self.config.get_usecase_options()

            # LLM selection
            self.user_controls["selected_llm"] = st.selectbox("🧠 Select LLM", llm_options)

            if self.user_controls["selected_llm"] == 'Groq':
                model_options = self.config.get_groq_model_options()
                self.user_controls["selected_groq_model"] = st.selectbox("⚡ Model Engine", model_options)
                self.user_controls["GROQ_API_KEY"] = st.session_state["GROQ_API_KEY"] = st.text_input("🔑 Groq API Key", type="password")

                if not self.user_controls["GROQ_API_KEY"]:
                    st.warning("⚠️ Enter GROQ API Key to initiate agents.")

            # Usecase selection
            self.user_controls["selected_usecase"] = st.selectbox("🚀 Agentic Workflow", usecase_options)

            if self.user_controls["selected_usecase"] == "Chatbot With Web":
                os.environ["TAVILY_API_KEY"] = self.user_controls["TAVILY_API_KEY"] = st.session_state["TAVILY_API_KEY"] = st.text_input("🌐 Tavily Search API Key", type="password")

                if not self.user_controls["TAVILY_API_KEY"]:
                    st.warning("⚠️ Enter Tavily API Key for Web Search features.")

        # Main Header Banner
        st.markdown(f"### 🤖 {self.config.get_page_title()}")
        st.caption("⚡ Powered by LangGraph • Stateful Multi-Agent Architecture")
        st.markdown("---")

        return self.user_controls