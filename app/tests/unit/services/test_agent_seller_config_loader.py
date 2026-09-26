from unittest.mock import mock_open, patch
from app.src.services.agent_seller_config_loader import AgentSellerConfigLoader


def test_agent_seller_config_loader_empty_file():
    loader = AgentSellerConfigLoader()
    with patch("builtins.open", mock_open(read_data="")):
        assert loader.load() == []


def test_agent_seller_config_loader_exception():
    loader = AgentSellerConfigLoader()
    with patch("builtins.open", side_effect=OSError("File not found")):
        assert loader.load() == []
