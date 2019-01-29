import pytest
import config42
from tests.fixtures.configs import sample_config, default_config


def test_configuration_content(sample_config):
    config_manager = config42.ConfigManager()
    config_manager.set_many(sample_config)
    assert_configuration_content(config_manager, sample_config)


def assert_configuration_content(config_manager, config):
    assert config['simple'] == config_manager.get('simple')
    assert config['bool'] == config_manager.get('bool')
    assert config['simple_dict']['key'] == config_manager.get('simple_dict.key')
    assert config['nested_dict']['nested']['key'] == config_manager.get('nested_dict.nested.key')
    assert config['nested_list'][0][0] == config_manager.get('nested_list.0.0')
    assert config['nested_list'][1][0] == config_manager.get('nested_list.1.0')
    assert config_manager.get('notindict') is None


def test_configuration_setting(sample_config):
    config_manager = config42.ConfigManager()
    for key, value in sample_config.items():
        config_manager.set(key, value)

    assert_configuration_content(config_manager, sample_config)


def test_configuration_setting_nested_keys(sample_config):
    config_manager = config42.ConfigManager()
    config_manager.set_many(sample_config)
    config_manager.set('key1', 'simple')
    config_manager.set('key2.key2', 'simple')
    config_manager.set('key3.key3.key3', 'simple')

    assert 'simple' == config_manager.get('key1')
    assert 'simple' == config_manager.get('key2.key2')
    assert 'simple' == config_manager.get('key3.key3.key3')


def test_configuration_setting_raise_exception(sample_config):
    config_manager = config42.ConfigManager()
    config_manager.set_many(sample_config)
    with pytest.raises(AttributeError):
        config_manager.set('nested_list.0.1', 'simple')


def test_configuration_content_index_error(sample_config):
    config_manager = config42.ConfigManager()
    config_manager.set_many(sample_config)
    assert config_manager.get('nested_list.0.4') is None


def test_configuration_content_absent_keys():
    config_manager = config42.ConfigManager()
    assert config_manager.get('absentkey1') is None
    assert config_manager.get('absentkey2.absentkey2') is None
    assert config_manager.get('absentkey3.absentkey3.absentkey3') is None


def test_configuration_default_values(default_config):
    config_manager = config42.ConfigManager(defaults=default_config)

    assert default_config['defaultkey1'] == config_manager.get('defaultkey1')
    assert default_config['defaultkey2']['defaultkey2'] == config_manager.get('defaultkey2.defaultkey2')
    assert config_manager.get('absentkey3.absentkey3.absentkey3') is None


def test_configuration_replace(default_config, sample_config):
    config_manager = config42.ConfigManager()

    config_manager.set_many(sample_config)
    assert sample_config['simple'] == config_manager.get('simple')
    config_manager.replace(default_config)
    assert config_manager.get('simple') is None
    assert default_config['defaultkey1'] == config_manager.get('defaultkey1')


def test_configuration_trigger_commit(sample_config):
    config_manager = config42.ConfigManager()

    config_manager.set_many(sample_config)
    config_manager.commit()
    assert sample_config['simple'] == config_manager.get('simple')

    config_manager.set('new_key', 'new_value')
    assert config_manager.handler._updated is False
    config_manager.set('new_key2', 'new_value2', trigger_commit=False)
    assert config_manager.handler._updated is True
    config_manager.commit()
    assert config_manager.handler._updated is False

    config_manager.set('new_key', 'new_value', trigger_commit=True)
    assert config_manager.handler._updated is False
