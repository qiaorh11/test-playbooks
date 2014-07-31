import os
import re
import pytest
import json
import logging
import common.tower.license
from inflect import engine
from common.yaml_file import load_file
from tests.api import Base_Api_Test
from common.exceptions import Duplicate_Exception, NoContent_Exception

# Initialize inflection engine
inflect = engine()

# Parameterize tests based on yaml configuration
def pytest_generate_tests(metafunc):

    # FIXME ... access the value of a fixture?
    # Wouldn't it be nice if one could use datafile() here?

    for fixture in metafunc.fixturenames:
        test_set = list()
        id_list = list()

        # HACK - to avoid fixture namespace collision, we prefix fixtures with
        # '_' in this module.  The following will identify such fixtures, and
        # find the appropriate YAML configuration.
        config_key = fixture
        if config_key.startswith('_'):
            config_key = config_key[1:]

        # plural - parametrize entire list
        # (e.g. if asked for organizations, give _all_ organizations)
        if config_key in metafunc.cls.config:
            test_set.append(metafunc.cls.config[config_key])
            id_list.append(fixture)

        # singular - parametrize every time on list
        # (e.g. if asked for organization, parametrize _each_ organization)
        elif inflect.plural_noun(config_key) in metafunc.cls.config:
            key = inflect.plural_noun(config_key)
            for (count, value) in enumerate(metafunc.cls.config[key]):
                test_set.append(value)
                if 'name' in value:
                    id_list.append(value['name'])
                elif 'username' in value:
                    id_list.append(value['username'])
                else:
                    id_list.append('item%d' % count)

        if test_set and id_list:
            metafunc.parametrize(fixture, test_set, ids=id_list)

@pytest.fixture(scope='class')
def install_integration_license(request, authtoken, ansible_runner, awx_config):
    '''If a suitable license is not already installed, install a new license'''
    logging.debug("calling fixture install_integration_license")
    if not (awx_config['license_info'].get('valid_key', False) and
            awx_config['license_info'].get('compliant', False) and
            awx_config['license_info'].get('available_instances', 0) >= 10001):

        logging.debug("backing up existing license")
        # Backup any aws license
        ansible_runner.shell('test -f /etc/awx/aws && mv /etc/awx/aws /etc/awx/.aws', creates='/etc/awx/.aws', removes='/etc/awx/aws')

        # Install/replace license
        logging.debug("installing license /etc/awx/license")
        fname = common.tower.license.generate_license_file(instance_count=10000, days=60)
        ansible_runner.copy(src=fname, dest='/etc/awx/license', owner='awx', group='awx', mode='0600')

@pytest.fixture(scope='class')
def update_sshd_config(request, ansible_runner):
    '''Update /etc/ssh/sshd_config to increase MaxSessions'''

    # Increase MaxSessions and MaxStartups
    ansible_runner.lineinfile(dest="/etc/ssh/sshd_config", regexp="^#?MaxSessions .*", line="MaxSessions 150")
    ansible_runner.lineinfile(dest="/etc/ssh/sshd_config", regexp="^#?MaxStartups .*", line="MaxStartups 150")
    # Enable PasswordAuth (disabled on AWS instances)
    ansible_runner.lineinfile(dest="/etc/ssh/sshd_config", regexp="^#?PasswordAuthentication .*", line="PasswordAuthentication yes")
    ansible_runner.lineinfile(dest="/etc/ssh/sshd_config", regexp="^#?ChallengeResponseAuthentication .*", line="ChallengeResponseAuthentication yes")
    # Permit root login
    ansible_runner.lineinfile(dest="/etc/ssh/sshd_config", regexp="^#?PermitRootLogin .*", line="PermitRootLogin yes")

    # Restart sshd
    # RPM-based distros call the service: sshd
    result = ansible_runner.service(name="sshd", state="restarted")
    # Ubuntu calls the service: ssh
    if 'failed' in result and result['failed']:
        ansible_runner.service(name="ssh", state="restarted")

