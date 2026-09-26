from unittest.mock import patch

from app.src.services.factories.bwt_port_factory import BWTPortFactory


@patch("app.src.services.factories.bwt_port_factory.BWTAdapter")
def test_bwt_port_factory_creates_adapter_with_scope(mock_adapter_class):
    factory = BWTPortFactory()

    factory.create("SBM")

    mock_adapter_class.assert_called_once_with(scope="SBM")
