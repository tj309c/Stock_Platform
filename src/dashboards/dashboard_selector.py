import streamlit as st
try:
    from streamlit_option_menu import option_menu
    HAS_OPTION_MENU = True
except ImportError:
    HAS_OPTION_MENU = False

from src.core.wsb_quotes import WSBQuotes, QuoteCategory
from src.core.design_system import MetricCardRenderer

# Import dashboard modules here as they are created
from src.dashboards.dashboard_equity import EquityDashboard
from src.dashboards.dashboard_crypto import CryptoDashboard
from src.dashboards.dashboard_options import OptionsDashboard
from src.dashboards.dashboard_predictive import PredictiveDashboard
from src.dashboards.dashboard_portfolio import PortfolioDashboard
from src.dashboards.dashboard_settings import SettingsDashboard
from src.dashboards.dashboard_debug import DebugDashboard

class PlaceholderDashboard:
    """A simple placeholder for dashboards that are not yet implemented."""
    def __init__(self, name, category: QuoteCategory = QuoteCategory.GENERAL):
        self.name = name
        self.category = category

    def display(self):
        st.header(f"🚧 {self.name} Dashboard")

        # Display a fun quote based on dashboard type
        quote = WSBQuotes.get_random_quote(self.category)
        MetricCardRenderer.render_alert_box(
            message=quote,
            alert_type="info",
            title="Words of Wisdom",
            icon="💭"
        )

        st.warning(f"The {self.name} dashboard is under construction.")
        st.info("This dashboard will include professional-grade analysis tools combined with WSB energy. Stay tuned!")

class DashboardSelector:
    """Handles the navigation and selection of different dashboards."""
    def __init__(self):
        self.dashboards = {
            "Equity": EquityDashboard(),  # Now using real dashboard!
            "Options": OptionsDashboard(),  # Now using real dashboard!
            "Crypto": CryptoDashboard(),  # Now using real dashboard!
            "Predictive": PredictiveDashboard(),
            "Portfolio": PortfolioDashboard(),
            "Screener": PlaceholderDashboard("Market Screener", QuoteCategory.GENERAL),
            "Backtester": PlaceholderDashboard("Signal Backtester", QuoteCategory.GENERAL),
            "Settings": SettingsDashboard(),
            "Debug": DebugDashboard(),
        }
        self.icons = {
            "Equity": "graph-up-arrow",
            "Options": "calculator",
            "Crypto": "currency-bitcoin",
            "Predictive": "robot",
            "Portfolio": "briefcase",
            "Screener": "search",
            "Backtester": "hourglass-split",
            "Settings": "gear",
            "Debug": "wrench",
        }

    def display(self):
        """Renders the sidebar navigation menu and returns the selected dashboard object."""
        # Display greeting
        st.sidebar.markdown("---")

        if HAS_OPTION_MENU:
            # Use fancy option menu if available
            selected = option_menu(
                menu_title="Dashboards",
                options=list(self.dashboards.keys()),
                icons=[self.icons.get(d, "bar-chart-line") for d in self.dashboards.keys()],
                menu_icon="cast",
                default_index=0,
            )
        else:
            # Fallback to simple selectbox if option_menu unavailable
            st.sidebar.subheader("📊 Dashboards")
            dashboard_names = list(self.dashboards.keys())
            emojis = {
                "Equity": "📈",
                "Options": "🧮",
                "Crypto": "₿",
                "Predictive": "🤖",
                "Portfolio": "💼",
                "Screener": "🔍",
                "Backtester": "⏱️"
                ,
                "Settings": "⚙️"
            }
            # Add emojis to names
            display_names = [f"{emojis.get(name, '📊')} {name}" for name in dashboard_names]
            selected_display = st.sidebar.selectbox(
                "Select Dashboard",
                display_names,
                label_visibility="collapsed"
            )
            # Extract actual name from display name
            selected = selected_display.split(" ", 1)[1] if " " in selected_display else selected_display

        return self.dashboards[selected]