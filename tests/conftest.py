"""
Pytest configuration for FSS Hero Chatbot tests.

This file contains shared fixtures and configuration for all tests.
"""

import sys
from pathlib import Path
import pytest

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def project_root_path():
    """Return the project root directory path."""
    return project_root


@pytest.fixture(scope="session")
def config_dir():
    """Return the config directory path."""
    return project_root / "config"


@pytest.fixture(scope="session")
def data_dir():
    """Return the data directory path."""
    return project_root / "data"


@pytest.fixture(scope="session")
def test_data_dir():
    """Return the test data directory path."""
    return Path(__file__).parent / "data" / "test_data"


@pytest.fixture
def sample_query():
    """Return a sample query for testing."""
    return "What is stop loss?"


@pytest.fixture
def sample_config():
    """Return sample configuration for testing agent."""
    return {
        "configurable": {
            "thread_id": "test_session",
            "web_search_enabled": False,
            "force_web_search": False,
            "similarity_threshold": 0.7
        }
    }


# Test markers for different test categories
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "requires_api: mark test as requiring API keys"
    )
