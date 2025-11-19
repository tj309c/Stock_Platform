"""
Design System for Analysis Master
Provides consistent theming, styling, and UI components across all dashboards.
Includes ThemeManager for color schemes and MetricCardRenderer for standardized metric displays.
"""

import streamlit as st
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass
from enum import Enum


class ColorScheme(Enum):
    """Color schemes for different metric types and themes."""
    BULLISH = "#00FF00"  # Green
    BEARISH = "#FF4444"  # Red
    NEUTRAL = "#FFAA00"  # Orange/Yellow
    PRIMARY = "#1E88E5"  # Blue
    SECONDARY = "#7C4DFF"  # Purple
    SUCCESS = "#4CAF50"  # Green
    WARNING = "#FF9800"  # Orange
    DANGER = "#F44336"  # Red
    INFO = "#2196F3"  # Blue
    DARK = "#212121"  # Dark Gray
    LIGHT = "#FAFAFA"  # Light Gray


@dataclass
class Theme:
    """Theme configuration for the application."""
    name: str
    background_color: str
    text_color: str
    card_background: str
    border_color: str
    accent_color: str
    success_color: str
    warning_color: str
    danger_color: str


class ThemeManager:
    """
    Centralized theme management for consistent styling across dashboards.
    Provides color schemes, spacing, and typography standards.
    """

    # Define available themes
    THEMES = {
        "dark": Theme(
            name="Dark Mode",
            background_color="#0E1117",
            text_color="#FAFAFA",
            card_background="#1E1E1E",
            border_color="#333333",
            accent_color="#1E88E5",
            success_color="#4CAF50",
            warning_color="#FF9800",
            danger_color="#F44336",
        ),
        "light": Theme(
            name="Light Mode",
            background_color="#FFFFFF",
            text_color="#212121",
            card_background="#F5F5F5",
            border_color="#E0E0E0",
            accent_color="#1976D2",
            success_color="#388E3C",
            warning_color="#F57C00",
            danger_color="#D32F2F",
        ),
    }

    @staticmethod
    def get_theme(theme_name: str = "dark") -> Theme:
        """Get a theme by name."""
        return ThemeManager.THEMES.get(theme_name, ThemeManager.THEMES["dark"])

    @staticmethod
    def get_sentiment_color(value: float, threshold_positive: float = 0, threshold_negative: float = 0) -> str:
        """
        Get color based on sentiment value.

        Args:
            value: The numeric value to evaluate
            threshold_positive: Values above this are bullish/positive
            threshold_negative: Values below this are bearish/negative

        Returns:
            str: Hex color code
        """
        if value > threshold_positive:
            return ColorScheme.BULLISH.value
        elif value < threshold_negative:
            return ColorScheme.BEARISH.value
        else:
            return ColorScheme.NEUTRAL.value

    @staticmethod
    def get_change_color(value: float) -> str:
        """Get color for price/percentage changes."""
        return ThemeManager.get_sentiment_color(value)

    @staticmethod
    def apply_custom_css():
        """Apply custom CSS styling to the Streamlit app using a set of class names and CSS variables.

        This avoids most inline style attributes while still allowing a small number of dynamic
        theme-aware variables via CSS custom properties.
        """
        # get base theme to inject consistent color variables
        t = ThemeManager.get_theme()
        custom_css = f"""
        <style>
            :root {{
                --card-bg: {t.card_background};
                --card-border: {t.border_color};
                --text-color: {t.text_color};
                --muted-color: #999;
                --accent-color: {t.accent_color};
                --success: {t.success_color};
                --warning: {t.warning_color};
                --danger: {t.danger_color};
            }}

            /* Main content area */
            .main {{ padding: 2rem; }}

            /* Metric cards and KPI */
            .metric-card {{
                background-color: var(--card-bg);
                border-radius: 10px;
                padding: 1.5rem;
                margin: 0.5rem 0;
                border: 1px solid var(--card-border);
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .kpi-card {{ background: var(--kpi-card-bg, var(--card-bg)); }}
            .metric-card-content {{ display:flex; align-items:center; gap: 1rem; }}
            .metric-content-body {{ flex: 1; }}
            .metric-card-row {{ display:flex; align-items:center; gap:1rem; }}

            .kpi-title {{ font-size: 0.875rem; color: var(--muted-color); text-transform: uppercase; letter-spacing: 0.05em; }}
            .kpi-value {{ font-size: 2rem; font-weight: 600; color: var(--text-color); margin-top: 0.25rem; }}
            .kpi-subtitle {{ font-size: 0.9rem; color: var(--muted-color); margin-top: 0.25rem; }}
            .kpi-icon {{ font-size: 2rem; margin-right: 0.5rem; }}

            /* Change styling */
            .metric-row {{ margin-top: 0.5rem; font-size: 0.9rem; }}
            .change-value {{ font-weight: 600; }}
            .change-neg {{ color: {ColorScheme.BEARISH.value}; }}
            .change-pos {{ color: {ColorScheme.BULLISH.value}; }}
            .change-neutral {{ color: {ColorScheme.NEUTRAL.value}; }}
            .metric-note {{ color: var(--muted-color); margin-left: 0.5rem; }}

            /* Tables and containers */
            .table-container {{ overflow-x: auto; max-width: 100%; }}
            .table-container.scrollable-y {{ max-height: 400px; overflow-y: auto; }}

            /* Alerts */
            .alert-box {{ border-radius: 4px; padding: 1rem; margin: 1rem 0; }}
            .alert-info {{ background: {ColorScheme.INFO.value}22; border-left: 4px solid {ColorScheme.INFO.value}; }}
            .alert-success {{ background: {ColorScheme.SUCCESS.value}22; border-left: 4px solid {ColorScheme.SUCCESS.value}; }}
            .alert-warning {{ background: {ColorScheme.WARNING.value}22; border-left: 4px solid {ColorScheme.WARNING.value}; }}
            .alert-danger {{ background: {ColorScheme.DANGER.value}22; border-left: 4px solid {ColorScheme.DANGER.value}; }}
            .alert-title {{ font-weight: 600; margin-bottom: 0.5rem; font-size: 1rem; }}
            .alert-message {{ color: #ddd; }}

            /* Score card */
            .score-card .score-value {{ font-size: 2.5rem; font-weight: 700; color: var(--score-color, var(--accent-color)); }}
            .score-bar {{ background: #333; border-radius: 10px; height: 12px; overflow: hidden; }}
            .score-bar-inner {{ height: 100%; transition: width 0.3s ease; background: var(--score-color, var(--accent-color)); width: var(--score-percent, 0%); }}
            .score-label {{ margin-top: 0.5rem; font-size: 0.875rem; font-weight: 600; color: var(--score-color, var(--accent-color)); }}

            /* Help tooltip */
            .help-tooltip {{ cursor: help; font-size: 0.9rem; }}

            /* Buttons and headers */
            h1, h2, h3 {{ font-weight: 600; margin-bottom: 1rem; }}
            .stButton>button {{ border-radius: 8px; font-weight: 500; transition: all 0.3s ease; }}
            .stButton>button:hover {{ transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.2); }}

            /* Tabs */
            .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
            .stTabs [data-baseweb="tab"] {{ border-radius: 8px 8px 0 0; padding: 0.75rem 1.5rem; }}

            /* Remove extra padding */
            .block-container {{ padding-top: 1rem; }}

            /* Plotly charts */
            .js-plotly-plot {{ border-radius: 8px; }}
        </style>
        """
        st.markdown(custom_css, unsafe_allow_html=True)


