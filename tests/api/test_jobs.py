import re
import types
import json
import logging
import pytest
import fauxfactory
import common.tower.inventory
from dateutil.parser import parse
from tests.api import Base_Api_Test


log = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def job_sleep(request, job_template_sleep):
    '''
    Launch the job_template_sleep and return a job resource.
    '''
    return job_template_sleep.launch()


@pytest.fixture(scope="function")
def job_with_status_pending(request, job_sleep):
    '''
    Wait for job_sleep to move from new to queued, and return the job.
    '''
    return job_sleep.wait_until_started()


@pytest.fixture(scope="function")
def job_with_status_running(request, job_sleep):
    '''
    Wait for job_sleep to move from queued to running, and return the job.
    '''
    return job_sleep.wait_until_status('running')


@pytest.fixture(scope="function")
def job_with_multi_ask_credential_and_password_in_payload(request, job_template_multi_ask, testsetup):
    '''
    Launch job_template_multi_ask with passwords in the payload.
    '''
    launch_pg = job_template_multi_ask.get_related("launch")

    # determine whether sudo or su was used
    credential = job_template_multi_ask.get_related('credential')

    # assert expected values in launch_pg.passwords_needed_to_start
    assert credential.expected_passwords_needed_to_start == launch_pg.passwords_needed_to_start

    # build launch payload
    payload = dict(ssh_password=testsetup.credentials['ssh']['password'],
                   ssh_key_unlock=testsetup.credentials['ssh']['encrypted']['ssh_key_unlock'],
                   vault_password=testsetup.credentials['ssh']['vault_password'],
                   become_password=testsetup.credentials['ssh']['become_password'])

    # launch job_template
    result = launch_pg.post(payload)

    # find and return specific job_pg
    jobs_pg = job_template_multi_ask.get_related('jobs', id=result.json['job'])
    assert jobs_pg.count == 1, "Unexpected number of jobs returned (%s != 1)" % jobs_pg.count
    return jobs_pg.results[0]


@pytest.fixture(scope="function", params=['project', 'inventory', 'credential'])
def job_with_deleted_related(request, job_with_status_completed):
    '''Creates and deletes an related attribute of a job'''
    related_pg = job_with_status_completed.get_related(request.param)
    related_pg.delete()
    return job_with_status_completed


@pytest.fixture()
def utf8_template(request, authtoken, api_job_templates_pg, project_ansible_playbooks_git, host_local, ssh_credential):
    payload = dict(name="playbook:utf-8.yml.yml, random:%s" % (fauxfactory.gen_utf8()),
                   description="utf-8.yml - %s" % (fauxfactory.gen_utf8()),
                   inventory=host_local.inventory,
                   job_type='run',
                   project=project_ansible_playbooks_git.id,
                   credential=ssh_credential.id,
                   playbook='utf-8.yml',)
    obj = api_job_templates_pg.post(payload)
    request.addfinalizer(obj.delete)
    return obj


@pytest.fixture(scope="function")
def project_with_scm_update_on_launch(request, project_ansible_playbooks_git):
        return project_ansible_playbooks_git.patch(scm_update_on_launch=True)


@pytest.fixture(scope="function")
def another_custom_group(request, authtoken, api_groups_pg, inventory, inventory_script):
    payload = dict(name="custom-group-%s" % fauxfactory.gen_alphanumeric(),
                   description="Custom Group %s" % fauxfactory.gen_utf8(),
                   inventory=inventory.id,
                   variables=json.dumps(dict(my_group_variable=True)))
    obj = api_groups_pg.post(payload)
    request.addfinalizer(obj.delete)

    # Set the inventory_source
    inv_source = obj.get_related('inventory_source')
    inv_source.patch(source='custom',
                     source_script=inventory_script.id)
    return obj


@pytest.fixture(scope="function")
def stop_mongodb(request, ansible_runner):
    '''Stops MongoDB'''

    log.debug("calling fixture stop_mongodb")

    # Attempt to stop MongoDB a first time
    ansible_runner.service(name="mongod", state="stopped")

    # Check MongoDB and stop it a second time if necessary
    contacted = ansible_runner.wait_for(port='27017', state='absent')
    result = contacted.values()[0]
    if 'failed' in result:
        log.warn("mongod did not stop, forcing shutdown")
        contacted = ansible_runner.command('mongod --shutdown --dbpath /var/lib/mongo')
        result = contacted.values()[0]
        assert 'failed' not in result, "Command failed - %s" % json.dumps(result, indent=2)


