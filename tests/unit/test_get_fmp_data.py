import pytest
from unittest.mock import patch, MagicMock
from src.pipelines.get_fmp_data import FMPDataPipeline
from src.core.config import AppConfig

@pytest.fixture
def fmp_pipeline():
    """Fixture for FMPDataPipeline."""
    # We patch AppConfig to ensure a fake API key is present during initialization
    with patch.object(AppConfig, '__init__', lambda self: setattr(self, 'fmp_api_key', 'test_api_key')):
        pipeline = FMPDataPipeline()
    return pipeline

def mock_requests_get(*args, **kwargs):
    """Helper to mock requests.get calls."""
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = 200

        def raise_for_status(self):
            if self.status_code != 200:
                raise Exception("HTTP Error")

        def json(self):
            return self.json_data

    if "profile/AAPL" in args[0]:
        return MockResponse([{"symbol": "AAPL", "companyName": "Apple Inc."}], 200)
    if "analyst-estimates/AAPL" in args[0]:
        return MockResponse([{"symbol": "AAPL", "consensusEPS": 5.0}], 200)
    if "earnings-surprises/AAPL" in args[0]:
        return MockResponse([{"actualEarningResult": 1.3, "estimatedEarning": 1.2}], 200)
    if "key-metrics/AAPL" in args[0]:
        return MockResponse([{"peRatio": 25.0}], 200)
    if "profile/ERROR" in args[0]:
        return MockResponse({"Error Message": "Invalid ticker."}, 200)

    return MockResponse(None, 404)

@patch('requests.get', side_effect=mock_requests_get)
def test_get_company_profile(mock_get, fmp_pipeline):
    """Test fetching a company profile."""
    profile = fmp_pipeline.get_company_profile("AAPL")
    assert profile is not None
    assert profile['symbol'] == "AAPL"
    assert profile['companyName'] == "Apple Inc."

@patch('requests.get', side_effect=mock_requests_get)
def test_get_analyst_consensus(mock_get, fmp_pipeline):
    """Test fetching analyst consensus."""
    consensus = fmp_pipeline.get_analyst_consensus("AAPL")
    assert consensus is not None
    assert consensus['symbol'] == "AAPL"
    assert consensus['consensusEPS'] == 5.0

@patch('requests.get', side_effect=mock_requests_get)
def test_get_earnings_surprises(mock_get, fmp_pipeline):
    """Test fetching earnings surprises."""
    surprises = fmp_pipeline.get_earnings_surprises("AAPL")
    assert surprises is not None
    assert len(surprises) == 1
    assert surprises[0]['actualEarningResult'] == 1.3

@patch('requests.get', side_effect=mock_requests_get)
def test_get_key_metrics(mock_get, fmp_pipeline):
    """Test fetching key metrics."""
    metrics = fmp_pipeline.get_key_metrics("AAPL")
    assert metrics is not None
    assert len(metrics) == 1
    assert metrics[0]['peRatio'] == 25.0

@patch('requests.get', side_effect=mock_requests_get)
def test_fmp_api_error(mock_get, fmp_pipeline):
    """Test handling of an API error message from FMP."""
    profile = fmp_pipeline.get_company_profile("ERROR")
    assert profile is None


@patch('requests.get')
def test_get_key_metrics_retry(mock_get, fmp_pipeline):
    """Test that key metrics uses retry on transient errors and succeeds on retry."""
    # First call raises a transient exception, second call returns valid data
    from requests.exceptions import Timeout
    def side_effect(*args, **kwargs):
        # Raise Timeout on first call, then return a good response
        if not hasattr(side_effect, 'count'):
            side_effect.count = 0
        if side_effect.count == 0:
            side_effect.count += 1
            raise Timeout('timeout')
        return mock_requests_get(*args, **kwargs)

    mock_get.side_effect = side_effect

    metrics = fmp_pipeline.get_key_metrics("AAPL")
    assert metrics is not None
    assert metrics[0]['peRatio'] == 25.0
