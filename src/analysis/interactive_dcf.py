"""Interactive DCF - Minimal placeholder implementation.

This module provides a lightweight InteractiveDCF class used by the Equity
dashboard. The full implementation is planned in Phase 2. For now, include
a minimal display() method so the dashboard can import and use this class
without failing during app startup or tests.
"""
from __future__ import annotations

import streamlit as st
from typing import List, Optional, Tuple
try:
    import plotly.express as px
except Exception:
    px = None
import pandas as pd


class InteractiveDCF:
    """A lightweight Interactive DCF placeholder with basic calculations
    and a simple preview chart. This is still a placeholder but provides
    meaningful values to test and preview valuation behavior.
    """

    def __init__(self):
        self.name = 'Interactive DCF'

    @staticmethod
    def calculate_fair_value(
        current_fcf: float,
        growth_rate: float,
        wacc: float,
        years: int = 5,
        terminal_growth: float = 2.0,
        shares_outstanding: float = 1_000_000_000,
    ) -> Tuple[float, List[dict]]:
        """Return (per_share_value, projection_list)

        - current_fcf: baseline free cash flow
        - growth_rate: annual growth (%) for projection years
        - wacc: discount rate (%) (e.g., 8 for 8%)
        - years: projection length in years
        - terminal_growth: perpetual growth rate after projection
        - shares_outstanding: number of shares to compute per-share value
        """
        # Basic safety/validation
        if shares_outstanding <= 0:
            shares_outstanding = 1

        # Convert percents to decimals
        gr = growth_rate / 100.0
        r = wacc / 100.0
        tg = terminal_growth / 100.0

        # Project FCF forward
        projection = []
        fcf = float(current_fcf)
        for y in range(1, years + 1):
            fcf = fcf * (1.0 + gr)
            projection.append({'year': y, 'fcf': fcf})

        # Discount projected FCFs
        pv_sum = 0.0
        for i, p in enumerate(projection, start=1):
            pv = p['fcf'] / ((1 + r) ** i)
            pv_sum += pv
            p['pv'] = pv

        # Terminal value using Gordon Growth (perpetuity)
        last_fcf = projection[-1]['fcf'] if projection else current_fcf
        terminal_value = 0.0
        if r > tg:
            terminal_value = (last_fcf * (1 + tg)) / (r - tg)
        # Discount terminal value back to present value
        terminal_pv = terminal_value / ((1 + r) ** years) if terminal_value else 0.0

        enterprise_value = pv_sum + terminal_pv

        # On a placeholder basis, treat the enterprise value as equity value
        equity_value = enterprise_value
        per_share = equity_value / float(shares_outstanding)

        # Compose return projection items with pv included
        proj = [{'year': p['year'], 'fcf': p['fcf'], 'pv': p['pv']} for p in projection]
        return per_share, proj + [{'year': 'terminal', 'fcf': terminal_value, 'pv': terminal_pv}]

    def display(self):
        """Render the interactive inputs and a preview plot of discounted cash flows."""
        try:
            st.header('🔮 Interactive DCF (Preview)')
            st.info('Preview: simple DCF projection and per-share fair value. This is a placeholder for Phase 2 full DCF.')
            col1, col2 = st.columns(2)
            with col1:
                current_fcf = st.number_input('Current Free Cash Flow (USD)', min_value=0.0, value=1_000_000_000.0, step=1_000_000.0)
                growth = st.number_input('Annual Growth (%, next N years)', min_value=-50.0, max_value=200.0, value=7.0, step=0.1)
                years = int(st.number_input('Projection Years', min_value=1, max_value=20, value=5))
            with col2:
                wacc = st.number_input('WACC (%, discount rate)', min_value=0.1, max_value=50.0, value=8.0, step=0.1)
                tg = st.number_input('Terminal Growth (%, perpetual)', min_value=-5.0, max_value=10.0, value=2.0, step=0.1)
                shares = st.number_input('Shares Outstanding', min_value=1.0, value=1_000_000_000.0, step=1_000_000.0)

            # Compute valuation
            per_share, projection = self.calculate_fair_value(float(current_fcf), float(growth), float(wacc), years=years, terminal_growth=float(tg), shares_outstanding=float(shares))

            st.markdown('### Valuation Summary')
            col1, col2 = st.columns(2)
            with col1:
                st.metric('Per-Share Fair Value (USD)', f'${per_share:,.2f}')
            with col2:
                st.metric('Projection Years', f'{years}')

            # Build plotly preview of FCF and PV
            try:
                df = pd.DataFrame(projection)
                # Keep only numeric year entries (skip 'terminal' for x axis) for FCF bars
                numeric_df = df[df['year'] != 'terminal']
                fig = px.bar(numeric_df, x='year', y='fcf', labels={'fcf': 'FCF (USD)', 'year': 'Year'}, title='Projected Free Cash Flows')
                fig.add_scatter(x=numeric_df['year'], y=numeric_df['pv'], mode='lines+markers', name='PV of FCF')
                st.plotly_chart(fig, use_container_width=True)
            except Exception:
                st.write('Unable to render preview chart')
        except Exception:
            # Ensure display never raises in test or import-only scenarios
            return None


__all__ = ['InteractiveDCF']
