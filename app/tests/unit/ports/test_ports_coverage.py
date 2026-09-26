from app.src.ports.config_port import ConfigPort
from app.src.ports.secrets_port import SecretsPort


def test_ports_abstract():
    class DummySecrets(SecretsPort):
        def get_secret(self, name):
            super().get_secret(name)
            return {}

    class DummyConfig(ConfigPort):
        def get_scheduler_config(self):
            super().get_scheduler_config()
            return {}

        def get_reverse_scheduler_config(self):
            super().get_reverse_scheduler_config()
            return {}

        def get_parameter(self, name):
            super().get_parameter(name)
            return ""

    ds = DummySecrets()
    dc = DummyConfig()

    ds.get_secret("test")
    dc.get_scheduler_config()
    dc.get_reverse_scheduler_config()
    dc.get_parameter("test")

