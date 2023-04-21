from __future__ import annotations

import os
from unittest import mock

import pytest

from singer_sdk.helpers._compat import metadata
from singer_sdk.plugin_base import NoPackageFoundForPluginError, PluginBase
from singer_sdk.typing import IntegerType, PropertiesList, Property, StringType


class PluginTest(PluginBase):
    """Example Plugin for tests."""

    name = "plugin-test"
    config_jsonschema = PropertiesList(
        Property("prop1", StringType, required=True),
        Property("prop2", IntegerType),
    ).to_dict()


def test_get_env_var_config():
    """Test settings parsing from environment variables."""
    with mock.patch.dict(
        os.environ,
        {
            "PLUGIN_TEST_PROP1": "hello",
            "PLUGIN_TEST_PROP3": "not-a-tap-setting",
        },
    ):
        env_config = PluginTest._env_var_config
        assert env_config["prop1"] == "hello"
        assert "PROP1" not in env_config
        assert "prop2" not in env_config
        assert "PROP2" not in env_config
        assert "prop3" not in env_config
        assert "PROP3" not in env_config

    no_env_config = PluginTest._env_var_config
    assert "prop1" not in no_env_config
    assert "PROP1" not in env_config
    assert "prop2" not in no_env_config
    assert "PROP2" not in env_config
    assert "prop3" not in no_env_config
    assert "PROP3" not in env_config


class MockDistribution:
    @property
    def metadata(self):
        return {
            "Version": "0.0.1",
            "Requires-Python": ">=3.7",
        }


def test_plugin_package_distribution(monkeypatch):
    monkeypatch.setattr(metadata, "distribution", lambda _: MockDistribution())
    meta = PluginTest.distribution.metadata
    assert meta["Version"] == "0.0.1"
    assert meta["Requires-Python"] == ">=3.7"


def test_plugin_package_distribution_not_found():
    with pytest.raises(NoPackageFoundForPluginError):
        _ = PluginTest.distribution
