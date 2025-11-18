import streamlit as st
from src.core.config import AppConfig
from src.core.design_system import ThemeManager
from src.core.wsb_quotes import WSBQuotes
from src.dashboards.dashboard_selector import DashboardSelector

def main():
    """
    Main function to run the Streamlit application.
    """
    # --- Page Configuration ---
    st.set_page_config(
        page_title="Analysis Master",
        page_icon="🔥",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # --- Apply Custom Theme ---
    ThemeManager.apply_custom_css()

    # --- Load Configuration ---
    config = AppConfig()

    # --- Sidebar Header ---
    with st.sidebar:
        st.title("🔥 Analysis Master")
        st.caption("One Dashboard to Rule Them All.")

        # Display a random greeting
        greeting = WSBQuotes.get_greeting()
        st.info(greeting)

        # Initialize and display the dashboard selector
        dashboard_selector = DashboardSelector()
        selected_dashboard = dashboard_selector.display()

        # Footer
        st.sidebar.markdown("---")
        st.sidebar.caption("💎🙌 Built by apes, for apes.")
        st.sidebar.caption("v0.1.0 - Phase 0 Complete")

    # --- Main Content Area ---
    selected_dashboard.display()

if __name__ == "__main__":
    main()