@pytest.mark.api
@pytest.mark.skip_selenium
@pytest.mark.destructive
class Test_Job(Base_Api_Test):

    pytestmark = pytest.mark.usefixtures('authtoken', 'backup_license', 'install_license_unlimited')

    def test_utf8(self, utf8_template):
        '''
        Verify that a playbook full of UTF-8 successfully works through Tower
        '''
        # launch job
        job_pg = utf8_template.launch_job()

        # wait for completion
        job_pg = job_pg.wait_until_completed(timeout=60 * 10)

        # assert successful completion of job
        assert job_pg.is_successful, "Job unsuccessful - %s " % job_pg

    def test_post_as_superuser(self, job_template, api_jobs_pg):
        '''
        Verify a superuser is able to create a job by POSTing to the /api/v1/jobs endpoint.
        '''

        # post a job
        job_pg = api_jobs_pg.post(job_template.json)

        # assert successful post
        assert job_pg.status == 'new'

    def test_post_as_non_superuser(self, non_superusers, user_password, api_jobs_pg, job_template):
        '''
        Verify a non-superuser is unable to create a job by POSTing to the /api/v1/jobs endpoint.
        '''

        for non_superuser in non_superusers:
            with self.current_user(non_superuser.username, user_password):
                with pytest.raises(common.exceptions.Forbidden_Exception):
                    api_jobs_pg.post(job_template.json)

    def test_relaunch_with_credential(self, job_with_status_completed):
        '''
        Verify relaunching a job with a valid credential no-ask credential.
        '''
        relaunch_pg = job_with_status_completed.get_related('relaunch')

        # assert values on relaunch resource
        assert not relaunch_pg.passwords_needed_to_start

        # relaunch the job and wait for completion
        job_pg = job_with_status_completed.relaunch().wait_until_completed()

        # assert success
        assert job_pg.is_successful, "Job unsuccessful - %s" % job_pg

    @pytest.mark.trello('https://trello.com/c/MjOiEWgS')
    def test_relaunch_with_deleted_related(self, job_with_deleted_related):
        '''
        Verify relaunching a job whose related information has been deleted.
        '''
        # get relaunch page
        relaunch_pg = job_with_deleted_related.get_related('relaunch')

        # assert values on relaunch resource
        assert not relaunch_pg.passwords_needed_to_start

        # attempt to relaunch the job, should raise exception
        with pytest.raises(common.exceptions.BadRequest_Exception):
            relaunch_pg.post()

    def test_relaunch_with_multi_ask_credential_and_passwords_in_payload(self, job_with_multi_ask_credential_and_password_in_payload, testsetup):  # NOQA
        '''
        Verify that relaunching a job with a credential that includes ASK passwords, behaves as expected when
        supplying the necessary passwords in the relaunch payload.
        '''
        # get relaunch page
        relaunch_pg = job_with_multi_ask_credential_and_password_in_payload.get_related('relaunch')

        # determine expected passwords
        credential = job_with_multi_ask_credential_and_password_in_payload.get_related('credential')

        # assert expected values in relaunch_pg.passwords_needed_to_start
        assert credential.expected_passwords_needed_to_start == relaunch_pg.passwords_needed_to_start

        # relaunch the job and wait for completion
        payload = dict(ssh_password=testsetup.credentials['ssh']['password'],
                       ssh_key_unlock=testsetup.credentials['ssh']['encrypted']['ssh_key_unlock'],
                       vault_password=testsetup.credentials['ssh']['vault_password'],
                       become_password=testsetup.credentials['ssh']['become_password'])
        job_pg = job_with_multi_ask_credential_and_password_in_payload.relaunch(payload).wait_until_completed()

        # assert success
        assert job_pg.is_successful, "Job unsuccessful - %s" % job_pg

    def test_relaunch_with_multi_ask_credential_and_without_passwords(self, job_with_multi_ask_credential_and_password_in_payload):  # NOQA
        '''
        Verify that relaunching a job with a multi-ask credential fails when not supplied with passwords.
        '''
        # get relaunch page
        relaunch_pg = job_with_multi_ask_credential_and_password_in_payload.get_related('relaunch')

        # determine expected passwords
        credential = job_with_multi_ask_credential_and_password_in_payload.get_related('credential')

        # assert expected values in relaunch_pg.passwords_needed_to_start
        assert credential.expected_passwords_needed_to_start == relaunch_pg.passwords_needed_to_start

        # relaunch the job
        exc_info = pytest.raises(common.exceptions.BadRequest_Exception, relaunch_pg.post, {})
        result = exc_info.value[1]

        # assert expected error responses
        assert 'passwords_needed_to_start' in result, \
            "Expecting 'passwords_needed_to_start' in API response when " \
            "relaunching a job, without provided credential " \
            "passwords. %s" % json.dumps(result)

        # assert expected values in response
        assert credential.expected_passwords_needed_to_start == result['passwords_needed_to_start']

    def test_relaunch_uses_extra_vars_from_job(self, job_with_extra_vars):
        '''
        Verify that when you relaunch a job containing extra_vars in the
        launch-time payload, the resulting extra_vars *and* the job_template
        extra_vars are used.
        '''
        relaunch_pg = job_with_extra_vars.get_related('relaunch')

        # assert values on relaunch resource
        assert not relaunch_pg.passwords_needed_to_start

        # relaunch the job and wait for completion
        relaunched_job_pg = job_with_extra_vars.relaunch().wait_until_completed()

        # assert success
        assert relaunched_job_pg.is_successful, "Job unsuccessful - %s" % relaunched_job_pg

        # coerce extra_vars into a dictionary
        try:
            job_extra_vars = json.loads(job_with_extra_vars.extra_vars)
        except ValueError:
            job_extra_vars = {}

        try:
            relaunch_extra_vars = json.loads(relaunched_job_pg.extra_vars)
        except ValueError:
            relaunch_extra_vars = {}

        # assert the extra_vars on the relaunched job, match the extra_vars
        # used in the original job
        assert set(relaunch_extra_vars) == set(job_extra_vars), \
            "The extra_vars on a relaunched job should match the extra_vars on the job being relaunched (%s != %s)" % \
            (relaunch_extra_vars, job_extra_vars)

    def test_cancel_pending_job(self, job_with_status_pending):
        '''
        Verify the job->cancel endpoint behaves as expected when canceling a
        pending/queued job
        '''
        cancel_pg = job_with_status_pending.get_related('cancel')
        assert cancel_pg.can_cancel, "Unable to cancel job (can_cancel:%s)" % cancel_pg.can_cancel

        # cancel job
        cancel_pg.post()

        # wait for job to cancel
        job_with_status_pending = job_with_status_pending.wait_until_status('canceled')

        assert job_with_status_pending.status == 'canceled', \
            "Unexpected job status after cancelling (expected 'canceled') - " \
            "%s" % job_with_status_pending

        # Make sure the ansible-playbook did not start

        # Inspect the job_events and assert that the playbook_on_start
        # event was never received.  If 'playbook_on_start' event appears, then
        # ansible-playbook started, and the job was not cancelled in the
        # 'pending' state.
        job_events = job_with_status_pending.get_related('job_events', event="playbook_on_start")
        assert job_events.count == 0, "The pending job was successfully " \
            "canceled, but a 'playbook_on_start' host_event was received. " \
            "It appears that the job was not cancelled while in pending."

    def test_cancel_running_job(self, job_with_status_running):
        '''
        Verify the job->cancel endpoint behaves as expected when canceling a
        running job
        '''
        cancel_pg = job_with_status_running.get_related('cancel')
        assert cancel_pg.can_cancel, "Unable to cancel job (can_cancel:%s)" % cancel_pg.can_cancel

        # cancel job
        cancel_pg.post()

        # wait for job to cancel
        job_with_status_running = job_with_status_running.wait_until_status('canceled')

        assert job_with_status_running.status == 'canceled', "Unexpected job" \
            "status after cancelling job (expected status:canceled) - %s" % \
            job_with_status_running

        # Make sure the ansible-playbook did not complete

        # First, inspect the job_events and assert that the playbook_on_stats
        # event was never received.  If 'playbook_on_stats' event appears, then
        # ansible-playbook completed, despite the job status being marked as
        # 'canceled'.
        job_events = job_with_status_running.get_related('job_events', event="playbook_on_stats")
        assert job_events.count == 0, "The job was successfully canceled, but a" \
            "'playbook_on_stats' host_event was received.  It appears that the " \
            "ansible-playbook didn't cancel as expected."

        # Second, be sure the standard "PLAY RECAP" is missing from standard
        # output
        assert "PLAY RECAP ************" not in job_with_status_running.result_stdout

    def test_cancel_completed_job(self, job_with_status_completed):
        '''
        Verify the job->cancel endpoint behaves as expected when canceling a
        completed job
        '''
        cancel_pg = job_with_status_completed.get_related('cancel')

        # assert not can_cancel
        assert not cancel_pg.can_cancel, \
            "Unexpectedly able to cancel a completed job (can_cancel:%s)" % \
            cancel_pg.can_cancel

        # assert Method_Not_Allowed when attempting to cancel
        with pytest.raises(common.exceptions.Method_Not_Allowed_Exception):
            cancel_pg.post()

    def test_launch_with_inventory_update(self, job_template, cloud_group, host_local):
        '''
        Tests that job launches with inventory updates work with all cloud providers.
        '''
        job_template.patch(inventory=cloud_group.inventory, limit=host_local.name)
        cloud_group.get_related('inventory_source').patch(update_on_launch=True)

        # Assert that the cloud_group has not updated
        assert cloud_group.get_related('inventory_source').last_updated is None

        # Launch job and check results
        job_pg = job_template.launch().wait_until_completed()
        assert job_pg.is_successful, "Job unsuccessful - %s" % job_pg

        # Assert that the inventory_update is marked as successful
        inv_source_pg = cloud_group.get_related('inventory_source')
        assert inv_source_pg.is_successful, "An inventory_update was launched, but the inventory_source is not successful - %s" % inv_source_pg

        # Assert that an inventory_update completed successfully
        inv_update_pg = inv_source_pg.get_related('last_update')
        assert inv_update_pg.is_successful, "An inventory_update was launched, but did not succeed - %s" % inv_update_pg

    def test_launch_with_scm_update(self, job_template, project_with_scm_update_on_launch):
        '''
        Tests that job launches with projects that have "Update on Launch" enabled work as expected.
        '''
        job_template.patch(project=project_with_scm_update_on_launch.id)

        # Remember last update
        initial_update_pg = project_with_scm_update_on_launch.get_related('last_update')

        # Launch job and check results
        job_pg = job_template.launch().wait_until_completed()
        assert job_pg.is_successful, "Job unsuccessful - %s" % job_pg

        # Assert a new scm update was launched
        updated_project_pg = project_with_scm_update_on_launch.get()
        final_update_pg = updated_project_pg.get_related('last_update')
        assert initial_update_pg.id != final_update_pg.id, "Update IDs are the same (%s = %s)" % (initial_update_pg.id, final_update_pg.id)

    @pytest.mark.fixture_args(source_script='''#!/usr/bin/env python
import json, time

time.sleep(10)
inventory = dict()

print json.dumps(inventory)
''')
    def test_cascade_cancel_with_inventory_update(self, job_template, custom_group, api_unified_jobs_pg):
        '''
        Tests that if you cancel an inventory update before it finishes that its dependent job
        fails.
        '''
        job_template.patch(inventory=custom_group.inventory)

        inventory_source_pg = custom_group.get_related('inventory_source')
        inventory_source_pg.patch(update_on_launch=True)

        # Assert that the cloud_group has not updated
        assert inventory_source_pg.last_updated is None, "inventory_source_pg unexpectedly updated."

        # Launch job
        job_pg = job_template.launch()

        # Wait for the inventory_source to start
        inventory_source_pg.wait_until_started()

        # Cancel inventory update
        update_pg = inventory_source_pg.get_related('current_update')
        cancel_pg = update_pg.get_related('cancel')
        assert cancel_pg.can_cancel, "The inventory_update is not cancellable, it may have already completed - %s" % update_pg.get()
        cancel_pg.post()

        # Assess job status
        job_pg = job_pg.wait_until_completed()
        assert not job_pg.is_successful, "Job run unexpectedly completed successfully - %s" % job_pg
        assert job_pg.job_explanation.startswith("Previous Task Failed: inventory_update"), \
            "Unexpected job_explanation: %s" % job_pg.job_explanation

        # Assert update_pg canceled
        update_pg.get()
        assert update_pg.status == 'canceled', "Unexpected job" \
            "status after cancelling (expected 'canceled') - %s" % \
            update_pg

        # Assert inventory source canceled
        inventory_source_pg.get()
        assert inventory_source_pg.status == 'canceled', "Unexpected " \
            "inventory_source status after cancelling (expected 'canceled') " \
            "- %s" % inventory_source_pg

    @pytest.mark.fixture_args(source_script='''#!/usr/bin/env python
import json, time

time.sleep(10)
inventory = dict()

print json.dumps(inventory)
''')
    def test_cascade_cancel_with_multiple_inventory_updates(self, job_template, custom_group, another_custom_group, api_unified_jobs_pg):
        '''
        Tests that if you cancel an inventory update before it finishes that its dependent jobs
        fail.
        '''
        job_template.patch(inventory=custom_group.inventory)

        inventory_source_pg = custom_group.get_related('inventory_source')
        inventory_source_pg.patch(update_on_launch=True)

        another_inventory_source_pg = another_custom_group.get_related('inventory_source')
        another_inventory_source_pg.patch(update_on_launch=True)

        # Assert that cloud_groups have not updated
        assert inventory_source_pg.last_updated is None, "inventory_source_pg unexpectedly updated."
        assert another_inventory_source_pg.last_updated is None, "another_inventory_source_pg unexpectedly updated."

        # Launch job
        job_pg = job_template.launch()

        # Wait for the inventory sources to start
        inventory_source_pg.wait_until_started()
        another_inventory_source_pg.wait_until_started()

        update_pg = inventory_source_pg.get_related('current_update')
        another_update_pg = another_inventory_source_pg.get_related('current_update')

        update_pg_started = parse(update_pg.created)
        another_update_pg_started = parse(another_update_pg.created)

        # Identify the sequence of the inventory updates and navigate to cancel_pg
        if update_pg_started > another_update_pg_started:
            cancel_pg = another_update_pg.get_related('cancel')
            assert cancel_pg.can_cancel, "Inventory update is not cancellable, it may have already completed - %s" % another_update_pg.get()

            # Set new set of vars
            first_update = another_update_pg
            second_update = update_pg
            first_inventory_source = another_inventory_source_pg
            second_inventory_source = inventory_source_pg

        else:
            cancel_pg = update_pg.get_related('cancel')
            assert cancel_pg.can_cancel, "Inventory update is not cancellable, it may have already completed - %s" % update_pg.get()

            # Set new set of vars
            first_update = update_pg
            second_update = another_update_pg
            first_inventory_source = inventory_source_pg
            second_inventory_source = another_inventory_source_pg

        # Cancel the first inventory update
        cancel_pg.post()

        # Assess job status
        job_pg = job_pg.wait_until_completed()
        assert not job_pg.is_successful, "Job run unexpectedly completed successfully - %s" % job_pg
        assert job_pg.job_explanation.startswith("Previous Task Failed: inventory_update"), \
            "Unexpected job_explanation: %s" % job_pg.job_explanation

        # Assert first inventory update cancelled
        first_update.get()
        assert first_update.status == 'canceled', "Did not cancel job as " \
            "expected (expected status:canceled) - %s" % first_update

        # Assert first inventory source cancelled
        first_inventory_source.get()
        assert first_inventory_source.status == 'canceled', "Did not cancel job as " \
            "expected (expected status:canceled) - %s" % first_inventory_source

        # Assert second inventory update failed
        second_update.get()
        assert second_update.status == 'failed', "Secondary inventory update not failed (status:%s)" % second_update.status
        assert second_update.job_explanation.startswith("Previous Task Failed: inventory_update")

        # Assert second inventory update failed
        second_inventory_source.get()
        assert second_inventory_source.status == 'failed', "Secondary inventory update not failed (status:%s)" % second_inventory_source.status

    def test_cascade_cancel_with_project_update(self, job_template, project_with_scm_update_on_launch, api_unified_jobs_pg):
        '''
        Tests that if you cancel a SCM update before it finishes that its dependent job
        fails.
        '''
        job_template.patch(project=project_with_scm_update_on_launch.id)
        project_with_scm_update_on_launch.patch(scm_url='https://github.com/ansible/ansible-examples')

        # Launch job
        job_pg = job_template.launch()

        # Wait for new update to start and cancel it
        project_with_scm_update_on_launch.wait_until_started()
        current_update_pg = project_with_scm_update_on_launch.get_related('current_update')
        cancel_pg = current_update_pg.get_related('cancel')
        assert cancel_pg.can_cancel, "The project update is not cancellable, it may have already completed - %s" % current_update_pg.get()
        cancel_pg.post()

        # Assert that original job failed
        job_pg = job_pg.wait_until_completed()
        assert not job_pg.is_successful, "Job run unexpectedly completed successfully - %s" % job_pg
        assert job_pg.job_explanation.startswith("Previous Task Failed: project_update")

        # Assert new scm update was canceled
        current_update_pg.get()
        assert current_update_pg.status == 'canceled', "Unexpected job" \
            "status after cancelling (expected 'canceled') - %s" % \
            current_update_pg

        # Assert project cancelled
        project_with_scm_update_on_launch.get()
        assert project_with_scm_update_on_launch.status == 'canceled', \
            "Unexpected project_update status (expected status:canceled) - %s" % \
            project_with_scm_update_on_launch

    def test_cascade_cancel_with_inventory_and_project_updates(self, job_template, project_with_scm_update_on_launch, custom_group, api_unified_jobs_pg):
        '''
        Tests that if you cancel a scm update before it finishes that its dependent job
        fails. This test runs both inventory and SCM updates on job launch.
        '''
        job_template.patch(inventory=custom_group.inventory, project=project_with_scm_update_on_launch.id)
        project_with_scm_update_on_launch.patch(scm_url='https://github.com/ansible/ansible-examples')

        inventory_source_pg = custom_group.get_related('inventory_source')
        inventory_source_pg.patch(update_on_launch=True)

        # Assert that the cloud_group has not updated
        assert inventory_source_pg.last_updated is None, "inventory_source_pg unexpectedly updated."

        # Launch job
        job_pg = job_template.launch()

        # Wait for new update to start and cancel it
        project_with_scm_update_on_launch.wait_until_started()
        current_update_pg = project_with_scm_update_on_launch.get_related('current_update')
        cancel_pg = current_update_pg.get_related('cancel')
        assert cancel_pg.can_cancel, "The project update is not cancellable, it may have already completed - %s" % current_update_pg.get()
        cancel_pg.post()

        # Assert that original job failed
        job_pg = job_pg.wait_until_completed()
        assert not job_pg.is_successful, "Job run unexpectedly completed successfully - %s" % job_pg
        assert job_pg.job_explanation.startswith("Previous Task Failed: project_update")

        # Assert new scm update was canceled
        current_update_pg.get()
        assert current_update_pg.status == 'canceled', "Unexpected job" \
            "status after cancelling (expected 'canceled') - %s" % \
            current_update_pg

        # Assert project cancelled
        project_with_scm_update_on_launch.get()
        assert project_with_scm_update_on_launch.status == 'canceled', \
            "Unexpected job status after cancelling (expected 'canceled') - " \
            "%s" % project_with_scm_update_on_launch

        # Assert update_pg successful
        inventory_source_pg.wait_until_completed()
        update_pg = inventory_source_pg.get_related('last_update')
        assert update_pg.is_successful, "Update unsuccessful - %s" % update_pg

        # Assert inventory source successful
        inventory_source_pg.get()
        assert inventory_source_pg.is_successful, "inventory_source unsuccessful - %s" % inventory_source_pg


