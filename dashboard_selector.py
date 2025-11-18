import streamlit as st
from streamlit_option_menu import option_menu

# Import the actual dashboard classes
from src.dashboards.dashboard_equity import EquityDashboard
from src.dashboards.dashboard_options import OptionsDashboard
from src.dashboards.dashboard_crypto import CryptoDashboard
from src.dashboards.dashboard_predictive import PredictiveDashboard
from src.dashboards.dashboard_portfolio import PortfolioDashboard

class PlaceholderDashboard:
    """A simple placeholder for dashboards that are not yet implemented."""
    def __init__(self, name):
        self.name = name
        self.icon = "tools"

    def display(self):
        st.header(f"🚧 {self.name}")
        st.warning(f"🚧 The {self.name} dashboard is under construction. 🚧")
        st.info("This is a placeholder and will be replaced with the actual dashboard content.")

class DashboardSelector:
    """Handles the navigation and selection of different dashboards."""
    def __init__(self):
        self.dashboards = {
            "Equity": EquityDashboard(),
            "Options": OptionsDashboard(),
            "Crypto": CryptoDashboard(),
            "Predictive": PredictiveDashboard(),
            "Portfolio": PortfolioDashboard(),
            "Screener": PlaceholderDashboard("Screener"),
            "Backtester": PlaceholderDashboard("Backtester"),
        }
        self.icons = {
            "Equity": "graph-up-arrow", "Options": "table", "Crypto": "currency-bitcoin",
            "Predictive": "robot", "Portfolio": "briefcase", "Screener": "search",
            "Backtester": "hourglass-split"
        }

    def display(self):
        """Renders the sidebar navigation menu and returns the selected dashboard object."""
        with st.sidebar:
            selected = option_menu(
                menu_title="Dashboards",
                options=list(self.dashboards.keys()),
                icons=[self.icons.get(d.name if hasattr(d, 'name') else d, "bar-chart-line") for d in self.dashboards.keys()],
                menu_icon="cast",
                default_index=0,
            )
        return self.dashboards[selected]