class MetricCardRenderer:
    """
    Standardized metric card renderer for consistent metric display across dashboards.
    Provides various card layouts and styles for displaying KPIs and metrics.
    """

    @staticmethod
    def render_metric(
        label: str,
        value: Union[str, float, int],
        delta: Optional[Union[str, float]] = None,
        delta_color: Optional[str] = None,
        help_text: Optional[str] = None,
        prefix: str = "",
        suffix: str = "",
    ):
        """
        Render a single metric using Streamlit's native metric component.

        Args:
            label: Metric label/title
            value: The main metric value
            delta: Optional change value or percentage
            delta_color: Optional color override for delta (auto-detects if None)
            help_text: Optional tooltip help text
            prefix: Optional prefix (e.g., '$', '₿')
            suffix: Optional suffix (e.g., '%', 'M')
        """
        # Format the value
        formatted_value = f"{prefix}{value}{suffix}"

        # Use Streamlit's metric component
        st.metric(
            label=label,
            value=formatted_value,
            delta=delta,
            help=help_text,
        )

    @staticmethod
    def render_metric_row(metrics: List[Dict[str, Any]], columns: Optional[int] = None):
        """
        Render multiple metrics in a single row.

        Args:
            metrics: List of metric dictionaries with keys: label, value, delta, etc.
            columns: Number of columns (defaults to number of metrics)
        """
        if not metrics:
            return

        num_cols = columns or len(metrics)
        cols = st.columns(num_cols)

        for idx, metric in enumerate(metrics):
            with cols[idx % num_cols]:
                MetricCardRenderer.render_metric(**metric)

    @staticmethod
    def render_kpi_card(
        title: str,
        value: Union[str, float, int],
        subtitle: Optional[str] = None,
        change: Optional[float] = None,
        change_label: str = "vs. previous",
        icon: Optional[str] = None,
        color: Optional[str] = None,
    ):
        """
        Render a large KPI card with enhanced styling.

        Args:
            title: KPI title
            value: Main KPI value
            subtitle: Optional subtitle/description
            change: Optional percentage change
            change_label: Label for the change metric
            icon: Optional emoji icon
            color: Optional background color
        """
        # Determine change color
        change_color = ThemeManager.get_change_color(change) if change is not None else ColorScheme.NEUTRAL.value

        # Build the HTML
        icon_html = f'<span class="kpi-icon">{icon}</span>' if icon else ''
        subtitle_html = f'<div class="kpi-subtitle">{subtitle}</div>' if subtitle else ''
        change_html = ''
        if change is not None:
            change_sign = "+" if change > 0 else ""
            change_class = 'change-pos' if change > 0 else 'change-neg' if change < 0 else 'change-neutral'
            change_html = f'''
            <div class="metric-row">
                <span class="change-value {change_class}">{change_sign}{change:.2f}%</span>
                <span class="metric-note">{change_label}</span>
            </div>
            '''

        # allow color override via CSS variable (if `color` is provided)
        card_style = f' style="--kpi-card-bg: {color};"' if color else ''
        card_html = f'''
        <div class="metric-card kpi-card"{card_style}>
            <div class="metric-card-content">
                {icon_html}
                <div class="metric-content-body">
                    <div class="kpi-title">{title}</div>
                    <div class="kpi-value">{value}</div>
                    {subtitle_html}
                    {change_html}
                </div>
            </div>
        </div>
        '''

        st.markdown(card_html, unsafe_allow_html=True)

    @staticmethod
    def render_score_card(
        score: float,
        max_score: float = 100,
        title: str = "Score",
        description: Optional[str] = None,
        thresholds: Optional[Dict[str, float]] = None,
    ):
        """
        Render a visual score card with color-coded progress bar.

        Args:
            score: The score value
            max_score: Maximum possible score
            title: Score title
            description: Optional description
            thresholds: Optional dict with 'low', 'medium', 'high' threshold values
        """
        if thresholds is None:
            thresholds = {"low": 33, "medium": 66, "high": 100}

        # Determine color based on score
        percentage = (score / max_score) * 100
        if percentage >= thresholds.get("high", 66):
            color = ColorScheme.SUCCESS.value
            label = "Strong"
        elif percentage >= thresholds.get("medium", 33):
            color = ColorScheme.WARNING.value
            label = "Moderate"
        else:
            color = ColorScheme.DANGER.value
            label = "Weak"

        desc_html = f'<div class="kpi-subtitle">{description}</div>' if description else ''

        card_style = f' style="--score-color:{color}; --score-percent:{percentage}%;"'
        card_html = f'''
        <div class="metric-card score-card"{card_style}>
            <div class="kpi-title">{title}</div>
            <div class="metric-card-row">
                <div class="score-value">{score:.0f}</div>
                <div class="metric-content-body">
                    <div class="score-bar"><div class="score-bar-inner"></div></div>
                    <div class="score-label">{label} ({percentage:.1f}%)</div>
                </div>
            </div>
            {desc_html}
        </div>
        '''

        st.markdown(card_html, unsafe_allow_html=True)

    @staticmethod
    def render_alert_box(
        message: str,
        alert_type: str = "info",
        title: Optional[str] = None,
        icon: Optional[str] = None,
    ):
        """
        Render a styled alert/info box.

        Args:
            message: Alert message
            alert_type: Type of alert ('info', 'success', 'warning', 'danger')
            title: Optional title
            icon: Optional emoji icon
        """
        colors = {
            "info": ColorScheme.INFO.value,
            "success": ColorScheme.SUCCESS.value,
            "warning": ColorScheme.WARNING.value,
            "danger": ColorScheme.DANGER.value,
        }

        color = colors.get(alert_type, ColorScheme.INFO.value)
        title_html = f'<div class="alert-title">{icon or ""} {title}</div>' if title else ''

        alert_html = f'''
        <div class="alert-box alert-{alert_type}">
            {title_html}
            <div class="alert-message">{message}</div>
        </div>
        '''

        st.markdown(alert_html, unsafe_allow_html=True)

    @staticmethod
    def format_financial_value(num, display_units: str = "Millions") -> str:
        """Delegate to HelpWidget.format_financial_value for consistency across the UI.

        Kept on MetricCardRenderer for backward compatibility with existing code that
        references MetricCardRenderer.format_financial_value.
        """
        return HelpWidget.format_financial_value(num, display_units)


