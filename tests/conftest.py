# Copyright (c) 2020 Chris ter Beke.
# ThingiBrowser plugin is released under the terms of the LGPLv3 or higher.
from unittest.mock import MagicMock

import pytest


def mock_preferences_get_value(key: str) -> str:
    """
    Mock implementation of Preferences().getValue().
    :param key: The preference key to get the value for.
    :return: The value of the preference.
    """
    if key == "thingibrowser/test_setting":
        return "default"
    elif key == "thingibrowser/test_setting_stored":
        return "stored"


@pytest.fixture
def preferences():
    """
    Fake preferences that mocks Cura's Preferences.
    :return: A MagicMock compatible with Cura's Preferences class.
    """
    preferences = MagicMock()
    preferences.addPreference.return_value = None
    preferences.getValue.side_effect = mock_preferences_get_value
    return preferences


@pytest.fixture
def application(preferences):
    """
    Fake application that mocks Cura's CuraApplication.
    :param preferences: A Preferences mock.
    :return: A MagicMock compatible with Cura's CuraApplication class.
    """
    app = MagicMock()
    app.getPreferences.return_value = preferences
    app.getInstance.return_value = app
    return app
