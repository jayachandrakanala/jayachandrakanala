import streamlit as st

THEMES = {
    "Cyberpunk": {
        "bg_color": "#0d0914",
        "card_bg": "#181224",
        "sidebar_bg": "#120a1d",
        "input_bg": "#1f172e",
        "primary": "#00f0ff",
        "secondary": "#ff007f",
        "text": "#e2d9f3",
        "border": "#2d1b4e"
    },
    "Dark Modern": {
        "bg_color": "#0e1117",
        "card_bg": "#161b22",
        "sidebar_bg": "#010409",
        "input_bg": "#21262d",
        "primary": "#58a6ff",
        "secondary": "#bc8cff",
        "text": "#c9d1d9",
        "border": "#30363d"
    },
    "Neon Matrix": {
        "bg_color": "#050d08",
        "card_bg": "#0b1a10",
        "sidebar_bg": "#030805",
        "input_bg": "#122b1b",
        "primary": "#00ff66",
        "secondary": "#00ccff",
        "text": "#d0ffd9",
        "border": "#13381e"
    }
}

def apply_custom_theme(theme_name="Cyberpunk"):
    theme = THEMES.get(theme_name, THEMES["Cyberpunk"])
    
    custom_css = f"""
    <style>
    /* Main App Background */
    .stApp {{
        background-color: {theme['bg_color']};
        color: {theme['text']};
    }}
    
    /* Sidebar Background */
    section[data-testid="stSidebar"] {{
        background-color: {theme['sidebar_bg']} !important;
        border-right: 1px solid {theme['border']};
    }}
    
    /* Input Fields Fix (Text Inputs & Password Boxes) */
    div[data-baseweb="input"] {{
        background-color: {theme['input_bg']} !important;
        border: 1px solid {theme['border']} !important;
        border-radius: 6px !important;
    }}
    
    div[data-baseweb="input"] input {{
        color: #ffffff !important;
        background-color: transparent !important;
    }}

    /* Input Labels */
    .stTextInput label, .stSelectbox label, .stTextArea label {{
        color: {theme['text']} !important;
        font-weight: 600;
    }}
    
    /* Main Titles */
    .main-title {{
        color: {theme['primary']};
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0px;
        text-shadow: 0 0 10px {theme['primary']}55;
    }}
    
    .sub-title {{
        color: {theme['secondary']};
        font-size: 1.0rem;
        font-weight: 500;
        margin-bottom: 25px;
    }}

    /* Execution Terminal Log */
    .log-box {{
        background-color: #05050a;
        border-left: 3px solid {theme['primary']};
        font-family: 'Courier New', Courier, monospace;
        padding: 10px 15px;
        font-size: 0.85rem;
        border-radius: 4px;
        margin-bottom: 8px;
        color: #a0a0b0;
    }}
    
    /* Action Buttons */
    .stButton>button {{
        background: linear-gradient(135deg, {theme['primary']} 0%, {theme['secondary']} 100%);
        color: #000000 !important;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        transition: all 0.3s ease;
    }}
    
    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 15px {theme['primary']}66;
    }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)