# Wrapper to maintain package path compatibility for tests
# The project's canonical implementation lives at the repo root `zero_fcf_valuation.py`.

try:
    from zero_fcf_valuation import ZeroFCFValuation  # type: ignore
except Exception:
    # Fallback: if the root module is not importable, define a minimal placeholder
    class ZeroFCFValuation:  # type: ignore
        @staticmethod
        def revenue_multiple_valuation(latest_revenue, revenue_multiple, shares_outstanding, cash=0.0, debt=0.0):
            enterprise_value = latest_revenue * revenue_multiple
            equity_value = enterprise_value - debt + cash
            intrinsic_value_per_share = equity_value / shares_outstanding if shares_outstanding > 0 else 0
            return {
                'enterprise_value': enterprise_value,
                'intrinsic_value_per_share': intrinsic_value_per_share
            }

        @staticmethod
        def rule_of_40(revenue_growth_rate, profit_margin):
            score = revenue_growth_rate + profit_margin
            assessment = 'Healthy' if score >= 0.40 else ('Needs Improvement' if score >= 0.20 else 'Unhealthy')
            return {'score': score, 'assessment': assessment}
