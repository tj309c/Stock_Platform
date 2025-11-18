import pytest
from unittest.mock import patch
from src.pipelines.get_economic_data import EconomicDataPipeline
from src.core.config import AppConfig

@pytest.fixture
def economic_pipeline():
    """Fixture for EconomicDataPipeline."""
    # Patch the AppConfig instance attributes directly after __init__ is stubbed
    def fake_init(self):
        self.fred_api_key = 'test_fred_key'
        self.eia_api_key = 'test_eia_key'
    with patch.object(AppConfig, '__init__', fake_init):
        return EconomicDataPipeline()

def mock_requests_get(*args, **kwargs):
    """Helper to mock requests.get calls for economic data."""
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = 200
        def raise_for_status(self):
            if self.status_code != 200:
                raise Exception("HTTP Error")
        def json(self):
            return self.json_data

    if "api.stlouisfed.org" in args[0]:
        return MockResponse({'observations': [{'date': '2025-11-01', 'value': '100'}]}, 200)
    if "api.eia.gov" in args[0]:
        return MockResponse({'response': {'data': [{'period': '2025-11', 'value': 50}]}}, 200)

    return MockResponse(None, 404)

@patch('requests.get', side_effect=mock_requests_get)
def test_get_fred_series(mock_get, economic_pipeline):
    """Test fetching a FRED series."""
    result = economic_pipeline.get_fred_series('GDP')
    assert result is not None
    assert 'observations' in result
    assert result['observations'][0]['value'] == '100'

@patch('requests.get', side_effect=mock_requests_get)
def test_get_eia_series(mock_get, economic_pipeline):
    """Test fetching an EIA series."""
    result = economic_pipeline.get_eia_series('PET.WCRSTUS1.W')
    assert result is not None
    assert 'response' in result
    assert result['response']['data'][0]['value'] == 50