@pytest.fixture(scope='class')
def set_rootpw(request, ansible_runner, testsetup):
    '''Set the rootpw to something we use in credentials'''
    assert 'ssh' in testsetup.credentials, "No SSH credentials defined"
    assert 'username' in testsetup.credentials['ssh'], "No SSH username defined in credentials"
    assert 'password' in testsetup.credentials['ssh'], "No SSH password defined in credentials"
    ansible_runner.shell("echo '{username}:{password}' | chpasswd".format(**testsetup.credentials['ssh']))

@pytest.mark.incremental
@pytest.mark.integration
@pytest.mark.skip_selenium
@pytest.mark.trylast
class Test_Quickstart_Scenario(Base_Api_Test):

    pytestmark = pytest.mark.usefixtures("authtoken", "install_integration_license", "update_sshd_config", "set_rootpw")

    # Load test configuration
    config = load_file(os.path.join(os.path.dirname(__file__), 'data.yaml'))

    @pytest.mark.destructive
    def test_organizations_post(self, api_organizations_pg, _organization):
        # Create a new organization
        payload = dict(name=_organization['name'],
                       description=_organization['description'])
        try:
            org = api_organizations_pg.post(payload)
        except Duplicate_Exception, e:
            pytest.xfail(str(e))

    @pytest.mark.nondestructive
    def test_organization_get(self, api_organizations_pg, _organizations):
        org_page = api_organizations_pg.get(or__name=[o['name'] for o in _organizations])
        assert len(_organizations) == len(org_page.results)

    @pytest.mark.destructive
    def test_users_post(self, api_users_pg, _user):
        payload = dict(username=_user['username'],
                       first_name=_user['first_name'],
                       last_name=_user['last_name'],
                       email=_user['email'],
                       is_superuser=_user['is_superuser'],
                       password=_user['password'],)

        try:
            api_users_pg.post(payload)
        except Duplicate_Exception, e:
            pytest.xfail(str(e))

    @pytest.mark.nondestructive
    def test_users_get(self, api_users_pg, _users):
        user_page = api_users_pg.get(username__in=','.join([o['username'] for o in _users]))
        assert len(_users) == len(user_page.results)

    @pytest.mark.destructive
    def test_organizations_add_users(self, api_users_pg, api_organizations_pg, _organization):
        # get org related users link
        matches = api_organizations_pg.get(name__exact=_organization['name']).results
        assert len(matches) == 1
        org_related_pg = matches[0].get_related('users')

        # Add each user to the org
        for username in _organization.get('users', []):
            user = api_users_pg.get(username__iexact=username).results.pop()

            # Add user to org
            payload = dict(id=user.id)
            with pytest.raises(NoContent_Exception):
                org_related_pg.post(payload)

    @pytest.mark.destructive
    def test_organizations_add_admins(self, api_users_pg, api_organizations_pg, _organization):
        # get org related users link
        matches = api_organizations_pg.get(name__exact=_organization['name']).results
        assert len(matches) == 1
        org_related_pg = matches[0].get_related('admins')

        # Add each user to the org
        for username in _organization.get('admins', []):
            user = api_users_pg.get(username__iexact=username).results.pop()

            # Add user to org
            payload = dict(id=user.id)
            with pytest.raises(NoContent_Exception):
                org_related_pg.post(payload)

    @pytest.mark.destructive
    def test_teams_post(self, api_teams_pg, api_organizations_pg, _team):
        # locate desired organization resource
        org_pg = api_organizations_pg.get(name__exact=_team['organization']).results[0]

        payload = dict(name=_team['name'],
                       description=_team['description'],
                       organization=org_pg.id)
        try:
            api_teams_pg.post(payload)
        except Duplicate_Exception, e:
            pytest.xfail(str(e))

    @pytest.mark.nondestructive
    def test_teams_get(self, api_teams_pg, _teams):
        teams = _teams
        team_page = api_teams_pg.get(name__in=','.join([o['name'] for o in teams]))
        assert len(teams) == len(team_page.results)

    @pytest.mark.destructive
    def test_teams_add_users(self, api_users_pg, api_teams_pg, _team):
        # locate desired team resource
        matches = api_teams_pg.get(name__iexact=_team['name']).results
        assert len(matches) == 1
        team_related_pg = matches[0].get_related('users')

        # Add specified users to the team
        for username in _team.get('users', []):
            user = api_users_pg.get(username__iexact=username).results.pop()

            # Add user to org
            payload = dict(id=user.id)
            with pytest.raises(NoContent_Exception):
                team_related_pg.post(payload)

    @pytest.mark.destructive
    def test_credentials_post(self, api_users_pg, api_teams_pg, api_credentials_pg, _credential):
        # build credential payload
        payload = dict(name=_credential['name'],
                       description=_credential['description'],
                       kind=_credential['kind'],
                       username=_credential.get('username', None),
                       password=_credential.get('password', None),
                       cloud=_credential.get('cloud', False),)

        # Add user id (optional)
        if _credential['user']:
            user_pg = api_users_pg.get(username__iexact=_credential['user']).results[0]
            payload['user'] = user_pg.id

        # Add team id (optional)
        if _credential['team']:
            team_pg = api_teams_pg.get(name__iexact=_credential['team']).results[0]
            payload['team'] = team_pg.id

        # Add machine/scm credential fields
        if _credential['kind'] in ('ssh', 'scm'):
            # Assert the required credentials available?
            fields = ['username', 'password', 'ssh_key_data', 'ssh_key_unlock', ]
            if _credential['kind'] in ('ssh'):
                fields += ['sudo_username', 'sudo_password', 'vault_password']
            # The value 'encrypted' is not included in 'fields' because it is
            # *not* a valid payload key
            assert self.has_credentials(_credential['kind'], fields=fields + ['encrypted'])

            # Merge with credentials.yaml
            payload.update(dict(
                ssh_key_data=_credential.get('ssh_key_data', ''),
                ssh_key_unlock=_credential.get('ssh_key_unlock', ''),
                sudo_username=_credential.get('sudo_username', ''),
                sudo_password=_credential.get('sudo_password', ''),
                vault_password=_credential.get('vault_password', ''),))

            # Apply any variable substitution
            for field in fields:
                payload[field] = payload[field].format(**self.credentials[_credential['kind']])

        # Merge with cloud credentials.yaml
        if _credential['cloud']:
            if _credential['kind'] == 'gce':
                fields = ['username', 'project', 'ssh_key_data']
            elif _credential['kind'] == 'azure':
                fields = ['username', 'ssh_key_data']
            else:
                fields = ['username', 'password']
            assert self.has_credentials('cloud', _credential['kind'], fields=fields)
            for field in fields:
                payload[field] = _credential[field].format(**self.credentials['cloud'][_credential['kind']])

        try:
            org = api_credentials_pg.post(payload)
        except Duplicate_Exception, e:
            pytest.xfail(str(e))

    @pytest.mark.nondestructive
    def test_credentials_get(self, api_credentials_pg, _credentials):
        credential_page = api_credentials_pg.get(or__name=[o['name'] for o in _credentials])
        assert len(_credentials) == len(credential_page.results)

    @pytest.mark.destructive
    def test_inventories_post(self, api_inventories_pg, api_organizations_pg, _inventory):
        # Find desired org
        matches = api_organizations_pg.get(name__exact=_inventory['organization']).results
        assert len(matches) == 1
        org = matches.pop()

        # Create a new inventory
        payload = dict(name=_inventory['name'],
                       description=_inventory.get('description', ''),
                       organization=org.id,
                       variables=json.dumps(_inventory.get('variables', None)))

        try:
            api_inventories_pg.post(payload)
        except Duplicate_Exception, e:
            pytest.xfail(str(e))

    @pytest.mark.nondestructive
    def test_inventories_get(self, api_inventories_pg, _inventories):
        # Get list of created inventories
        api_inventories_pg.get(or__name=[o['name'] for o in _inventories])

        # Validate number of inventories found
        assert len(_inventories) == len(api_inventories_pg.results)

    @pytest.mark.destructive
    def test_groups_post(self, api_groups_pg, api_inventories_pg, _group):
        # Find desired inventory
        inventory_id = api_inventories_pg.get(name__iexact=_group['inventory']).results[0].id

        # Create a new inventory
        payload = dict(name=_group['name'],
                       description=_group.get('description', ''),
                       inventory=inventory_id,
                       variables=json.dumps(_group.get('variables', None)))

        # different behavior depending on if we're creating child or parent
        if 'parent' in _group:
            parent_pg = api_groups_pg.get(name__exact=_group['parent']).results[0]
            new_group_pg = parent_pg.get_related('children')
        else:
            new_group_pg = api_groups_pg

        try:
            new_group_pg.post(payload)
        except Duplicate_Exception, e:
            pytest.xfail(str(e))

    @pytest.mark.nondestructive
    def test_groups_get(self, api_groups_pg, _groups):
        groups = _groups
        # Get list of created groups
        api_groups_pg.get(name__in=','.join([o['name'] for o in groups]))

        # Validate number of inventories found
        assert len(groups) == len(api_groups_pg.results)

    @pytest.mark.destructive
    def test_hosts_post(self, api_hosts_pg, api_inventories_pg, _host):
        host = _host
        # Find desired inventory
        inventory_id = api_inventories_pg.get(name__iexact=host['inventory']).results[0].id

        # Create a new host
        payload = dict(name=host['name'],
                       description=host.get('description', None),
                       inventory=inventory_id,
                       variables=json.dumps(host.get('variables', None)))

        try:
            api_hosts_pg.post(payload)
        except Duplicate_Exception, e:
            pytest.xfail(str(e))

    @pytest.mark.nondestructive
    def test_hosts_get(self, api_hosts_pg, _hosts):
        hosts = _hosts
        # Get list of available hosts
        api_hosts_pg.get(or__name=[o['name'] for o in hosts])

        # Validate number of inventories found
        assert len(hosts) == api_hosts_pg.count

    @pytest.mark.destructive
    def test_hosts_add_group(self, api_hosts_pg, api_groups_pg, _host):
        # Find desired host
        host_id = api_hosts_pg.get(name=_host['name']).results[0].id

        # Find desired groups
        groups = api_groups_pg.get(name__in=','.join([grp for grp in _host.get('groups', [])])).results

        if not groups:
            pytest.skip("Not all hosts are associated with a group")

        # Add host to associated groups
        payload = dict(id=host_id)
        for group in groups:
            groups_host_pg = group.get_related('hosts')
            with pytest.raises(NoContent_Exception):
                groups_host_pg.post(payload)

    @pytest.mark.destructive
    def test_inventory_sources_patch(self, api_groups_pg, api_credentials_pg, _inventory_source):
        # Find desired group
        group_pg = api_groups_pg.get(name__iexact=_inventory_source['group']).results[0]

        # Find desired credential
        credential_pg = api_credentials_pg.get(name__iexact=_inventory_source['credential']).results[0]

        # Get Page groups->related->inventory_source
        inventory_source_pg = group_pg.get_related('inventory_source')

        payload = dict(source=_inventory_source['source'],
                       source_regions=_inventory_source.get('source_regions', ''),
                       source_vars=_inventory_source.get('source_vars', ''),
                       source_tags=_inventory_source.get('source_tags', ''),
                       credential=credential_pg.id,
                       overwrite=_inventory_source.get('overwrite', False),
                       overwrite_vars=_inventory_source.get('overwrite_vars', False),
                       update_on_launch=_inventory_source.get('update_on_launch', False),
                       update_interval=_inventory_source.get('update_interval', 0),)
        inventory_source_pg.patch(**payload)

    @pytest.mark.destructive
    def test_inventory_sources_update(self, api_groups_pg, api_inventory_sources_pg, _inventory_source):
        # Find desired group
        group_id = api_groups_pg.get(name__iexact=_inventory_source['group']).results[0].id

        # Find inventory source
        inv_src = api_inventory_sources_pg.get(group=group_id).results[0]

        # Navigate to related -> update
        inv_update_pg = inv_src.get_related('update')

        # Ensure inventory_source is ready for update
        assert inv_update_pg.json['can_update']

        # Trigger inventory_source update
        inv_update_pg.post()

    @pytest.mark.nondestructive
    @pytest.mark.jira('AC-596', run=False)
    def test_inventory_sources_update_status(self, api_groups_pg, api_inventory_sources_pg, _inventory_source):
        # Find desired group
        group_id = api_groups_pg.get(name__iexact=_inventory_source['group']).results[0].id

        # Find desired inventory_source
        inv_src = api_inventory_sources_pg.get(group=group_id).results[0]

        # Navigate to related -> inventory_updates
        # last_update only appears *after* the update completes
        # inv_updates_pg = inv_src.get_related('last_update')
        # Warning, the following sssumes the first update is the most recent
        inv_updates_pg = inv_src.get_related('inventory_updates').results[0]

        # Wait for task to complete
        inv_updates_pg = inv_updates_pg.wait_until_completed()

        # Make sure there is no traceback in result_stdout or result_traceback
        assert inv_updates_pg.is_successful, \
            "Job unsuccessful (status:%s, failed:%s)\nJob result_stdout: %s\nJob result_traceback: %s\nJob explanation: %s" % \
            (inv_updates_pg.status, inv_updates_pg.failed, inv_updates_pg.result_stdout, inv_updates_pg.result_traceback, inv_updates_pg.job_explanation)

        # Display output, even for success
        print inv_updates_pg.result_stdout

    @pytest.mark.nondestructive
    def test_inventory_sources_get_children(self, api_groups_pg, _inventory_source, region_choices):
        '''
        Tests that an inventory_sync created expected sub-groups
        '''
        # Find desired group
        group = api_groups_pg.get(name__iexact=_inventory_source['group']).results[0]

        # Find sub-groups
        children_pg = group.get_related('children')

        # Assert sub-groups were synced
        assert children_pg.count > 0, "No sub-groups were created for inventory '%s'" % _inventory_source['name']

        # Ensure all only groups matching source_regions were imported
        if 'source_regions' in _inventory_source and _inventory_source['source_regions'] != '':
            expected_source_regions = re.split(r'[,\s]+', _inventory_source['source_regions'])
            for child in children_pg.results:
                # If the group is an official region (e.g. 'us-east-1' or
                # 'ORD'), make sure it's one we asked for
                if child.name in region_choices[_inventory_source['source']]:
                    assert child.name in expected_source_regions, \
                        "Imported region (%s) that wasn't in list of expected regions (%s)" % \
                        (child.name, expected_source_regions)
                else:
                    print "Ignoring group '%s', it appears to not be a cloud region" % child.name

    @pytest.mark.nondestructive
    def test_inventory_sources_get_hosts(self, api_groups_pg, api_hosts_pg, _inventory_source):
        '''
        Tests that an inventory_sync successfully imported hosts
        '''
        # Find desired group
        group = api_groups_pg.get(name__iexact=_inventory_source['group']).results[0]

        # Find hosts within the group
        group_hosts_pg = group.get_related('hosts')

        # Validate number of hosts found
        assert group_hosts_pg.count > 0, "No hosts were synced for group '%s'" % group.name

        # Assert all hosts are enabled ... this isn't a good test, having
        # disabled hosts isn't bad.  This may happen with systems are coming
        # online when the inventory import happens.
        # disabled_hosts = group_hosts_pg.get(enabled=False)
        # assert disabled_hosts.count == 0, "ERROR: detected disabled inventory_update groups\n%s" % group.get_related('inventory_source').get_related('last_update').result_stdout

    @pytest.mark.destructive
    def test_projects_post(self, api_projects_pg, api_organizations_pg, api_credentials_pg, awx_config, _project, ansible_runner):
        # Checkout repository on the target system
        if _project['scm_type'] in [None, 'manual'] \
           and 'scm_url' in _project:
            assert '_ansible_module' in _project, \
                "Must provide ansible module to use for scm_url: %s " % _project['scm_url']

            # Make sure the required package(s) are installed
            results = ansible_runner.shell("test -f /etc/system-release && yum -y install %s || true"
                                           % _project['_ansible_module'])
            results = ansible_runner.shell("grep -qi ubuntu /etc/os-release && apt-get install %s || true"
                                           % _project['_ansible_module'])

            # Clone the repo
            clone_func = getattr(ansible_runner, _project['_ansible_module'])
            results = clone_func(
                force='no',
                repo=_project['scm_url'],
                dest="%s/%s" % (awx_config['project_base_dir'], _project['local_path']))

        # Find desired object identifiers
        org_id = api_organizations_pg.get(name__exact=_project['organization']).results[0].id

        # Build payload
        payload = dict(name=_project['name'],
                       description=_project['description'],
                       organization=org_id,
                       scm_type=_project['scm_type'],)

        # Add scm_type specific values
        if _project['scm_type'] in [None, 'manual']:
            payload['local_path'] = _project['local_path']
        else:
            payload.update(dict(scm_url=_project['scm_url'],
                                scm_branch=_project.get('scm_branch', ''),
                                scm_clean=_project.get('scm_clean', False),
                                scm_delete_on_update=_project.get('scm_delete_on_update', False),
                                scm_update_on_launch=_project.get('scm_update_on_launch', False),))

        # Add credential (optional)
        if 'credential' in _project:
            credential_id = api_credentials_pg.get(name__iexact=_project['credential']).results[0].id
            payload['credential'] = credential_id

        # Create project
        try:
            api_projects_pg.post(payload)
        except Duplicate_Exception, e:
            pytest.xfail(str(e))

    @pytest.mark.nondestructive
    def test_projects_get(self, api_projects_pg, _projects):
        api_projects_pg.get(or__name=[o['name'] for o in _projects])
        assert len(_projects) == len(api_projects_pg.results)

    @pytest.mark.destructive
    def test_projects_update(self, api_projects_pg, api_organizations_pg, _project):
        # Find desired project
        matches = api_projects_pg.get(name__iexact=_project['name'], scm_type=_project['scm_type'])
        assert matches.count == 1
        project_pg = matches.results.pop()

        # Assert that related->update matches expected
        update_pg = project_pg.get_related('update')
        if _project['scm_type'] in [None, 'manual']:
            assert not update_pg.json['can_update'], "Manual projects should not be updateable"
            pytest.skip("Manual projects can not be updated")
        else:
            assert update_pg.json['can_update'], "SCM projects must be updateable"

            # Has an update already been triggered?
            if 'current_update' in project_pg.json['related']:
                pytest.xfail("Project update already queued")
            else:
                # Create password payload
                payload = dict()

                # Add required password fields (optional)
                assert self.has_credentials('scm')
                for field in update_pg.json.get('passwords_needed_to_update', []):
                    credential_field = field
                    if field == 'scm_password':
                        credential_field = 'password'
                    payload[field] = self.credentials['scm'][credential_field]

                # Initiate update
                update_pg.post(payload)

    @pytest.mark.nondestructive
    def test_projects_update_status(self, api_projects_pg, api_organizations_pg, _project):
        # Find desired project
        matches = api_projects_pg.get(name__iexact=_project['name'], scm_type=_project['scm_type'])
        assert matches.count == 1
        project_pg = matches.results.pop()

        # Assert that related->update matches expected
        update_pg = project_pg.get_related('update')
        if _project['scm_type'] in [None, 'manual']:
            assert not update_pg.json['can_update'], "Manual projects should not be updateable"
        else:
            assert update_pg.json['can_update'], "SCM projects must be updateable"

        # Further inspect project updates
        project_updates_pg = project_pg.get_related('project_updates')
        if _project['scm_type'] in [None, 'manual']:
            assert project_updates_pg.count == 0, "Manual projects do not support updates"
        else:
            assert project_updates_pg.count > 0, "SCM projects should update after creation, but no updates were found"

            latest_update_pg = project_updates_pg.results.pop()

            # Wait 8mins for job to complete
            latest_update_pg = latest_update_pg.wait_until_completed()

            # Make sure there is no traceback in result_stdout or result_traceback
            assert latest_update_pg.is_successful, \
                "Job unsuccessful (status:%s, failed:%s)\nJob result_stdout: %s\nJob result_traceback: %s\nJob explanation: %s" % \
                (latest_update_pg.status, latest_update_pg.failed, latest_update_pg.result_stdout, latest_update_pg.result_traceback, latest_update_pg.job_explanation)

            # Display output, even for success
            print latest_update_pg.result_stdout

    @pytest.mark.destructive
    def test_organizations_add_projects(self, api_organizations_pg, api_projects_pg, _organization):
        # locate desired project resource
        matches = api_organizations_pg.get(name__exact=_organization['name']).results
        assert len(matches) == 1
        project_related_pg = matches[0].get_related('projects')

        projects = _organization.get('projects', [])
        if not projects:
            pytest.skip("No projects associated with organization")

        # Add each team to the project
        for name in projects:
            project = api_projects_pg.get(name__iexact=name).results.pop()

            payload = dict(id=project.id)
            with pytest.raises(NoContent_Exception):
                project_related_pg.post(payload)

    @pytest.mark.jira('AC-641', run=True)
    @pytest.mark.destructive
    def test_job_templates_post(self, api_inventories_pg, api_credentials_pg, api_projects_pg, api_job_templates_pg, _job_template, ansible_facts, ansible_runner):
        # Find desired object identifiers
        inventory_id = api_inventories_pg.get(name__iexact=_job_template['inventory']).results[0].id
        project_id = api_projects_pg.get(name__iexact=_job_template['project']).results[0].id

        # This is slightly nuts ... please look away
        if 'inventory_hostname' not in ansible_facts:
            if ansible_facts['ansible_domain'] == 'ec2.internal':
                ec2_facts = ansible_runner.ec2_facts()
                ansible_facts['inventory_hostname'] = ec2_facts['ansible_facts']['ansible_ec2_public_hostname']
            else:
                ansible_facts['inventory_hostname'] = ansible_facts['ansible_fqdn'].replace('x86-64', 'x86_64')

        # Substitute any template parameters
        limit = _job_template.get('limit', '').format(**ansible_facts)

        # Create a new job_template
        payload = dict(name=_job_template['name'],
                       description=_job_template.get('description', None),
                       job_type=_job_template['job_type'],
                       playbook=_job_template['playbook'],
                       job_tags=_job_template.get('job_tags', ''),
                       limit=limit,
                       inventory=inventory_id,
                       project=project_id,
                       allow_callbacks=_job_template.get('allow_callbacks', False),
                       verbosity=_job_template.get('verbosity', 0),
                       forks=_job_template.get('forks', 0),
                       extra_vars=json.dumps(_job_template.get('extra_vars', None)),)

        # Add credential identifiers
        for cred in ('credential', 'cloud_credential'):
            if cred in _job_template:
                payload[cred] = api_credentials_pg.get(name__iexact=_job_template[cred]).results[0].id

        try:
            api_job_templates_pg.post(payload)
        except Duplicate_Exception, e:
            pytest.xfail(str(e))

    @pytest.mark.nondestructive
    def test_job_templates_get(self, api_job_templates_pg, _job_templates):
        api_job_templates_pg.get(or__name=[o['name'] for o in _job_templates])
        assert len(_job_templates) == len(api_job_templates_pg.results)

    @pytest.mark.destructive
    def test_jobs_launch(self, api_job_templates_pg, api_jobs_pg, _job_template):
        # If desired, skip launch
        if not _job_template.get('_launch', True):
            pytest.skip("Per-request, skipping launch: %s" % _job_template['name'])

        # Find desired object identifiers
        template_pg = api_job_templates_pg.get(name__iexact=_job_template['name']).results[0]

        # Create the job
        payload = dict(name=template_pg.name,  # Add Date?
                       job_template=template_pg.id,
                       inventory=template_pg.inventory,
                       project=template_pg.project,
                       playbook=template_pg.playbook,
                       credential=template_pg.credential,)
        job_pg = api_jobs_pg.post(payload)

        # Determine if job is able to start
        start_pg = job_pg.get_related('start')
        assert start_pg.json['can_start']

        # If the credential used requires a password, provide a password.
        # Note, the password here is bogus and would fail if used.  In the
        # current scenario, the test systems do not require sudo passwords, so
        # the bogus value provided isn't used by the playbooks/hosts.
        payload = dict()
        for pass_field in start_pg.json.get('passwords_needed_to_start', []):
            payload[pass_field] = 'thisWillFail'

        # Launch job
        start_pg.post(payload)

    @pytest.mark.nondestructive
    def test_jobs_launch_status(self, api_job_templates_pg, api_jobs_pg, _job_template):
        # If desired, skip launch
        if not _job_template.get('_launch', True):
            pytest.skip("Per-request, skipping launch: %s" % _job_template['name'])

        # Find desired object identifiers
        template_pg = api_job_templates_pg.get(name__iexact=_job_template['name']).results[0]

        # Find the most recently launched job for the desired job_template
        matches = api_jobs_pg.get(job_template=template_pg.id, order_by='-id')
        assert matches.results > 0, "No jobs matching job_template=%s found" % template_pg.id
        job_pg = matches.results[0]

        # Wait 20mins for job to start (aka, enter 'pending' state)
        job_pg = job_pg.wait_until_started(timeout=60 * 20)

        # With the job started, it shouldn't be start'able anymore
        start_pg = job_pg.get_related('start')
        assert not start_pg.json['can_start'], \
            "Job id:%s launched (status:%s), but can_start: %s\nJob result_stdout: %s\nJob result_traceback: %s\nJob explanation: %s" % \
            (job_pg.id, job_pg.status, start_pg.json['can_start'], job_pg.result_stdout, job_pg.result_traceback, job_pg.job_explanation)

        # Wait 20mins for job to complete
        # TODO: It might be nice to wait 15 mins from when the job started
        job_pg = job_pg.wait_until_completed(timeout=60 * 20)

        # xfail for known vault packaging failure
        if job_pg.failed and 'ERROR: ansible-vault requires a newer version of pycrypto than the one installed on your platform.' in job_pg.result_stdout:
            pytest.xfail("Vault tests are expected to fail when tested with an older pycrypto")

        # Make sure there is no traceback in result_stdout or result_traceback
        assert job_pg.is_successful, \
            "Job unsuccessful (status:%s, failed:%s)\nJob result_stdout: %s\nJob result_traceback: %s\nJob explanation: %s" % \
            (job_pg.status, job_pg.failed, job_pg.result_stdout, job_pg.result_traceback, job_pg.job_explanation)

        # Display output, even for success
        print job_pg.result_stdout
