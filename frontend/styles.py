"""
UPDATED Custom CSS Styling for Cricket Explorer
Improved readability, brighter colors, better contrast
"""

def get_custom_css():
    """Return custom CSS with improved visibility"""
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Roboto+Mono:wght@400;700&display=swap');
    
    /* Global Styles - LIGHTER BACKGROUND */
    .stApp {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        font-family: 'Inter', sans-serif;
        color: #0f172a;
    }
    
    /* Headers - BRIGHT AND CLEAR */
    h1, h2, h3, h4 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }
    
    h1 {
        font-size: 2.8rem !important;
        color: #0c4a6e !important;
        margin-bottom: 0.5rem !important;
    }
    
    h2 {
        font-size: 2rem !important;
        color: #0369a1 !important;
        border-left: 5px solid #0ea5e9;
        padding-left: 1rem;
        margin-top: 2rem !important;
    }
    
    h3 {
        font-size: 1.5rem !important;
        color: #0284c7 !important;
    }
    
    h4 {
        font-size: 1.2rem !important;
        color: #0369a1 !important;
        font-weight: 700 !important;
    }
    
    /* Text - HIGH CONTRAST */
    p, span, div, label {
        color: #1e293b !important;
    }
    
    /* Sidebar - BRIGHT */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border-right: 3px solid #cbd5e1;
    }
    
    [data-testid="stSidebar"] h1 {
        color: #0c4a6e !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stDateInput label,
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stTextInput label {
        color: #0f172a !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Buttons - BRIGHT AND CLEAR */
    .stButton > button {
        background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.75rem 1.75rem !important;
        font-weight: 700 !important;
        font-family: 'Inter', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(14, 165, 233, 0.4) !important;
        font-size: 0.95rem !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 25px rgba(14, 165, 233, 0.6) !important;
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
    }
    
    /* Primary action buttons */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4) !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 6px 25px rgba(16, 185, 129, 0.6) !important;
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
    }
    
    /* Secondary buttons */
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #64748b 0%, #475569 100%) !important;
        box-shadow: 0 4px 15px rgba(100, 116, 139, 0.3) !important;
    }
    
    /* DataFrames - BRIGHT TABLES */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
        background: #ffffff;
    }
    
    .stDataFrame table {
        background: #ffffff !important;
    }
    
    .stDataFrame th {
        background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        padding: 1rem !important;
    }
    
    .stDataFrame td {
        color: #1e293b !important;
        font-size: 0.9rem !important;
        padding: 0.75rem !important;
    }
    
    .stDataFrame tr:nth-child(even) {
        background: #f8fafc !important;
    }
    
    .stDataFrame tr:hover {
        background: #e0f2fe !important;
    }
    
    /* Metrics - BRIGHT CARDS */
    .stMetric {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 1.75rem;
        border-radius: 12px;
        border: 2px solid #cbd5e1;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
    
    .stMetric label {
        color: #475569 !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #0c4a6e !important;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        font-family: 'Roboto Mono', monospace !important;
    }
    
    /* Info/Success/Warning/Error boxes - BRIGHT */
    .stAlert {
        border-radius: 10px;
        border-left: 5px solid #0ea5e9;
        background: #f0f9ff;
        padding: 1.25rem;
        color: #0c4a6e !important;
        font-weight: 500;
    }
    
    .stSuccess {
        border-left-color: #10b981 !important;
        background: #ecfdf5 !important;
        color: #065f46 !important;
    }
    
    .stWarning {
        border-left-color: #f59e0b !important;
        background: #fffbeb !important;
        color: #92400e !important;
    }
    
    .stError {
        border-left-color: #ef4444 !important;
        background: #fef2f2 !important;
        color: #991b1b !important;
    }
    
    /* Tabs - BRIGHT AND CLEAR */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #ffffff;
        border-radius: 10px 10px 0 0;
        color: #64748b !important;
        font-weight: 700 !important;
        padding: 1rem 2rem;
        border: 2px solid #cbd5e1;
        border-bottom: none;
        font-size: 1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%) !important;
        color: #ffffff !important;
        border-color: #0284c7 !important;
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        background: #ffffff;
        padding: 2rem;
        border-radius: 0 12px 12px 12px;
        border: 2px solid #cbd5e1;
        border-top: none;
    }
    
    /* Expander - BRIGHT */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 10px;
        border: 2px solid #cbd5e1;
        color: #0f172a !important;
        font-weight: 700 !important;
        padding: 1rem !important;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #0ea5e9 !important;
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
    }
    
    /* Input fields - BRIGHT */
    .stTextInput input,
    .stSelectbox select,
    .stMultiSelect select,
    .stDateInput input {
        background-color: #ffffff !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 8px !important;
        color: #0f172a !important;
        font-weight: 500 !important;
        padding: 0.75rem !important;
    }
    
    .stTextInput input:focus,
    .stSelectbox select:focus,
    .stDateInput input:focus {
        border-color: #0ea5e9 !important;
        box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.2) !important;
    }
    
    /* Radio buttons */
    .stRadio > label {
        color: #0f172a !important;
        font-weight: 700 !important;
    }
    
    .stRadio > div {
        background: #ffffff;
        padding: 0.5rem;
        border-radius: 8px;
    }
    
    /* Scrollbar - BRIGHT */
    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 6px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #0ea5e9, #0284c7);
        border-radius: 6px;
        border: 2px solid #f1f5f9;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #0284c7, #0369a1);
    }
    
    /* Custom cricket-themed badges */
    .cricket-badge {
        display: inline-block;
        background: linear-gradient(135deg, #10b981, #059669);
        color: #ffffff;
        padding: 0.4rem 1rem;
        border-radius: 25px;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin: 0.25rem;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
    }
    
    .wicket-badge {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
    }
    
    /* Loading spinner - BRIGHT */
    .stSpinner > div {
        border-top-color: #0ea5e9 !important;
    }
    
    /* Divider - BRIGHT */
    hr {
        border: none;
        height: 3px;
        background: linear-gradient(90deg, transparent, #0ea5e9, transparent);
        margin: 2.5rem 0;
    }
    
    /* Match cards - BRIGHT */
    .match-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 15px;
        padding: 1.75rem;
        margin: 1rem 0;
        border: 2px solid #cbd5e1;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
    
    .match-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 35px rgba(14, 165, 233, 0.25);
        border-color: #0ea5e9;
    }
    
    /* Download buttons */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%) !important;
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4) !important;
    }
    
    .stDownloadButton > button:hover {
        box-shadow: 0 6px 25px rgba(139, 92, 246, 0.6) !important;
    }
    
    /* Improve text visibility everywhere */
    .element-container, .stMarkdown, .stText {
        color: #0f172a !important;
    }
    
    /* Ensure labels are visible */
    label {
        color: #0f172a !important;
        font-weight: 600 !important;
    }
    
    /* Caption text */
    .caption, small {
        color: #475569 !important;
        font-weight: 500 !important;
    }
    </style>
    """