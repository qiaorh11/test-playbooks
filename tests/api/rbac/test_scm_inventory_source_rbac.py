import towerkit.exceptions as exc
import pytest

from tests.api import APITest


@pytest.mark.api
@pytest.mark.rbac
@pytest.mark.usefixtures('authtoken', 'install_enterprise_license_unlimited')
class TestSCMInventorySourceRBAC(APITest):

    @pytest.mark.parametrize('role', ['admin', 'read', 'use', 'update'])
    def test_scm_inventory_source_project_with_update_on_project_update(self, factories, role):
        user = factories.v2_user()

        inventory = factories.v2_inventory()
        assert inventory.set_object_roles(user, 'admin')

        project = factories.v2_project()
        assert project.set_object_roles(user, role)

        inv_source_args = dict(source='scm', source_path='inventories/inventory.ini', inventory=inventory,
                               project=project, update_on_project_update=True)

        with self.current_user(user):
            if role in ('read', 'update'):
                with pytest.raises(exc.Forbidden):
                    inv_source = factories.v2_inventory_source(**inv_source_args).wait_until_completed()
            else:
                inv_source = factories.v2_inventory_source(**inv_source_args).wait_until_completed()
                assert inv_source.wait_until_completed().is_successful

    @pytest.mark.parametrize('role', ['admin', 'read', 'use', 'update'])
    def test_scm_inventory_source_project_association(self, factories, role):
        user = factories.v2_user()

        inventory = factories.v2_inventory()
        assert inventory.set_object_roles(user, 'admin')

        project = factories.v2_project()
        assert project.set_object_roles(user, role)

        inv_source = factories.v2_inventory_source(source='scm', source_path='inventories/inventory.ini',
                                                   inventory=inventory)
        inv_source.ds.project.set_object_roles(user, 'admin')

        with self.current_user(user):
            if role in ('read', 'update'):
                with pytest.raises(exc.Forbidden):
                    inv_source.source_project = project.id
            else:
                inv_source.source_project = project.id
