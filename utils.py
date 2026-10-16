import streamlit as st

def render_sidebar():
    # Shared responsive styling: visual/layout-only changes; business logic is unchanged.
    st.markdown(
        """
        <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
        <style>
            [data-testid="stSidebarNav"] { display: none; }
            html, body, [data-testid="stAppViewContainer"] { max-width: 100%; overflow-x: hidden; }
            [data-testid="stMainBlockContainer"] {
                width: 100%; max-width: 1200px;
                padding-left: clamp(0.75rem, 3vw, 2.5rem);
                padding-right: clamp(0.75rem, 3vw, 2.5rem);
                padding-top: clamp(1rem, 3vw, 2rem);
            }
            h1, h2, h3 { overflow-wrap: anywhere; line-height: 1.25; }
            [data-testid="stHorizontalBlock"] { flex-wrap: wrap; gap: 1rem; }
            [data-testid="stVerticalBlock"] { min-width: 0; }
            [data-testid="stDataFrame"], [data-testid="stTable"] { max-width: 100%; overflow-x: auto; }
            iframe { max-width: 100% !important; }
            [data-testid="stImage"] img { max-width: 100%; height: auto; object-fit: contain; }
            input, textarea, select { font-size: 16px !important; }
            [data-testid="stFormSubmitButton"] button, [data-testid="stButton"] button {
                min-height: 44px; white-space: normal; overflow-wrap: anywhere;
            }
            [data-testid="stMetric"] { min-width: 0; padding: 0.65rem; }
            [data-testid="stSidebar"] { min-width: 0; }
            @media (max-width: 768px) {
                [data-testid="stMainBlockContainer"] {
                    padding: 1rem 0.8rem 2rem 0.8rem !important;
                }
                [data-testid="stHorizontalBlock"] {
                    flex-direction: column !important; align-items: stretch !important; gap: 0.65rem !important;
                }
                [data-testid="stHorizontalBlock"] > [data-testid="column"] {
                    width: 100% !important; min-width: 100% !important; flex: 1 1 100% !important;
                }
                h1 { font-size: 1.65rem !important; }
                h2 { font-size: 1.35rem !important; }
                h3 { font-size: 1.12rem !important; }
                [data-testid="stMetricValue"] { font-size: 1.35rem !important; }
                [data-testid="stFileUploader"] section { padding: 0.75rem !important; }
                [data-testid="stSidebar"] { width: min(85vw, 320px) !important; }
                iframe { width: 100% !important; }
                .stMarkdown, .stText, p, li { overflow-wrap: anywhere; }
            }
            @media (max-width: 420px) {
                [data-testid="stMainBlockContainer"] { padding-left: 0.6rem !important; padding-right: 0.6rem !important; }
                [data-testid="stMetric"] { padding: 0.45rem; }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    with st.sidebar:
        st.title("🏙️ Navigation")
        
        if not st.session_state.get("logged_in"):
            if st.button("🏠 Home / Login", use_container_width=True):
                st.switch_page("app.py")
        else:
            role = st.session_state.user_info.get("role")
            
            st.markdown(f"**Logged in as: {role}**")
            st.divider()
            
            if role == "User":
                if st.button("📝 Submit Complaint", use_container_width=True):
                    st.switch_page("pages/1_User_Portal.py")
                if st.button("📦 My Complaints", use_container_width=True):
                    st.switch_page("pages/5_My_Complaints.py")
                if st.button("⭐ Feedback", use_container_width=True):
                    st.switch_page("pages/4_Feedback.py")
                    
            elif role == "Sevak":
                if st.button("👨‍💼 Sevak Dashboard", use_container_width=True):
                    st.switch_page("pages/2_Nagar_Sevak.py")
                    
            elif role in ["Admin", "Officer"]:
                if st.button("📈 Admin Dashboard", use_container_width=True):
                    st.switch_page("pages/3_Admin_Dashboard.py")
            
            st.divider()
            if st.button("Log Out", use_container_width=True, type="primary"):
                st.session_state.logged_in = False
                st.session_state.user_info = None
                st.switch_page("app.py")