@pytest.mark.api
@pytest.mark.skip_selenium
@pytest.mark.destructive
class Test_Scan_Job(Base_Api_Test):
    '''Tests for scan jobs.'''
    pytestmark = pytest.mark.usefixtures('authtoken', 'backup_license')

    def test_launch_scan_job_without_mongodb(self, install_enterprise_license, stop_mongodb, scan_job_with_status_completed):
        '''Tests that scan jobs without mongodb running fail appropriately.'''
        assert scan_job_with_status_completed.status == "error", \
            "Unexpected job status when running a scan job without MongoDB running - %s." % scan_job_with_status_completed.status
        assert scan_job_with_status_completed.result_traceback.endswith("RuntimeError: Fact Scan Database is offline\n"), \
            "Unexpected traceback upon running a scan job with MongoDB offline - %s." % scan_job_with_status_completed.result_traceback


@pytest.fixture(scope="function", params=['aws', 'rax', 'azure', 'gce', 'vmware'])
def job_template_with_cloud_credential(request, job_template, host):
    cloud_credential = request.getfuncargvalue(request.param + '_credential')

    # PATCH the job_template with the correct inventory and cloud_credential
    job_template.patch(inventory=host.inventory,
                       cloud_credential=cloud_credential.id)
    return job_template


@pytest.mark.api
@pytest.mark.skip_selenium
@pytest.mark.destructive
class Test_Cloud_Credential_Job(Base_Api_Test):
    '''
    Verify that cloud credentials are properly passed to playbooks as
    environment variables ('job_env')
    '''

    pytestmark = pytest.mark.usefixtures('authtoken', 'backup_license', 'install_license_unlimited')

    def test_job_env(self, job_template_with_cloud_credential):
        '''Verify that job_env has the expected cloud_credential variables'''

        # get cloud_credential
        cloud_credential = job_template_with_cloud_credential.get_related('cloud_credential')

        # launch job
        job_pg = job_template_with_cloud_credential.launch()

        # wait for completion
        job_pg = job_pg.wait_until_completed()

        # assert successful completion of job
        assert job_pg.is_successful, "Job unsuccessful - %s " % job_pg

        # Assert expected environment variables and their values
        if cloud_credential.kind == 'aws':
            self.has_credentials('cloud', cloud_credential.kind, ['username'])
            expected_env_vars = dict(
                AWS_ACCESS_KEY=self.credentials['cloud'][cloud_credential.kind]['username'],
                AWS_SECRET_KEY=u'**********'
            )
        elif cloud_credential.kind == 'rax':
            self.has_credentials('cloud', cloud_credential.kind, ['username'])
            expected_env_vars = dict(
                RAX_USERNAME=self.credentials['cloud'][cloud_credential.kind]['username'],
                RAX_API_KEY=u'**********'
            )
        elif cloud_credential.kind == 'gce':
            self.has_credentials('cloud', cloud_credential.kind, ['username', 'project'])
            expected_env_vars = dict(
                GCE_EMAIL=self.credentials['cloud'][cloud_credential.kind]['username'],
                GCE_PROJECT=self.credentials['cloud'][cloud_credential.kind]['project'],
                GCE_PEM_FILE_PATH=lambda x: re.match(r'^/tmp/ansible_tower_\w+/tmp\w+', x)
            )
        elif cloud_credential.kind == 'azure':
            self.has_credentials('cloud', cloud_credential.kind, ['username'])
            expected_env_vars = dict(
                AZURE_SUBSCRIPTION_ID=self.credentials['cloud'][cloud_credential.kind]['username'],
                AZURE_CERT_PATH=lambda x: re.match(r'^/tmp/ansible_tower_\w+/tmp\w+', x)
            )

        elif cloud_credential.kind == 'vmware':
            self.has_credentials('cloud', cloud_credential.kind, ['username', 'host'])
            expected_env_vars = dict(
                VMWARE_USER=self.credentials['cloud'][cloud_credential.kind]['username'],
                VMWARE_PASSWORD=u'**********',
                VMWARE_HOST=self.credentials['cloud'][cloud_credential.kind]['host']
            )
        else:
            raise Exception("Unhandled cloud type: %s" % cloud_credential.kind)

        # assert the expected job_env variables are present
        for env_var, env_val in expected_env_vars.items():
            assert env_var in job_pg.job_env, \
                "Missing expected %s environment variable %s in job_env.\n%s" % \
                (cloud_credential.kind, env_var, json.dumps(job_pg.job_env, indent=2))
            if isinstance(env_val, types.FunctionType):
                is_correct = env_val(job_pg.job_env[env_var])
            else:
                is_correct = job_pg.job_env[env_var] == env_val

            assert is_correct, "Unexpected value for %s environment variable %s" \
                "in job_env ('%s')" % (cloud_credential.kind, env_var,
                                       job_pg.job_env[env_var])