class HelpWidget:
    """
    Small, reusable help/tutorial widget used across dashboards.
    - render_help_tooltip: show a tiny info icon with hover text (no extra vertical space)
    - render_help_expander: show an expander titled with a small icon that reveals a short tutorial
    """
    @staticmethod
    def render_help_tooltip(short_text: str):
        # A small icon that displays via title attribute on hover. Keep it minimal.
        try:
            st.markdown(f'<span title="{short_text}" class="help-tooltip">ℹ️</span>', unsafe_allow_html=True)
        except Exception:
            # Fallback to simple text
            st.write("(i)" + short_text)

    @staticmethod
    def render_help_expander(title: str, content: str, expanded: bool = False):
        try:
            with st.expander(f"ℹ️ {title}", expanded=expanded):
                # allow markdown in the long form content
                st.markdown(content)
        except Exception:
            st.write(f"{title}: {content}")

    @staticmethod
    def format_financial_value(num, display_units: str = "Millions") -> str:
        """Format numbers for financial tables consistently across dashboards.

        Args:
            num: Numeric value to format
            display_units: 'Full', 'Thousands', 'Millions', or 'Billions'
        Returns:
            Formatted string (e.g., "$12,345" or "($1,234.56)")
        """
        try:
            if num is None:
                return ""
            import math
            if isinstance(num, float) and math.isnan(num):
                return ""
            val = float(num)
            is_negative = val < 0
            abs_val = abs(val)
            units = (display_units or "").lower()
            if units.startswith("bill"):
                scaled = abs_val / 1e9
                s = f"${scaled:,.2f}"
            elif units.startswith("mill"):
                scaled = abs_val / 1e6
                s = f"${scaled:,.2f}"
            elif units.startswith("thou"):
                scaled = abs_val / 1e3
                s = f"${scaled:,.0f}"
            else:
                if abs_val < 1000:
                    s = f"${abs_val:,.2f}"
                else:
                    s = f"${abs_val:,.0f}"
            if is_negative:
                return f"({s})"
            return s
        except Exception:
            return ""


# Convenience functions
def apply_theme():
    """Apply the default theme to the app."""
    ThemeManager.apply_custom_css()


def render_metric(*args, **kwargs):
    """Shortcut to render a metric."""
    return MetricCardRenderer.render_metric(*args, **kwargs)


def render_metric_row(*args, **kwargs):
    """Shortcut to render a metric row."""
    return MetricCardRenderer.render_metric_row(*args, **kwargs)
