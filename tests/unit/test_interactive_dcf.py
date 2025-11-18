import pytest
import sys


def test_interactive_dcf_import_and_display(monkeypatch):
    # Import the module and perform a basic instantiation and call.
    from src.analysis.interactive_dcf import InteractiveDCF

    # Monkeypatch Streamlit functions used by display to avoid running UI.
    class DummyStreamlit:
        def header(self, *args, **kwargs):
            return None
        def info(self, *args, **kwargs):
            return None
        def columns(self, *args, **kwargs):
            class Ctx:
                def __enter__(self):
                    return [self, self]
                def __exit__(self, *a):
                    return None
            return [Ctx(), Ctx()]
        def number_input(self, *args, **kwargs):
            return kwargs.get('value', 0)
        def markdown(self, *args, **kwargs):
            return None
        def write(self, *args, **kwargs):
            return None
        def metric(self, *args, **kwargs):
            return None

    monkeypatch.setitem(sys.modules, 'streamlit', DummyStreamlit())
    # Now import again to ensure our dummy Streamlit is used in the module
    import importlib
    import src.analysis.interactive_dcf as mod
    importlib.reload(mod)
    dcf = mod.InteractiveDCF()
    assert hasattr(dcf, 'display')
    # display should not raise when Streamlit methods are patched
    dcf.display()


def test_interactive_dcf_calculate():
    from src.analysis.interactive_dcf import InteractiveDCF
    # Simple deterministic test: small numbers for easy calculation
    per_share, projection = InteractiveDCF.calculate_fair_value(
        current_fcf=100.0,
        growth_rate=10.0,
        wacc=10.0,
        years=3,
        terminal_growth=2.0,
        shares_outstanding=10.0,
    )
    # Per-share returned should be numeric >0
    assert isinstance(per_share, float)
    assert per_share > 0
    # projection should include 4 items (3 years + terminal)
    assert len(projection) == 4