@pytest.fixture(scope="function")
def cloud_inventory_job_template(request, job_template, cloud_group):
    # PATCH the job_template with the correct inventory and cloud_credential
    job_template.patch(inventory=cloud_group.inventory)
    return job_template


@pytest.mark.api
@pytest.mark.skip_selenium
@pytest.mark.destructive
class Test_Update_On_Launch(Base_Api_Test):
    '''
    Verify that, when configured, inventory_updates and project_updates are
    initiated on job launch
    '''

    pytestmark = pytest.mark.usefixtures('authtoken', 'backup_license', 'install_license_unlimited')

    def test_inventory(self, cloud_inventory_job_template, cloud_group):
        '''Verify that an inventory_update is triggered by job launch'''

        # 1) Set update_on_launch
        inv_src_pg = cloud_group.get_related('inventory_source')
        inv_src_pg.patch(update_on_launch=True)
        assert inv_src_pg.update_cache_timeout == 0
        assert inv_src_pg.last_updated is None, "Not expecting inventory_source an have been updated - %s" % \
            json.dumps(inv_src_pg.json, indent=4)

        # 2) Update job_template to cloud inventory
        cloud_inventory_job_template.patch(inventory=cloud_group.inventory)

        # 3) Launch job_template and wait for completion
        cloud_inventory_job_template.launch_job().wait_until_completed(timeout=50 * 10)

        # 4) Ensure inventory_update was triggered
        inv_src_pg.get()
        assert inv_src_pg.last_updated is not None, "Expecting value for last_updated - %s" % \
            json.dumps(inv_src_pg.json, indent=4)
        assert inv_src_pg.last_job_run is not None, "Expecting value for last_job_run - %s" % \
            json.dumps(inv_src_pg.json, indent=4)

        # 5) Ensure inventory_update was successful
        last_update = inv_src_pg.get_related('last_update')
        assert last_update.is_successful, "last_update unsuccessful - %s" % last_update
        assert inv_src_pg.is_successful, "inventory_source unsuccessful - %s" % json.dumps(inv_src_pg.json, indent=4)

    def test_inventory_multiple(self, job_template, aws_inventory_source, rax_inventory_source):
        '''Verify that multiple inventory_update's are triggered by job launch'''

        # 1) Set update_on_launch
        aws_inventory_source.patch(update_on_launch=True)
        assert aws_inventory_source.update_on_launch
        assert aws_inventory_source.update_cache_timeout == 0
        assert aws_inventory_source.last_updated is None, "Not expecting inventory_source to have been updated - %s" % \
            json.dumps(aws_inventory_source.json, indent=4)
        rax_inventory_source.patch(update_on_launch=True)
        assert rax_inventory_source.update_on_launch
        assert rax_inventory_source.update_cache_timeout == 0
        assert rax_inventory_source.last_updated is None, "Not expecting inventory_source to have been updated - %s" % \
            json.dumps(rax_inventory_source.json, indent=4)

        # 2) Update job_template to cloud inventory
        assert rax_inventory_source.inventory == aws_inventory_source.inventory, \
            "The inventory differs between the two inventory sources"
        job_template.patch(inventory=aws_inventory_source.inventory)

        # 3) Launch job_template and wait for completion
        job_template.launch_job().wait_until_completed(timeout=50 * 10)

        # 4) Ensure inventory_update was triggered
        aws_inventory_source.get()
        assert aws_inventory_source.last_updated is not None, "Expecting value for aws_inventory_source last_updated - %s" % \
            json.dumps(aws_inventory_source.json, indent=4)
        assert aws_inventory_source.last_job_run is not None, "Expecting value for aws_inventory_source last_job_run - %s" % \
            json.dumps(aws_inventory_source.json, indent=4)

        rax_inventory_source.get()
        assert rax_inventory_source.last_updated is not None, "Expecting value for rax_inventory_source last_updated - %s" % \
            json.dumps(rax_inventory_source.json, indent=4)
        assert rax_inventory_source.last_job_run is not None, "Expecting value for rax_inventory_source last_job_run - %s" % \
            json.dumps(rax_inventory_source.json, indent=4)

        # 5) Ensure inventory_update was successful
        last_update = aws_inventory_source.get_related('last_update')
        assert last_update.is_successful, "aws_inventory_source -> last_update unsuccessful - %s" % last_update
        assert aws_inventory_source.is_successful, "inventory_source unsuccessful - %s" % \
            json.dumps(aws_inventory_source.json, indent=4)

        # assert last_update successful
        last_update = rax_inventory_source.get_related('last_update')
        assert last_update.is_successful, "rax_inventory_source -> last_update unsuccessful - %s" % last_update
        assert rax_inventory_source.is_successful, "inventory_source unsuccessful - %s" % \
            json.dumps(rax_inventory_source.json, indent=4)

    def test_inventory_cache_timeout(self, cloud_inventory_job_template, cloud_group):
        '''Verify that an inventory_update is not triggered by job launch if the cache is still valid'''

        # 1) Set update_on_launch and a 5min update_cache_timeout
        inv_src_pg = cloud_group.get_related('inventory_source')
        cache_timeout = 60 * 5
        inv_src_pg.patch(update_on_launch=True, update_cache_timeout=cache_timeout)
        assert inv_src_pg.update_cache_timeout == cache_timeout
        assert inv_src_pg.last_updated is None, "Not expecting inventory_source an have been updated - %s" % \
            json.dumps(inv_src_pg.json, indent=4)

        # 2) Update job_template to cloud inventory
        cloud_inventory_job_template.patch(inventory=cloud_group.inventory)

        # 3) Launch job_template and wait for completion
        cloud_inventory_job_template.launch_job().wait_until_completed(timeout=50 * 10)

        # 4) Ensure inventory_update was triggered
        inv_src_pg.get()
        assert inv_src_pg.last_updated is not None, "Expecting value for last_updated - %s" % \
            json.dumps(inv_src_pg.json, indent=4)
        assert inv_src_pg.last_job_run is not None, "Expecting value for last_job_run - %s" % \
            json.dumps(inv_src_pg.json, indent=4)
        last_updated = inv_src_pg.last_updated
        last_job_run = inv_src_pg.last_job_run

        # 5) Launch job_template and wait for completion
        cloud_inventory_job_template.launch_job().wait_until_completed(timeout=50 * 10)

        # 6) Ensure inventory_update was *NOT* triggered
        inv_src_pg.get()
        assert inv_src_pg.last_updated == last_updated, \
            "An inventory_update was unexpectedly triggered (last_updated changed)- %s" % \
            json.dumps(inv_src_pg.json, indent=4)
        assert inv_src_pg.last_job_run == last_job_run, \
            "An inventory_update was unexpectedly triggered (last_job_run changed)- %s" % \
            json.dumps(inv_src_pg.json, indent=4)

    def test_project(self, project_ansible_playbooks_git, job_template_ansible_playbooks_git):
        '''Verify that a project_update is triggered by job launch'''

        # 1) set scm_update_on_launch for the project
        project_ansible_playbooks_git.patch(scm_update_on_launch=True)
        assert project_ansible_playbooks_git.scm_update_on_launch
        assert project_ansible_playbooks_git.scm_update_cache_timeout == 0
        last_updated = project_ansible_playbooks_git.last_updated

        # 2) Launch job_template and wait for completion
        job_template_ansible_playbooks_git.launch_job().wait_until_completed(timeout=50 * 10)

        # 3) Ensure project_update was triggered and successful
        project_ansible_playbooks_git.get()
        assert project_ansible_playbooks_git.last_updated != last_updated, \
            "A project_update was not triggered, last_updated (%s) remains unchanged" % last_updated
        assert project_ansible_playbooks_git.is_successful, "project unsuccessful - %s" % \
            json.dumps(project_ansible_playbooks_git.json, indent=4)

    def test_project_cache_timeout(self, project_ansible_playbooks_git, job_template_ansible_playbooks_git):
        '''Verify that a project_update is not triggered when the cache_timeout has not exceeded'''

        # 1) set scm_update_on_launch for the project
        cache_timeout = 60 * 5
        project_ansible_playbooks_git.patch(scm_update_on_launch=True, scm_update_cache_timeout=cache_timeout)
        assert project_ansible_playbooks_git.scm_update_on_launch
        assert project_ansible_playbooks_git.scm_update_cache_timeout == cache_timeout
        assert project_ansible_playbooks_git.last_updated is not None
        last_updated = project_ansible_playbooks_git.last_updated

        # 2) Launch job_template and wait for completion
        job_template_ansible_playbooks_git.launch_job().wait_until_completed(timeout=50 * 10)

        # 3) Ensure project_update was *NOT* triggered
        project_ansible_playbooks_git.get()
        assert project_ansible_playbooks_git.last_updated == last_updated, \
            "A project_update happened, but was not expected"

    def test_inventory_and_project(self, project_ansible_playbooks_git, job_template_ansible_playbooks_git,
                                   cloud_group):
        '''Verify that a project_update and inventory_update are triggered by job launch'''

        # 1) Set scm_update_on_launch for the project
        project_ansible_playbooks_git.patch(scm_update_on_launch=True)
        assert project_ansible_playbooks_git.scm_update_on_launch
        last_updated = project_ansible_playbooks_git.last_updated

        # 2) Set update_on_launch for the inventory
        inv_src_pg = cloud_group.get_related('inventory_source')
        inv_src_pg.patch(update_on_launch=True)
        assert inv_src_pg.update_on_launch

        # 3) Update job_template to cloud inventory
        job_template_ansible_playbooks_git.patch(inventory=cloud_group.inventory)

        # 4) Launch job_template and wait for completion
        job_template_ansible_playbooks_git.launch_job().wait_until_completed(timeout=50 * 10)

        # 5) Ensure inventory_update was triggered and successful
        inv_src_pg.get()
        assert inv_src_pg.last_updated is not None, "Expecting value for last_updated - %s" % \
            json.dumps(inv_src_pg.json, indent=4)
        assert inv_src_pg.last_job_run is not None, "Expecting value for last_job_run - %s" % \
            json.dumps(inv_src_pg.json, indent=4)
        assert inv_src_pg.is_successful, "inventory_source unsuccessful - %s" % json.dumps(inv_src_pg.json, indent=4)

        # 6) Ensure project_update was triggered
        project_ansible_playbooks_git.get()
        assert project_ansible_playbooks_git.last_updated != last_updated, \
            "project_update was not triggered - %s" % json.dumps(project_ansible_playbooks_git.json, indent=4)
        assert project_ansible_playbooks_git.is_successful, "project unsuccessful - %s" % \
            json.dumps(project_ansible_playbooks_git.json, indent=4)
