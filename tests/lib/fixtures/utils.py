import pytest


@pytest.fixture
def subrequest(request):
    # https://github.com/pytest-dev/pytest/issues/2495
    # To ensure that teardowns occur roughly in registered order
    # do not use the request fixture directly as all its finalizer calls
    # will occur in same block
    return request


@pytest.fixture(scope='class')
def class_subrequest(request):
    return request


@pytest.fixture(scope='class')
def is_docker(ansible_module_cls):
    try:
        manager = ansible_module_cls.inventory_manager
        groups_dict = manager.get_group_dict() if hasattr(manager, 'get_group_dict') else manager.get_groups_dict()
        tower_hosts = groups_dict.get('tower')
        return manager.get_host(tower_hosts[0]).get_vars().get('ansible_connection') == 'docker'
    except (TypeError, IndexError):
        return False
