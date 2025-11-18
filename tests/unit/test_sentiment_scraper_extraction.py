"""
Unit tests for the specific extraction patterns in SentimentScraper.

These tests validate that the scraper can correctly parse headlines, dates, and links
from sample HTML/XML content for each supported source.
"""

import pytest
from src.pipelines.get_sentiment_scraper import SentimentScraper
from unittest.mock import MagicMock

@pytest.fixture
def scraper():
    """Provides a SentimentScraper instance for testing."""
    return SentimentScraper()

def test_finviz_extraction_pattern(scraper, monkeypatch):
    """Test that the Finviz scraper correctly extracts headlines from a sample HTML table."""
    html_content = """
    <html><body>
    <table class="fullview-news-outer">
        <tr>
            <td width="130" align="right">Nov-17-23 09:00AM</td>
            <td align="left">
                <a href="https://example.com/news1" class="tab-link-news">This is the first headline.</a>
                <span style="color:#aa6dc0;font-size:9px"> (some-source)</span>
            </td>
        </tr>
        <tr>
            <td width="130" align="right">Nov-16-23 04:30PM</td>
            <td align="left">
                <a href="https://example.com/news2" class="tab-link-news">This is a second, older headline.</a>
            </td>
        </tr>
    </table>
    </body></html>
    """
    mock_response = MagicMock()
    mock_response.text = html_content

    # Patch the public method directly to isolate the test
    def mock_finviz_headlines(self, ticker): # noqa
        return scraper._parse_finviz_html(mock_response.text)

    monkeypatch.setattr(SentimentScraper, '_get_headlines_from_finviz', mock_finviz_headlines) # noqa

    # Call the parsing method directly (avoid the cached module-level wrapper which
    # creates a new SentimentScraper instance and would ignore instance-level monkeypatches).
    headlines = scraper.get_headlines_from_finviz('ANY_TICKER')
    assert len(headlines) == 2
    assert headlines[0]['title'] == "This is the first headline."
    assert headlines[0]['url'] == "https://example.com/news1"
    assert headlines[0]['source'] == "Finviz" # noqa

def test_yahoo_rss_extraction_pattern(scraper, monkeypatch):
    """Test that the Yahoo RSS scraper correctly parses a sample XML feed."""
    xml_content = """
    <rss version="2.0">
        <channel>
            <item>
                <title>First Yahoo Headline</title>
                <link>https://finance.yahoo.com/news/story1.html</link>
                <pubDate>Mon, 17 Nov 2025 12:00:00 GMT</pubDate>
            </item>
            <item>
                <title>Second Yahoo Headline</title>
                <link>https://finance.yahoo.com/news/story2.html</link>
                <pubDate>Mon, 17 Nov 2025 11:00:00 GMT</pubDate>
            </item>
        </channel>
    </rss>
    """
    mock_response = MagicMock()
    mock_response.text = xml_content

    # Patch the public method directly
    def mock_yahoo_headlines(self, ticker): # noqa
        return scraper._parse_yahoo_rss(mock_response.text)

    monkeypatch.setattr(SentimentScraper, '_get_headlines_from_yahoo', mock_yahoo_headlines) # noqa

    headlines = scraper._get_headlines_from_yahoo('ANY_TICKER')
    assert len(headlines) == 2
    assert headlines[0]['title'] == "First Yahoo Headline"
    assert headlines[0]['url'] == "https://finance.yahoo.com/news/story1.html"
    assert headlines[1]['title'] == "Second Yahoo Headline"