import streamlit as st

def apply_custom_theme():
    st.markdown("""
    <style>
        /* Main Application Dark Theme */
        .stApp {
            background-color: #0b0914 !important;
            color: #ffffff !important;
        }
        
        /* Sidebar Explicit Styling Fix */
        section[data-testid="stSidebar"] {
            background-color: #120d1f !important;
            border-right: 1px solid #2d1b4e !important;
        }
        
        section[data-testid="stSidebar"] *, 
        section[data-testid="stSidebar"] label, 
        section[data-testid="stSidebar"] span, 
        section[data-testid="stSidebar"] div {
            color: #ffffff !important;
        }

        /* Sidebar Inputs & Select Boxes */
        section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
        section[data-testid="stSidebar"] input {
            background-color: #1a142b !important;
            color: #ffffff !important;
            border: 1px solid #3d2b63 !important;
            border-radius: 6px !important;
        }

        /* Header Styling */
        .main-title {
            color: #00f0ff !important;
            font-family: 'Inter', sans-serif;
            font-weight: 800;
            font-size: 2.2rem;
            margin-bottom: 0px;
            text-shadow: 0 0 12px rgba(0, 240, 255, 0.4);
        }
        
        .sub-title {
            color: #b0b5c0 !important;
            font-size: 1.0rem;
            margin-bottom: 20px;
        }

        /* Workspace Input Fields */
        .stTextArea textarea, div[data-testid="stForm"] input {
            background-color: #181224 !important;
            color: #ffffff !important;
            border: 1px solid #3d2b63 !important;
            border-radius: 8px !important;
            font-size: 0.95rem !important;
        }

        .stTextArea textarea:focus, div[data-testid="stForm"] input:focus {
            border-color: #00f0ff !important;
            box-shadow: 0 0 8px rgba(0, 240, 255, 0.5) !important;
        }

        /* Reduce st.file_uploader height by ~50% */
        div[data-testid="stFileUploader"] {
            background-color: #181224 !important;
            border: 1px dashed #00f0ff !important;
            border-radius: 8px !important;
            padding: 2px 8px !important; /* Reduced vertical padding */
        }

        /* Compact internal drop-zone padding and layout */
        div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] {
            padding: 4px 8px !important; /* Shrinks internal box height */
            min-height: 45px !important;  /* Enforces a low profile height */
        }

        /* Make internal upload icon and instructions more compact */
        div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] span {
            font-size: 0.8rem !important;
            line-height: 1.1 !important;
        }

        div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] svg {
            height: 18px !important;
            width: 18px !important;
        }

        /* Compact upload button inside uploader */
        div[data-testid="stFileUploader"] button {
            background-color: #00f0ff !important;
            color: #0b0914 !important;
            font-weight: 700 !important;
            border-radius: 6px !important;
            padding: 2px 10px !important; /* Compact button dimensions */
            font-size: 0.8rem !important;
        }

        /* Primary Execution & Action Buttons */
        .stButton > button, div[data-testid="stForm"] button {
            background: linear-gradient(90deg, #7928ca 0%, #ff007f 100%) !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            border: none !important;
            padding: 10px 24px !important;
            border-radius: 8px !important;
            box-shadow: 0 4px 15px rgba(255, 0, 127, 0.4) !important;
        }

        .stButton > button *, div[data-testid="stForm"] button * {
            color: #ffffff !important;
        }

        /* Native Streamlit Tabs Styling */
        button[data-baseweb="tab"] {
            background-color: transparent !important;
            color: #a0a0b0 !important;
            font-weight: 600 !important;
            font-size: 1.0rem !important;
            border-bottom: 2px solid transparent !important;
            padding: 10px 18px !important;
        }

        button[aria-selected="true"] {
            color: #00f0ff !important;
            border-bottom: 2px solid #00f0ff !important;
        }

        /* Status Cards */
        .status-card {
            background-color: #151022 !important;
            padding: 14px !important;
            border-radius: 10px !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5) !important;
        }
    </style>
    """, unsafe_allow_html=True)