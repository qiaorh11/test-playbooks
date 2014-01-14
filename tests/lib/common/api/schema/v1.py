from common.api.schema import Awx_Schema_Base

class Awx_Schema(Awx_Schema_Base):
    version = 'v1'
    component = '/api'

    def __init__(self):
        Awx_Schema_Base.__init__(self)

        # Shared enum's
        self.definitions['enum_launch_type'] = {
            'enum': [ '', 'manual', 'callback', 'scheduled', ]
        }
        self.definitions['enum_launch_status'] = {
            'enum': [ '', 'new', 'pending', 'waiting', 'running', 'successful', 'failed', 'error', 'canceled' ]
        }
        self.definitions['enum_project_status'] = {
            'enum': [ 'ok', 'missing', 'never updated', 'updating', 'failed', 'successful', ]
        }
        self.definitions['enum_project_update_status'] = {
            'enum': [ 'new', 'pending', 'waiting', 'running', 'successful', 'failed', 'error', 'canceled', ],
        }
        self.definitions['enum_inventory_status'] = {
            'enum': [ "", "none", "never updated", "updating", "failed", "successful", ]
        }
        self.definitions['enum_inventory_update_status'] = {
            'enum': [ "", "new", "pending", "waiting", "running", "successful", "failed", "error", "canceled", ],
        }
        self.definitions['enum_source_status'] = {
            'enum': [ 'error', 'failed', 'never updated', 'none', 'successful', 'updating']
        }
        self.definitions['enum_kind'] = {
            'enum': [ 'ssh', 'scm', 'aws', 'rax' ],
        }
        self.definitions['enum_passwords_needed_to_start'] = {
            'enum': [ 'ssh_password', 'sudo_password', 'ssh_key_unlock', ],
        }
        self.definitions['enum_activity_stream_operation'] = {
            'type': 'string',
            'enum': [ 'create', 'update', 'delete', 'associate', 'disassociate'],
        }
        self.definitions['enum_dashboard_inventory_sources_label'] = {
            'type': 'string',
            'enum': [ 'Amazon EC2', 'Rackspace', ],
        }
        self.definitions['enum_dashboard_scm_types_label'] = {
            'type': 'string',
            'enum': [ 'Subversion', 'Git', 'Mercurial' ],
        }
        self.definitions['enum_permission_type'] = {
            'type': 'string',
            'enum': [ 'read', 'write', 'admin', 'run', 'check' ],
        }

        # Shared errors
        self.definitions['error_required_field'] = {
            'type': 'array',
            'minItems': 1,
            'uniqueItems': True,
            'items': {
                'type': 'string',
                'pattern': '^This field is required.$',
            },
        }

        self.definitions['error_login_failure'] = {
            'type': 'array',
            'minItems': 0,
            'uniqueItems': True,
            'items': {
                'type': 'string', 'pattern': '^Unable to login with provided credentials.$',
            },
        }

        # Shared fields
        self.definitions['id'] = dict(type='number', minimum=1)
        self.definitions['id_or_null'] = dict(type=['number', 'null'], minimum=1)

        self.definitions['dashboard_common_core'] = {
            'type': 'object',
            'required': [ 'url', 'total', ],
            'additionalProperties': False,
            'properties': {
                'url': { 'type': 'string', 'format': 'uri'},
                'total': { 'type': 'number', 'minimum': 0, },
            }
        }

        self.definitions['dashboard_inventory_sources'] = {
            'type': 'object',
            'required': [ 'url', 'total', 'failures_url', 'failed', 'label', ],
            'additionalProperties': False,
            'properties': {
                'failures_url': { 'type': 'string', 'format': 'uri'},
                'failed': { 'type': 'number', 'minimum': 0, },
                'label': { '$ref': '#/definitions/enum_dashboard_inventory_sources_label', },
                'url': { 'type': 'string', 'format': 'uri'},
                'total': { 'type': 'number', 'minimum': 0, },
            },
        }
        self.definitions['dashboard_scm_types'] = {
            'type': 'object',
            'required': [ 'url', 'total', 'failures_url', 'failed', 'label', ],
            'additionalProperties': False,
            'properties': {
                'failures_url': { 'type': 'string', 'format': 'uri'},
                'failed': { 'type': 'number', 'minimum': 0, },
                'label': { '$ref': '#/definitions/enum_dashboard_scm_types_label', },
                'url': { 'type': 'string', 'format': 'uri'},
                'total': { 'type': 'number', 'minimum': 0, },
            },
        }

        self.definitions['passwords_needed_to_start'] = {
            'type': 'array',
            'minItems': 0,
            'uniqueItems': True,
            'items': {
                'type': 'string',
                'uniqueItems': True,
                '$ref': '#/definitions/enum_passwords_needed_to_start',
            },
        }
        self.definitions['summary_fields_project'] = {
            'type': 'object',
            'required': ['name', 'description', ],
            'additionalProperties': False,
            'properties': {
                'name':        { 'type': 'string', },
                'description': { 'type': 'string', },
                'status':      { '$ref': '#/definitions/enum_project_status' },
            },
        }
        self.definitions['job_env'] = {
            'type': 'object',
            'additionalProperties': True,
            'properties': {
                '_': { 'type': 'string', 'minLength': 1, 'pattern': '^/usr/bin/supervisord', },
                'USER': { 'type': 'string', 'minLength': 1, 'pattern': '^awx$', },
                'HOME': { 'type': 'string', 'minLength': 1, 'pattern': '^/var/lib/awx$'},
                'PWD': { 'type': 'string', 'minLength': 1, },
                'PATH': { 'type': 'string', 'minLength': 1, },
                'TERM': { 'type': 'string', 'minLength': 1, },
                'LANG': { 'type': 'string', 'minLength': 1, },
                'TZ': { 'type': 'string', 'minLength': 1, },
            },
        }

        # Shared summary fields
        self.definitions['summary_fields_inventory'] = {
            'type': 'object',
            'required': ['name', 'description', 'has_active_failures', 'hosts_with_active_failures',],
            'additionalProperties': False,
            'properties': {
                'name':                         { 'type': 'string', },
                'description':                  { 'type': 'string', },
                'has_active_failures':          { 'type': 'boolean', },
                'has_inventory_sources':        { 'type': 'boolean', },
                'hosts_with_active_failures':   { 'type': 'number', 'minimum': 0, },
                'groups_with_active_failures':  { 'type': 'number', 'minimum': 0, },
                'inventory_sources_with_failures': { 'type': 'number', 'minimum': 0, },
                'total_groups':                 { 'type': 'number', 'minimum': 0, },
                'total_hosts':                  { 'type': 'number', 'minimum': 0, },
                'total_inventory_sources':      { 'type': 'number', 'minimum': 0, },
            },
        }
        self.definitions['summary_fields_inventory_source'] = {
            'type': 'object',
            'required': ['source', 'status', ],
            'additionalProperties': False,
            'properties': {
                'source':       { 'type': 'string', },
                'last_updated': { 'type': 'string', 'format': 'date-time', },
                'status':       { '$ref': '#/definitions/enum_source_status', },
            },
        }
        self.definitions['summary_fields_credential'] = {
            'type': 'object',
            'required': ['name', 'description', 'kind', 'cloud', ],
            'additionalProperties': False,
            'properties': {
                'name':        { 'type': 'string', },
                'description': { 'type': 'string', },
                'kind':        { '$ref': '#/definitions/enum_kind', },
                'cloud':       { 'type': 'boolean', },
            },
        }
        self.definitions['summary_fields_job_template'] = {
            'type': 'object',
            'required': ['name', 'description', ],
            'additionalProperties': False,
            'properties': {
                'name':        { 'type': 'string', },
                'description': { 'type': 'string', },
            },
        }

        self.definitions['summary_fields_source'] = {
            'type': 'object',
            'required': ['source', 'status', ],
            'additionalProperties': False,
            'properties': {
                'source':       { 'type': 'string', },
                'status':       { '$ref': '#/definitions/enum_source_status', },
                'last_updated': { 'type': 'string', 'format': 'date-time', },
            },
        }

        self.definitions['summary_fields_group'] = {
            'type': 'object',
            'required': [ 'name', 'description', 'has_active_failures', 'has_inventory_sources', 'hosts_with_active_failures', 'total_hosts', 'total_groups', 'groups_with_active_failures', ],
            'additionalProperties': False,
            'properties': {
                'name': { 'type': 'string', },
                'description': { 'type': 'string', },
                'has_active_failures': { 'type': 'boolean', },
                'has_inventory_sources': { 'type': 'boolean', },
                'hosts_with_active_failures': { 'type': 'number', 'minimum': 0 },
                'total_hosts': { 'type': 'number', 'minimum': 0 },
                'total_groups': { 'type': 'number', 'minimum': 0 },
                'groups_with_active_failures': { 'type': 'number', 'minimum': 0 },
            },
        }

        self.definitions['summary_fields_groups'] = {
            'type': 'object',
            'required': [ 'id', 'name', ],
            'additionalProperties': False,
            'properties': {
                'id': { 'type': 'number', 'minimum': 1, },
                'name': { 'type': 'string', },
            },
        }

        self.definitions['summary_fields_groups_list'] = {
            'type': 'array',
            'minItems': 0,
            'uniqueItems': True,
            'items': {
                '$ref': '#/definitions/summary_fields_groups',
            },
        }

        self.definitions['summary_fields_last_job'] = {
            'type': 'object',
            'required': [ 'description', 'status', 'failed', 'job_template_id', 'job_template_name' ],
            'additionalProperties': False,
            'properties': {
                'description':          { 'type': 'string', },
                'failed':               { 'type': 'boolean', },
                'job_template_id':      { '$ref': '#/definitions/id', },
                'job_template_name':    { 'type': 'string', },
                'status':               { '$ref': '#/definitions/enum_source_status', },
            },
        }

        self.definitions['summary_fields_last_job_host_summary'] = {
            'type': 'object',
            'required': [ 'failed', ],
            'additionalProperties': False,
            'properties': {
                'failed': { 'type': 'boolean', },
            },
        }

        self.definitions['user'] = {
            'type': 'object',
            'required': ['created', 'email', 'first_name', 'id', 'is_superuser', 'last_name', 'ldap_dn', 'related', 'url', 'username'],
            'additionalProperties': False,
            'properties': {
                'id': { 'type': 'number', 'minimum': 1, },
                'url': { 'type': 'string', 'format': 'uri'},
                'created':  { 'type': 'string', 'format': 'date-time', },
                'modified': { 'type': 'string', 'format': 'date-time', },
                'first_name': { 'type': 'string', },
                'last_name': { 'type': 'string', },
                'username': { 'type': 'string', },
                'ldap_dn': { 'type': 'string', },
                'is_superuser': { 'type': 'boolean', },
                'email': { 'type': 'string', 'format': 'email'},
                'related': {
                    'type': 'object',
                    'required': ['admin_of_organizations', 'credentials', 'organizations', 'permissions', 'projects', 'teams', 'activity_stream', ],
                    'additionalProperties': False,
                    'properties': {
                        'admin_of_organizations':   { 'type': 'string', 'format': 'uri' },
                        'credentials':              { 'type': 'string', 'format': 'uri' },
                        'organizations':            { 'type': 'string', 'format': 'uri' },
                        'permissions':              { 'type': 'string', 'format': 'uri' },
                        'projects':                 { 'type': 'string', 'format': 'uri' },
                        'teams':                    { 'type': 'string', 'format': 'uri' },
                        'activity_stream':          { 'type': 'string', 'format': 'uri' },
                    },
                },
            },
        }

    @property
    def put(self):
        return {}

    @property
    def patch(self):
        return {}

    @property
    def post(self):
        return {}

    @property
    def head(self):
        return {}

    @property
    def get(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'properties': {
                'available_versions': { 'type': 'object', },
                'description': { 'type': 'string', },
                'current_version': { 'type': 'string', },
            },
            'required': ['available_versions', 'description', 'current_version'],
            'additionalProperties': False,
        })

    @property
    def options(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': [ 'renders', 'parses' ],
            'additionalProperties': True,
            'properties': {
                'name': {
                    'type': 'string',
                },
                'description': {
                    'type': 'string',
                },
                'renders': {
                    'type': 'array',
                    "items": {
                        'type': 'string'
                    },
                    'minItems': 1,
                    'uniqueItems': True,
                },
                'parses': {
                    'type': 'array',
                    'items': {
                        'type': 'string'
                    },
                    'minItems': 1,
                    'uniqueItems': True,
                },
                'search_fields': {
                    'type': 'array',
                    'minItems': 1,
                    'uniqueItems': True,
                    'items': {
                        'type': 'string'
                    },
                }
            },
        })

    @property
    def bad_request(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'additionalProperties': False,
            'properties': {
                'name': { '$ref': '#/definitions/error_required_field' },
                'username': { '$ref': '#/definitions/error_required_field' },
                'password': { '$ref': '#/definitions/error_required_field' },
                'organization': { '$ref': '#/definitions/error_required_field' },
                'inventory': { '$ref': '#/definitions/error_required_field' },
                'job_type': { '$ref': '#/definitions/error_required_field' },
                'playbook': { '$ref': '#/definitions/error_required_field' },
                'non_field_errors': { '$ref': '#/definitions/error_login_failure' },
            },
        })

    @property
    def method_not_allowed(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['detail', ],
            'additionalProperties': False,
            'properties': {
                'detail': {
                    'type': 'string',
                    'pattern': "^Method '[A-Z]+' not allowed.$",
                },
            },
        })

    @property
    def unauthorized(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['detail', ],
            'additionalProperties': False,
            'properties': {
                'detail': {
                    'type': 'string',
                    'pattern': '^Authentication credentials were not provided.$'
                },
            },
        })

class Awx_Schema_v1(Awx_Schema):
    component = '/api/v1'

    @property
    def get(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': [ ],
            'additionalProperties': False,
            'properties': {
                'authtoken': { 'type': 'string', 'format': 'uri' },
                'config': { 'type': 'string', 'format': 'uri' },
                'me': { 'type': 'string', 'format': 'uri' },
                'dashboard': { 'type': 'string', 'format': 'uri' },
                'organizations': { 'type': 'string', 'format': 'uri' },
                'users': { 'type': 'string', 'format': 'uri' },
                'projects': { 'type': 'string', 'format': 'uri' },
                'teams': { 'type': 'string', 'format': 'uri' },
                'credentials': { 'type': 'string', 'format': 'uri' },
                'inventory': { 'type': 'string', 'format': 'uri' },
                'inventory_sources': { 'type': 'string', 'format': 'uri' },
                'groups': { 'type': 'string', 'format': 'uri' },
                'hosts': { 'type': 'string', 'format': 'uri' },
                'job_templates': { 'type': 'string', 'format': 'uri' },
                'jobs': { 'type': 'string', 'format': 'uri' },
                'activity_stream': { 'type': 'string', 'format': 'uri' },
            },
        }

class Awx_Schema_Organizations(Awx_Schema):
    component = '/organizations'

    def __init__(self):
        super(Awx_Schema_Organizations, self).__init__()

        self.definitions['organization'] = {
            'type': 'object',
            'required': ['id', 'url', 'name', 'description', 'created', 'modified', 'summary_fields', 'related'],
            'additionalProperties': False,
            'properties': {
                'id': { 'type': 'number', 'minimum': 1, },
                'url': { 'type': 'string', 'format': 'uri'},
                'related': {
                    'type': 'object',
                    'required': ['created_by', 'admins', 'inventories', 'users', 'projects', 'teams', 'activity_stream', ],
                    'additionalProperties': False,
                    'properties': {
                        'created_by':   { 'type': 'string', 'format': 'uri' },
                        'admins':       { 'type': 'string', 'format': 'uri' },
                        'inventories':  { 'type': 'string', 'format': 'uri' },
                        'users':        { 'type': 'string', 'format': 'uri' },
                        'projects':     { 'type': 'string', 'format': 'uri' },
                        'teams':        { 'type': 'string', 'format': 'uri' },
                        'activity_stream': { 'type': 'string', 'format': 'uri' },
                    },
                },
                'summary_fields': { 'type': 'object', }, # FIXME
                'created':  { 'type': 'string', 'format': 'date-time', },
                'modified': { 'type': 'string', 'format': 'date-time', },
                'name': { 'type': 'string', },
                'description': { 'type': 'string', },
            },
        }

    @property
    def duplicate(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'array',
                    'minItems': 0,
                    'uniqueItems': True,
                    'items': {
                        'type': 'string',
                        'pattern': '^Organization with this Name already exists.$',
                    },
                },
            },
            'required': ['name', ],
            'additionalProperties': False,
        }

    @property
    def get(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['count', 'next', 'previous', 'results', ],
            'additionalProperties': False,
            'properties': {
                'count': { 'type': 'number', 'minimum': 0, },
                'next': { 'type': ['string','null'], },
                'previous': { 'type': ['string','null'], },
                'results': {
                    'type': 'array',
                    'minItems': 0,
                    'uniqueItems': True,
                    'items': {
                        '$ref': '#/definitions/organization',
                    },
                },
            },
        })

    @property
    def post(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            '$ref': '#/definitions/organization',
        })

class Awx_Schema_Users(Awx_Schema):
    component = '/users'

    @property
    def duplicate(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['username', ],
            'additionalProperties': False,
            'properties': {
                "username": {
                    'type': 'array',
                    'minItems': 0,
                    'uniqueItems': True,
                    'items': {
                        'type': 'string',
                        'pattern': '^User with this Username already exists.$',
                    },
                },
            },
        }

    @property
    def get(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['count', 'next', 'previous', 'results', ],
            'additionalProperties': False,
            'properties': {
                'count': { 'type': 'number', 'minimum': 0, },
                'next': { 'type': ['string','null'], },
                'previous': { 'type': ['string','null'], },
                'results': {
                    'type': 'array',
                    'minItems': 0,
                    'uniqueItems': True,
                    'items': {
                        '$ref': '#definitions/user',
                    },
                },
            },
        })

    @property
    def post(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            '$ref': '#/definitions/user',
        })

class Awx_Schema_Team_Users(Awx_Schema_Users):
    component = '/teams/\d+/users'

class Awx_Schema_Org_Users(Awx_Schema_Users):
    component = '/organizations/\d+/users'

class Awx_Schema_Org_Admins(Awx_Schema_Users):
    component = '/organizations/\d+/admins'

class Awx_Schema_Inventories(Awx_Schema):
    component = '/inventories'

    def __init__(self):
        super(Awx_Schema_Inventories, self).__init__()

        self.definitions['inventory'] = {
            'type': 'object',
            'required': ['id', 'url', 'related', 'summary_fields', 'created', 'modified', 'name', 'description', 'organization', 'variables', 'has_active_failures', 'hosts_with_active_failures', 'has_inventory_sources', 'total_inventory_sources', 'total_hosts', 'inventory_sources_with_failures', 'groups_with_active_failures', 'total_groups', ],

            'additionalProperties': False,
            'properties': {
                'id': { 'type': 'number', 'minimum': 1, },
                'url': { 'type': 'string', 'format': 'uri'},
                'related': {
                    'type': 'object',
                    'required': ['created_by', 'variable_data', 'root_groups', 'script', 'tree', 'hosts', 'groups', 'organization', 'inventory_sources', 'activity_stream', ],
                    'additionalProperties': False,
                    'properties': {
                        'created_by':       { 'type': 'string', 'format': 'uri', },
                        'variable_data':    { 'type': 'string', 'format': 'uri', },
                        'root_groups':      { 'type': 'string', 'format': 'uri', },
                        'script':           { 'type': 'string', 'format': 'uri', },
                        'tree':             { 'type': 'string', 'format': 'uri', },
                        'hosts':            { 'type': 'string', 'format': 'uri', },
                        'groups':           { 'type': 'string', 'format': 'uri', },
                        'organization':     { 'type': 'string', 'format': 'uri', },
                        'inventory_sources':{ 'type': 'string', 'format': 'uri', },
                        'activity_stream': { 'type': 'string', 'format': 'uri' },
                    },
                },
                'summary_fields':  {
                    'type': 'object',
                    'required': ['organization'],
                    'additionalProperties': False,
                    'properties': {
                        "organization": {
                            'type': 'object',
                            'required': ['name', 'description'],
                            'additionalProperties': False,
                            'properties': {
                                'name':        { 'type': 'string', },
                                'description': { 'type': 'string', },
                            },
                        },
                    },
                },
                'created':  { 'type': 'string', 'format': 'date-time', },
                'modified': { 'type': 'string', 'format': 'date-time', },
                'name': { 'type': 'string', },
                'description': { 'type': 'string', },
                'organization': { 'type': 'number', 'minimum': 1, },
                'variables': { 'type': 'string', },
                'has_active_failures': { 'type': 'boolean', },
                'hosts_with_active_failures': { 'type': 'number', 'minimum': 0, },
                'total_hosts': { 'type': 'number', 'minimum': 0, },
                'groups_with_active_failures': { 'type': 'number', 'minimum': 0, },
                'total_groups': { 'type': 'number', 'minimum': 0, },
                'total_inventory_sources': { 'type': 'number', 'minimum': 0, },
                'has_inventory_sources': { 'type': 'boolean', },
                'inventory_sources_with_failures': { 'type': 'number', 'minimum': 0, },
            },
        }

    @property
    def get(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['count', 'next', 'previous', 'results', ],
            'additionalProperties': False,
            'properties': {
                'count': { 'type': 'number', 'minimum': 0, },
                'next': { 'type': ['string','null'], },
                'previous': { 'type': ['string','null'], },
                'results': {
                    'type': 'array',
                    'minItems': 0,
                    'uniqueItems': True,
                    'items': {
                        '$ref': '#definitions/inventory',
                    },
                },
            },
        })

    @property
    def post(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            '$ref': '#/definitions/inventory',
        })

    @property
    def duplicate(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['name', '__all__'],
            'additionalProperties': False,
            'properties': {
                "__all__": {
                    'type': 'array',
                    'minItems': 1,
                    'uniqueItems': True,
                    'items': {
                        'type': 'string',
                        'pattern': '^Inventory with this Name and Organization already exists.$',
                    },
                },
                "name": {
                    'type': 'array',
                    'minItems': 1,
                    'uniqueItems': True,
                    'items': {
                        'type': 'string',
                        'pattern': '^Inventory with this Name already exists.$',
                    },
                },
            },
        }


class Awx_Schema_Groups(Awx_Schema):
    component = '/groups'

    def __init__(self):
        super(Awx_Schema_Groups, self).__init__()

        self.definitions['group'] = {
            'type': 'object',
            'required': ['id', 'url', 'created', 'modified', 'name', 'description', 'inventory', 'variables', 'has_active_failures', 'hosts_with_active_failures', 'has_inventory_sources', 'related', 'summary_fields', 'total_hosts', 'groups_with_active_failures', 'total_groups'],
            'additionalProperties': False,
            'properties': {
                'id': { 'type': 'number', 'minimum': 1, },
                'url': { 'type': 'string', 'format': 'uri'},
                'created':  { 'type': 'string', 'format': 'date-time', },
                'modified': { 'type': 'string', 'format': 'date-time', },
                'name': { 'type': 'string', },
                'description': { 'type': 'string', },
                'inventory': { 'type': 'number', 'minimum': 1, },
                'variables': { 'type': 'string', },
                'has_active_failures': { 'type': 'boolean', },
                'hosts_with_active_failures': { 'type': 'number', 'minimum': 0, },
                'has_inventory_sources': { 'type': 'boolean', },
                'total_hosts': { 'type': 'number', 'minimum': 0, },
                'groups_with_active_failures': { 'type': 'number', 'minimum': 0, },
                'total_groups':{ 'type': 'number', 'minimum': 0, },
                'related': {
                    'type': 'object',
                    'required': [ 'job_host_summaries', 'variable_data', 'inventory_source', 'job_events', 'potential_children', 'all_hosts', 'hosts', 'inventory', 'children', 'activity_stream', ],
                    'additionalProperties': False,
                    'properties': {
                        "created_by":           { 'type': 'string', 'format': 'uri', },
                        "job_host_summaries":   { 'type': 'string', 'format': 'uri', },
                        "variable_data":        { 'type': 'string', 'format': 'uri', },
                        "inventory_source":     { 'type': 'string', 'format': 'uri', },
                        "job_events":           { 'type': 'string', 'format': 'uri', },
                        "potential_children":   { 'type': 'string', 'format': 'uri', },
                        "all_hosts":            { 'type': 'string', 'format': 'uri', },
                        "hosts":                { 'type': 'string', 'format': 'uri', },
                        "inventory":            { 'type': 'string', 'format': 'uri', },
                        "children":             { 'type': 'string', 'format': 'uri', },
                        'activity_stream': { 'type': 'string', 'format': 'uri' },
                    },
                },
                'summary_fields':  {
                    'type': 'object',
                    'required': ['inventory', 'inventory_source'],
                    'additionalProperties': False,
                    'properties': {
                        "inventory": {
                            '$ref': '#/definitions/summary_fields_inventory',
                        },
                        "inventory_source": {
                            '$ref': '#/definitions/summary_fields_source',
                        },
                    },
                },
            },
        }

    @property
    def get(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['count', 'next', 'previous', 'results', ],
            'additionalProperties': False,
            'properties': {
                'count': { 'type': 'number', 'minimum': 0, },
                'next': { 'type': ['string','null'], },
                'previous': { 'type': ['string','null'], },
                'results': {
                    'type': 'array',
                    'minItems': 0,
                    'uniqueItems': True,
                    'items': {
                        '$ref': '#/definitions/group',
                    },
                },
            },
        })

    @property
    def post(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            '$ref': '#/definitions/group',
        })

    @property
    def duplicate(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['__all__',],
            'additionalProperties': False,
            'properties': {
                "__all__": {
                    'type': 'array',
                    'minItems': 0,
                    'uniqueItems': True,
                    'items': {
                        'type': 'string',
                        'pattern': '^Group with this Name and Inventory already exists.$',
                    },
                },
            },
        }

class Awx_Schema_Group_Children(Awx_Schema_Groups):
    component = '/groups/\d+/children'

class Awx_Schema_Hosts(Awx_Schema):
    component = '/hosts'

    def __init__(self):
        super(Awx_Schema_Hosts, self).__init__()

        self.definitions['host'] = {
            'type': 'object',
            'required': [ 'id', 'url', 'created', 'modified', 'name', 'description', 'inventory', 'variables', 'enabled', 'has_active_failures', 'has_inventory_sources', 'last_job', 'last_job_host_summary', 'related', 'summary_fields', ],
            'additionalProperties': False,
            'properties': {
                'id': { 'type': 'number', 'minimum': 1, },
                'url': { 'type': 'string', 'format': 'uri'},
                'created':  { 'type': 'string', 'format': 'date-time', },
                'modified': { 'type': 'string', 'format': 'date-time', },
                'name': { 'type': 'string', },
                'description': { 'type': 'string', },
                'inventory': { 'type': 'number', 'minimum': 1, },
                'variables': { 'type': 'string', },
                'instance_id': { 'type': 'string', },
                'enabled': { 'type': 'boolean', },
                'has_active_failures': { 'type': 'boolean', },
                'has_inventory_sources': { 'type': 'boolean', },
                'last_job': { 'type': ['number', 'null'] },
                'last_job_host_summary': { 'type': ['number', 'null'] },
                'related': {
                    'type': 'object',
                    'required': [ 'job_host_summaries', 'variable_data', 'job_events', 'groups', 'all_groups', 'inventory', ],
                    'additionalProperties': True,
                    'properties': {
                        'created_by':           { 'type': 'string', 'format': 'uri', },
                        'job_host_summaries':   { 'type': 'string', 'format': 'uri', },
                        'variable_data':        { 'type': 'string', 'format': 'uri', },
                        'job_events':           { 'type': 'string', 'format': 'uri', },
                        'groups':               { 'type': 'string', 'format': 'uri', },
                        'all_groups':           { 'type': 'string', 'format': 'uri', },
                        'inventory':            { 'type': 'string', 'format': 'uri', },
                        'last_job':             { 'type': 'string', 'format': 'uri', },
                        'last_job_host_summary':{ 'type': 'string', 'format': 'uri', },
                    },
                },
                'summary_fields':  {
                    'type': 'object',
                    'required': ['inventory', 'groups', 'all_groups', ], # 'last_job', 'last_job_host_summary', ],
                    'additionalProperties': True,
                    'properties': {
                        "inventory": {
                            '$ref': '#/definitions/summary_fields_inventory',
                        },
                        "all_groups": {
                            '$ref': '#/definitions/summary_fields_groups_list',
                        },
                        "groups": {
                            '$ref': '#/definitions/summary_fields_groups_list',
                        },
                        "last_job": {
                            '$ref': '#/definitions/summary_fields_last_job',
                        },
                        "last_job_host_summary": {
                            '$ref': '#/definitions/summary_fields_last_job_host_summary',
                        },
                    },
                },
            },
        }

    @property
    def get(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['count', 'next', 'previous', 'results', ],
            'additionalProperties': False,
            'properties': {
                'count': { 'type': 'number', 'minimum': 0, },
                'next': { 'type': ['string','null'], },
                'previous': { 'type': ['string','null'], },
                'results': {
                    'type': 'array',
                    'minItems': 0,
                    'uniqueItems': True,
                    'items': {
                        '$ref': '#/definitions/host',
                    },
                },
            },
        })

    @property
    def post(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            '$ref': '#/definitions/host',
        })

    @property
    def duplicate(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['__all__',],
            'additionalProperties': False,
            'properties': {
                "__all__": {
                    'type': 'array',
                    'minItems': 0,
                    'uniqueItems': True,
                    'items': {
                        'type': 'string',
                        'pattern': '^Host with this Name and Inventory already exists.$',
                    },
                },
            },
        }

class Awx_Schema_Group_Hosts(Awx_Schema_Hosts):
    component = '/groups/\d+/hosts'

class Awx_Schema_Credentials(Awx_Schema):
    component = '/credentials'

    def __init__(self):
        super(Awx_Schema_Credentials, self).__init__()

        self.definitions['credential'] = {
            'type': 'object',
            'required': [ 'id', 'name', 'username', 'password', 'kind', 'url', 'created', 'modified', 'description', 'ssh_key_data', 'ssh_key_unlock', 'sudo_username', 'sudo_password', 'user', 'team', 'cloud', 'related', 'summary_fields',],
            'additionalProperties': False,
            'properties': {
                'id': { 'type': 'number', 'minimum': 1, },
                'name': { 'type': 'string', },
                'url': { 'type': 'string', 'format': 'uri', },
                'kind': { '$ref': '#/definitions/enum_kind', },
                'cloud': { 'type': 'boolean', },
                'created':  { 'type': 'string', 'format': 'date-time', },
                'modified': { 'type': 'string', 'format': 'date-time', },
                'description': { 'type': 'string', },
                'username': { 'type': 'string', },
                'password': { 'type': 'string', },
                'ssh_key_data': { 'type': 'string', },
                'ssh_key_unlock': { 'type': 'string', },
                'sudo_username': { 'type': 'string', },
                'sudo_password': { 'type': 'string', },
                'user': { 'type': ['number', 'null'], 'minimum': 1, },
                'team': { 'type': ['number', 'null'], 'minimum': 1, },
                'related': {
                    'type': 'object',
                    'required': ['created_by', 'activity_stream', ],
                    'additionalProperties': False,
                    'properties': {
                        'user': { 'type': 'string', 'format': 'uri' },
                        'team': { 'type': 'string', 'format': 'uri' },
                        'created_by': { 'type': 'string', 'format': 'uri' },
                        'activity_stream': { 'type': 'string', 'format': 'uri' },
                    },
                },
                'summary_fields': {
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': {
                        'user': {
                            'type': 'object',
                            'required': ['username', 'first_name', 'last_name'],
                            'additionalProperties': False,
                            'properties': {
                                'username': { 'type': 'string' },
                                'first_name': { 'type': 'string' },
                                'last_name': { 'type': 'string' },
                            },
                        },
                        'team': {
                            'type': 'object',
                            'required': ['name', 'description' ],
                            'additionalProperties': False,
                            'properties': {
                                'name': { 'type': 'string' },
                                'description': { 'type': 'string' },
                            },
                        },
                    },
                },
            },
        }

    @property
    def post(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            '$ref': '#/definitions/credential',
        })

    @property
    def get(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['count', 'next', 'previous', 'results', ],
            'additionalProperties': False,
            'properties': {
                'count': { 'type': 'number', 'minimum': 0, },
                'next': { 'type': ['string','null'], },
                'previous': { 'type': ['string','null'], },
                'results': {
                    'type': 'array',
                    'minItems': 0,
                    'uniqueItems': True,
                    'items': {
                        '$ref': '#/definitions/credential',
                    },
                },
            },
        })

    @property
    def duplicate(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['__all__',],
            'additionalProperties': False,
            'properties': {
                "__all__": {
                    'type': 'array',
                    'minItems': 0,
                    'uniqueItems': True,
                    'items': {
                        'type': 'string',
                        'pattern': '^Credential with this .* already exists.$',
                    },
                },
            },
        }

class Awx_Schema_User_Credentials(Awx_Schema_Credentials):
    component = '/users/\d+/credentials'

class Awx_Schema_User_Permissions(Awx_Schema):
    component = '/users/\d+/permissions'

    def __init__(self):
        super(Awx_Schema_User_Permissions, self).__init__()

        self.definitions['permission'] = {
            'type': 'object',
            'required': [ 'id', 'url', 'created', 'modified', 'name', 'description', 'user', 'team', 'project', 'inventory', 'permission_type', 'related', 'summary_fields', ],
            'additionalProperties': False,
            'properties': {
                'id': { 'type': 'number', 'minimum': 1, },
                'url': { 'type': 'string', 'format': 'uri', },
                'created':  { 'type': 'string', 'format': 'date-time', },
                'modified': { 'type': 'string', 'format': 'date-time', },
                'name': { 'type': 'string', },
                'description': { 'type': 'string', },

                'user': { '$ref': '#/definitions/id_or_null', },
                'team': { '$ref': '#/definitions/id_or_null', },
                'project': { '$ref': '#/definitions/id_or_null', },
                'inventory': { '$ref': '#/definitions/id_or_null', },
                'permission_type': { '$ref': '#/definitions/enum_permission_type', },

                'related': {
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': {
                        'user': { 'type': 'string', 'format': 'uri', },
                        'team': { 'type': 'string', 'format': 'uri', },
                        'inventory': { 'type': 'string', 'format': 'uri', },
                        'project': { 'type': 'string', 'format': 'uri', },
                    },
                },
                'summary_fields': {
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': {
                        'user': { 'type': 'object', },
                        'team': { 'type': 'object', },
                        'inventory': { 'type': 'object', },
                        'project': { 'type': 'object', },
                    },
                },
            },
        }

    @property
    def get(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['count', 'next', 'previous', 'results', ],
            'additionalProperties': False,
            'properties': {
                'count': { 'type': 'number', 'minimum': 0, },
                'next': { 'type': ['string','null'], },
                'previous': { 'type': ['string','null'], },
                'results': {
                    'type': 'array',
                    'minItems': 0,
                    'uniqueItems': True,
                    'items': {
                        '$ref': '#/definitions/permission',
                    },
                },
            },
        })

    @property
    def post(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            '$ref': '#/definitions/permission',
        })
class Awx_Schema_Projects(Awx_Schema):
    component = '/projects'

    def __init__(self):
        super(Awx_Schema_Projects, self).__init__()

        self.definitions['project'] = {
            'type': 'object',
            'required': [ 'id', 'name', 'url', 'created', 'modified', 'last_updated', 'description', 'last_update_failed', 'status', 'summary_fields', 'local_path', 'scm_type', 'scm_url', 'scm_branch', 'scm_clean', 'scm_delete_on_update', 'scm_delete_on_next_update', 'scm_update_on_launch', 'credential', ],
            'additionalProperties': False,
            'properties': {
                'id': { 'type': 'number', 'minimum': 1, },
                'name': { 'type': 'string', },
                'url': { 'type': 'string', 'format': 'uri', },
                'created':  { 'type': 'string', 'format': 'date-time', },
                'modified': { 'type': 'string', 'format': 'date-time', },
                'last_updated': { 'type': ['string', 'null'], 'format': 'date-time', },
                'description': { 'type': 'string', },
                'last_update_failed': { 'type': 'boolean', },
                'status': { '$ref': '#/definitions/enum_project_status' },
                'summary_fields': { 'type': 'object', },
                'local_path': { 'type': 'string', 'format': 'uri', },
                'scm_type': { 'type': ['string', 'null',] },
                'scm_url': { 'type': 'string', },
                'scm_branch': { 'type': 'string', },
                'scm_clean': { 'type': 'boolean', },
                'scm_delete_on_update': { 'type': 'boolean', },
                'scm_delete_on_next_update': { 'type': 'boolean', },
                'scm_update_on_launch': { 'type': 'boolean', },
                'credential': { 'type': ['number','null'], },
                'related': {
                    'type': 'object',
                    'required': ['created_by', 'organizations', 'project_updates', 'playbooks', 'update', 'teams', 'activity_stream', ],
                    'additionalProperties': False,
                    'properties': {
                        'created_by':      { 'type': 'string', 'format': 'uri', },
                        'current_update':  { 'type': 'string', 'format': 'uri', },
                        'last_update':     { 'type': 'string', 'format': 'uri', },
                        'organizations':   { 'type': 'string', 'format': 'uri', },
                        'project_updates': { 'type': 'string', 'format': 'uri', },
                        'playbooks':       { 'type': 'string', 'format': 'uri', },
                        'update':          { 'type': 'string', 'format': 'uri', },
                        'teams':           { 'type': 'string', 'format': 'uri', },
                        'credential':      { 'type': 'string', 'format': 'uri', },
                        'activity_stream': { 'type': 'string', 'format': 'uri' },
                    },
                },
            },
        }

    @property
    def get(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['count', 'next', 'previous', 'results', ],
            'additionalProperties': False,
            'properties': {
                'count': { 'type': 'number', 'minimum': 0, },
                'next': { 'type': ['string','null'], },
                'previous': { 'type': ['string','null'], },
                'results': {
                    'type': 'array',
                    'minItems': 0,
                    'uniqueItems': True,
                    'items': {
                        '$ref': '#/definitions/project',
                    },
                },
            },
        })

    @property
    def post(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            '$ref': '#/definitions/project',
        })

    @property
    def duplicate(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'additionalProperties': False,
            'properties': {
                'local_path': {
                    'type': 'array',
                    'minItems': 0,
                    'uniqueItems': True,
                    'items': {
                        'type': 'string',
                        'pattern': '^Invalid path choice$',
                    },
                },
                'name': {
                    'type': 'array',
                    'minItems': 0,
                    'uniqueItems': True,
                    'items': {
                        'type': 'string',
                        'pattern': '^Project with this Name already exists.$',
                    },
                },
            },
        }

class Awx_Schema_Project_Organizations(Awx_Schema_Organizations):
    component = '/projects/\d+/organizations'

class Awx_Schema_Org_Projects(Awx_Schema_Projects):
    component = '/organizations/\d+/projects'

class Awx_Schema_Projects_Project_Updates(Awx_Schema):
    component = '/projects/\d+/project_updates'

    def __init__(self):
        super(Awx_Schema_Projects_Project_Updates, self).__init__()

        self.definitions['project_update'] = {
            'type': 'object',
            'required': [ 'id', 'url', 'created', 'modified', 'project', 'status', 'failed', 'result_stdout', 'result_traceback', 'job_args', 'job_cwd', 'job_env', 'related', 'summary_fields', ],
            'additionalProperties': False,
            'properties': {
                'id': { '$ref': '#/definitions/id', },
                'url': { 'type': 'string', 'format': 'uri', },
                'created':  { 'type': 'string', 'format': 'date-time', },
                'modified': { 'type': 'string', 'format': 'date-time', },
                'project': { '$ref': '#/definitions/id', },
                'status': { '$ref': '#/definitions/enum_project_update_status', },
                'failed': { 'type': 'boolean', },
                'result_stdout': { 'type': 'string', },
                'result_traceback': { 'type': 'string', },
                'job_args': {
                    'type': 'string',
                    #'type': 'array',
                    #'minItems': 0,
                    #'uniqueItems': False,
                },
                'job_cwd': { 'type': 'string', },
                'job_env': { '$ref': '#/definitions/job_env', },
                'related': {
                    'type': 'object',
                    'required': [ 'cancel', 'project'],
                    'additionalProperties': False,
                    'properties': {
                        "cancel": { 'type': 'string', 'format': 'uri' },
                        "project": { 'type': 'string', 'format': 'uri' },
                    },
                },
                'summary_fields':  {
                    'type': 'object',
                    'required': ['project', ],
                    'additionalProperties': False,
                    'properties': {
                        "project": {
                            '$ref': '#/definitions/summary_fields_project',
                        },
                    },
                },
            },
        }

    @property
    def get(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['count', 'next', 'previous', 'results', ],
            'additionalProperties': False,
            'properties': {
                'count': { 'type': 'number', 'minimum': 0, },
                'next': { 'type': ['string','null'], },
                'previous': { 'type': ['string','null'], },
                'results': {
                    'type': 'array',
                    'minItems': 0,
                    'uniqueItems': True,
                    'items': {
                        '$ref': '#/definitions/project_update',
                    },
                },
            },
        })

class Awx_Schema_Project_Update(Awx_Schema):
    component = '/projects/\d+/update'

    def __init__(self):
        super(Awx_Schema_Project_Update, self).__init__()

        self.definitions['project_update'] = {
            'type': 'object',
            'required': [ 'can_update', ],
            'additionalProperties': True,
            'properties': {
                'can_update': { 'type': 'boolean', },
                'passwords_needed_to_update': {
                    '$ref': '#/definitions/passwords_needed_to_start',
                },
            },
        }

    @property
    def get(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            '$ref': '#/definitions/project_update',
        })

    @property
    def post(self):
        return {}

class Awx_Schema_Project_Updates(Awx_Schema_Projects_Project_Updates):
    component = '/project_updates/\d+'

    @property
    def get(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            '$ref': '#/definitions/project_update',
        })

class Awx_Schema_Job_Templates(Awx_Schema):
    component = '/job_templates'

    def __init__(self):
        super(Awx_Schema_Job_Templates, self).__init__()

        self.definitions['job_template'] = {
            'type': 'object',
            'required': [ 'id', 'name', 'url', 'description', 'created', 'modified', 'job_type', 'inventory', 'project', 'playbook', 'credential', 'cloud_credential', 'forks', 'verbosity', 'limit', 'extra_vars', 'job_tags', 'host_config_key', 'related', 'summary_fields', ],
            'additionalProperties': False,
            'properties': {
                'id': { '$ref': '#/definitions/id', },
                'name': { 'type': 'string', },
                'url': { 'type': 'string', 'format': 'uri', },
                'description': { 'type': 'string', },
                'created':  { 'type': 'string', 'format': 'date-time', },
                'modified': { 'type': 'string', 'format': 'date-time', },
                'job_type': { 'enum': ['run', 'check'], },
                'inventory': { '$ref': '#/definitions/id', },
                'project': { '$ref': '#/definitions/id', },
                'playbook': { 'type': 'string', 'pattern': '.*\.(yaml|yml)' },
                'credential': { '$ref': '#/definitions/id', },
                'cloud_credential': { '$ref': '#/definitions/id_or_null', },
                'forks': { 'type': 'number', 'minimum': 0 },
                'verbosity': { 'type': 'number', 'minimum': 0 },
                'limit': { 'type': 'string', },
                'extra_vars': { 'type': 'string', },
                'job_tags': { 'type': 'string', },
                'host_config_key': { 'type': 'string', },
                'related': {
                    'type': 'object',
                    'required': [ 'created_by', 'project', 'jobs', 'inventory', 'credential', 'activity_stream', ],
                    'additionalProperties': False,
                    'properties': {
                        'created_by': { 'type': 'string', 'format': 'uri' },
                        'project': { 'type': 'string', 'format': 'uri' },
                        'jobs': { 'type': 'string', 'format': 'uri' },
                        'inventory': { 'type': 'string', 'format': 'uri' },
                        'credential': { 'type': 'string', 'format': 'uri' },
                        'cloud_credential': { 'type': 'string', 'format': 'uri' },
                        'activity_stream': { 'type': 'string', 'format': 'uri' },
                    },
                },
                'summary_fields':  {
                    'type': 'object',
                    'required': ['inventory', 'project', 'credential',],
                    'additionalProperties': False,
                    'properties': {
                        "inventory": {
                            '$ref': '#/definitions/summary_fields_inventory',
                        },
                        "project": {
                            '$ref': '#/definitions/summary_fields_project',
                        },
                        "credential": {
                            '$ref': '#/definitions/summary_fields_credential',
                        },
                    },
                },
            },
        }

    @property
    def get(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['count', 'next', 'previous', 'results', ],
            'additionalProperties': False,
            'properties': {
                'count': { 'type': 'number', 'minimum': 0, },
                'next': { 'type': ['string','null'], },
                'previous': { 'type': ['string','null'], },
                'results': {
                    'type': 'array',
                    'minItems': 0,
                    'uniqueItems': True,
                    'items': {
                        '$ref': '#/definitions/job_template',
                    },
                },
            },
        })

    @property
    def post(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            '$ref': '#/definitions/job_template',
        })

    @property
    def duplicate(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['name', ],
            'additionalProperties': False,
            'properties': {
                "name": {
                    'type': 'array',
                    'minItems': 0,
                    'uniqueItems': True,
                    'items': {
                        'type': 'string',
                        'pattern': '^Job template with this Name already exists.',
                    },
                },
            },
        }

class Awx_Schema_Jobs(Awx_Schema):
    component = '/jobs'

    def __init__(self):
        super(Awx_Schema_Jobs, self).__init__()

        self.definitions['job'] = {
            'type': 'object',
            'required': [ 'id', 'url', 'created', 'modified', 'job_type', 'inventory', 'project', 'playbook', 'credential', 'cloud_credential', 'forks', 'verbosity', 'limit', 'extra_vars', 'job_tags', 'job_template', 'launch_type', 'status', 'failed', 'result_stdout', 'result_traceback', 'passwords_needed_to_start', 'job_args', 'job_cwd', 'job_env', 'related', 'summary_fields', ],
            'additionalProperties': False,
            'properties': {
                'id': { '$ref': '#/definitions/id', },
                'url': { 'type': 'string', 'format': 'uri', },
                'created':  { 'type': 'string', 'format': 'date-time', },
                'modified': { 'type': 'string', 'format': 'date-time', },
                'job_type': { 'enum': ['run', 'check'], },
                'inventory': { '$ref': '#/definitions/id', },
                'project': { '$ref': '#/definitions/id', },
                'playbook': { 'type': 'string', 'pattern': '.*\.(yaml|yml)' },
                'credential': { '$ref': '#/definitions/id', },
                'cloud_credential': { '$ref': '#/definitions/id_or_null', },
                'forks': { 'type': 'number', 'minimum': 0 },
                'verbosity': { 'type': 'number', 'minimum': 0 },
                'limit': { 'type': 'string', },
                'extra_vars': { 'type': 'string', },
                'job_tags': { 'type': 'string', },
                'job_template': { '$ref': '#/definitions/id', },
                'launch_type': { '$ref': '#/definitions/enum_launch_type', },
                'status': { '$ref': '#/definitions/enum_launch_status', },
                'failed': { 'type': 'boolean', },
                'result_stdout': { 'type': 'string', },
                'result_traceback': { 'type': 'string', },
                'passwords_needed_to_start': { '$ref': '#/definitions/passwords_needed_to_start', },
                'job_args': { 'type': 'string', },
                'job_cwd': { 'type': 'string', },
                'job_env': { '$ref': '#/definitions/job_env', },
                'related': {
                    'type': 'object',
                    'required': [ 'project', 'job_host_summaries', 'credential', 'job_events', 'inventory', 'job_template', 'start', 'cancel', 'activity_stream', ],
                    'additionalProperties': False,
                    'properties': {
                        'created_by': { 'type': 'string', 'format': 'uri' },
                        'project': { 'type': 'string', 'format': 'uri', },
                        'job_host_summaries': { 'type': 'string', 'format': 'uri', },
                        'credential': { 'type': 'string', 'format': 'uri', },
                        'cloud_credential': { 'type': 'string', 'format': 'uri', },
                        'job_events': { 'type': 'string', 'format': 'uri', },
                        'inventory': { 'type': 'string', 'format': 'uri', },
                        'job_template': { 'type': 'string', 'format': 'uri', },
                        'start': { 'type': 'string', 'format': 'uri', },
                        'cancel': { 'type': 'string', 'format': 'uri', },
                        'activity_stream': { 'type': 'string', 'format': 'uri' },
                    },
                },
                'summary_fields':  {
                    'type': 'object',
                    'required': ['inventory', 'project', 'credential',],
                    'additionalProperties': False,
                    'properties': {
                        "inventory": {
                            '$ref': '#/definitions/summary_fields_inventory',
                        },
                        "project": {
                            '$ref': '#/definitions/summary_fields_project',
                        },
                        "credential": {
                            '$ref': '#/definitions/summary_fields_credential',
                        },
                        "job_template": {
                            '$ref': '#/definitions/summary_fields_job_template',
                        },
                    },
                },
            },
        }

    @property
    def get(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['count', 'next', 'previous', 'results', ],
            'additionalProperties': False,
            'properties': {
                'count': { 'type': 'number', 'minimum': 0, },
                'next': { 'type': ['string','null'], },
                'previous': { 'type': ['string','null'], },
                'results': {
                    'type': 'array',
                    'minItems': 0,
                    'uniqueItems': True,
                    'items': {
                        '$ref': '#/definitions/job',
                    },
                },
            },
        })

    @property
    def post(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            '$ref': '#/definitions/job',
        })


class Awx_Schema_Inventory_Sources(Awx_Schema):
    component = '/inventory_sources'

    def __init__(self):
        super(Awx_Schema_Inventory_Sources, self).__init__()

        self.definitions['inventory_source'] = {
            'type': 'object',
            'required': [ 'id', 'url', 'created', 'modified', 'inventory', 'group', 'overwrite', 'overwrite_vars', 'update_on_launch', 'last_updated', 'last_update_failed', 'status', 'update_interval', "source", "source_path", "source_vars", "credential", "source_regions", 'related', 'summary_fields', ],
            'additionalProperties': False,
            'properties': {
                'id': { '$ref': '#/definitions/id', },
                'url': { 'type': 'string', 'format': 'uri', },
                'created':  { 'type': 'string', 'format': 'date-time', },
                'modified': { 'type': 'string', 'format': 'date-time', },
                'inventory': { '$ref': '#/definitions/id', },
                'group': { '$ref': '#/definitions/id', },
                'overwrite': { 'type': 'boolean', },
                'overwrite_vars': { 'type': 'boolean', },
                'update_on_launch': { 'type': 'boolean', },
                'last_updated': { 'type': ['string', 'null'], 'format': 'date-time', },
                'last_update_failed': { 'type': 'boolean', },
                'status': { '$ref': '#/definitions/enum_inventory_status', },
                'update_interval': { 'type': 'number', 'minimum': 0 },
                "source": { 'type': 'string', },
                "source_path": { 'type': 'string', },
                "source_vars": { 'type': 'string', },
                'credential': { '$ref': '#/definitions/id_or_null', },
                "source_regions": { 'type': 'string', },
                'related': {
                    'type': 'object',
                    'required': [ 'inventory_updates', 'update', 'inventory', 'group', ],
                    'additionalProperties': True,
                    'properties': {
                        "created_by": { 'type': 'string', 'format': 'uri' },
                        "current_update": { 'type': 'string', 'format': 'uri' },
                        "last_update": { 'type': 'string', 'format': 'uri' },
                        "inventory_updates": { 'type': 'string', 'format': 'uri' },
                        "update": { 'type': 'string', 'format': 'uri' },
                        "inventory": { 'type': 'string', 'format': 'uri' },
                        "group": { 'type': 'string', 'format': 'uri' },
                    },
                },
                'summary_fields':  {
                    'type': 'object',
                    'required': ['inventory', 'group', ],
                    'additionalProperties': True,
                    'properties': {
                        "inventory": {
                            '$ref': '#/definitions/summary_fields_inventory',
                        },
                        "group": {
                            '$ref': '#/definitions/summary_fields_group',
                        },
                    },
                },
            },
        }

    @property
    def get(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['count', 'next', 'previous', 'results', ],
            'additionalProperties': False,
            'properties': {
                'count': { 'type': 'number', 'minimum': 0, },
                'next': { 'type': ['string','null'], },
                'previous': { 'type': ['string','null'], },
                'results': {
                    'type': 'array',
                    'minItems': 0,
                    'uniqueItems': True,
                    'items': {
                        '$ref': '#/definitions/inventory_source',
                    },
                },
            },
        })

    @property
    def patch(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            '$ref': '#/definitions/inventory_source',
        })

    @property
    def put(self):
        return self.patch

    @property
    def post(self):
        return self.patch

class Awx_Schema_Inventory_Sources_Update(Awx_Schema):
    component = '/inventory_sources/\d+/update'

    def __init__(self):
        super(Awx_Schema_Inventory_Sources_Update, self).__init__()

        self.definitions['inventory_source_update'] = {
            'type': 'object',
            'required': [ 'can_update', ],
            'additionalProperties': True,
            'properties': {
                'can_update': { 'type': 'boolean', },
                'passwords_needed_to_update': {
                    '$ref': '#/definitions/passwords_needed_to_start',
                },
            },
        }

    @property
    def get(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            '$ref': '#/definitions/inventory_source_update',
        })

    @property
    def post(self):
        return {}

class Awx_Schema_Inventory_Source_Updates(Awx_Schema):
    component = '/inventory_sources/\d+/inventory_updates'

    def __init__(self):
        super(Awx_Schema_Inventory_Source_Updates, self).__init__()

        self.definitions['inventory_update'] = {
            'type': 'object',
            'required': [ 'id', 'url', 'created', 'modified', 'inventory_source', 'status', 'failed', 'result_stdout', 'result_traceback', 'job_args', 'job_cwd', 'job_env', 'related', 'summary_fields', 'license_error', ],
            'additionalProperties': False,
            'properties': {
                'id': { '$ref': '#/definitions/id', },
                'url': { 'type': 'string', 'format': 'uri', },
                'created':  { 'type': 'string', 'format': 'date-time', },
                'modified': { 'type': 'string', 'format': 'date-time', },
                'inventory_source': { '$ref': '#/definitions/id', },
                'status': { '$ref': '#/definitions/enum_inventory_update_status', },
                'failed': { 'type': 'boolean', },
                'license_error': { 'type': 'boolean', },
                'result_stdout': { 'type': 'string', },
                'result_traceback': { 'type': 'string', },
                'job_args': {
                    'type': 'string',
                    #'type': 'array',
                    #'minItems': 0,
                    #'uniqueItems': False,
                },
                'job_cwd': { 'type': 'string', },
                'job_env': { '$ref': '#/definitions/job_env', },
                'related': {
                    'type': 'object',
                    'required': [ 'cancel', 'inventory_source'],
                    'additionalProperties': False,
                    'properties': {
                        "cancel": { 'type': 'string', 'format': 'uri' },
                        "inventory_source": { 'type': 'string', 'format': 'uri' },
                    },
                },
                'summary_fields':  {
                    'type': 'object',
                    'required': ['inventory_source', ],
                    'additionalProperties': False,
                    'properties': {
                        "inventory_source": {
                            '$ref': '#/definitions/summary_fields_inventory_source',
                        },
                    },
                },
            },
        }

    @property
    def get(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['count', 'next', 'previous', 'results', ],
            'additionalProperties': False,
            'properties': {
                'count': { 'type': 'number', 'minimum': 0, },
                'next': { 'type': ['string','null'], },
                'previous': { 'type': ['string','null'], },
                'results': {
                    'type': 'array',
                    'minItems': 0,
                    'uniqueItems': True,
                    'items': {
                        '$ref': '#/definitions/inventory_update',
                    },
                },
            },
        })

class Awx_Schema_Inventory_Source_Update(Awx_Schema_Inventory_Source_Updates):
    component = '/inventory_updates/\d+'

    @property
    def get(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            '$ref': '#/definitions/inventory_update',
        })

class Awx_Schema_Teams(Awx_Schema):
    component = '/teams'

    def __init__(self):
        super(Awx_Schema_Teams, self).__init__()

        self.definitions['team'] = {
            'type': 'object',
            'required': ['created', 'id', 'url', 'related', 'summary_fields', 'name', 'description', 'organization'],
            'additionalProperties': False,
            'properties': {
                'id': { 'type': 'number', 'minimum': 1, },
                'url': { 'type': 'string', 'format': 'uri'},
                'created':  { 'type': 'string', 'format': 'date-time', },
                'modified': { 'type': 'string', 'format': 'date-time', },
                'name': { 'type': 'string', },
                'description': { 'type': 'string', },
                'organization': { 'type': 'number', 'minimum': 1, },
                'related': {
                    'type': 'object',
                    'required': [ 'created_by', 'organization', 'permissions', 'users', 'projects', 'credentials', 'activity_stream', ],
                    'additionalProperties': False,
                    'properties': {
                        'created_by':   { 'type': 'string', 'format': 'uri' },
                        'organization': { 'type': 'string', 'format': 'uri' },
                        'permissions':  { 'type': 'string', 'format': 'uri' },
                        'users':        { 'type': 'string', 'format': 'uri' },
                        'projects':     { 'type': 'string', 'format': 'uri' },
                        'credentials':  { 'type': 'string', 'format': 'uri' },
                        'activity_stream': { 'type': 'string', 'format': 'uri' },
                    },
                },
                'summary_fields':  {
                    'type': 'object',
                    'required': ['organization'],
                    'additionalProperties': False,
                    'properties': {
                        'organization': {
                            'type': 'object',
                            'required': ['name', 'description'],
                            'additionalProperties': False,
                            'properties': {
                                'name':        { 'type': 'string', },
                                'description': { 'type': 'string', },
                            },
                        },
                    },
                },
            },
        }

    @property
    def duplicate(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': [ '__all__'],
            'additionalProperties': False,
            'properties': {
                "__all__": {
                    'type': 'array',
                    'minItems': 1,
                    'uniqueItems': True,
                    'items': {
                        'type': 'string',
                        'pattern': '^Team with this Organization and Name already exists.$',
                    },
                },
            },
        }

    @property
    def get(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['count', 'next', 'previous', 'results', ],
            'additionalProperties': False,
            'properties': {
                'count': { 'type': 'number', 'minimum': 0, },
                'next': { 'type': ['string','null'], },
                'previous': { 'type': ['string','null'], },
                'results': {
                    'type': 'array',
                    'minItems': 0,
                    'uniqueItems': True,
                    'items': {
                        '$ref': '#definitions/team',
                    },
                },
            },
        })

    @property
    def post(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            '$ref': '#/definitions/team',
        })

class Awx_Schema_Project_Teams(Awx_Schema_Teams):
    component = '/projects/\d+/teams'

class Awx_Schema_Config(Awx_Schema):
    component = '/config'

    def __init__(self):
        super(Awx_Schema_Config, self).__init__()

        self.definitions['config'] = {
            'type': 'object',
            'required': [ 'license_info', 'ansible_version', 'version', 'project_base_dir', 'time_zone', 'project_local_paths', ],
            'additionalProperties': False,
            'properties': {
                'license_info': {
                    'type': 'object',
                    'required': [ 'available_instances', 'current_instances', 'free_instances', ],
                    'additionalProperties': False,
                    'properties': {
                        'available_instances': { 'type': 'number', 'minimum': 0 },
                        'current_instances':   { 'type': 'number', 'minimum': 0 },
                        'free_instances':      { 'type': 'number', 'minimum': 0 },
                        'instance_count':      { 'type': 'number', 'minimum': 0 },
                        'license_date':        { 'type': 'number', 'minimum': 0 },
                        'time_remaining':      { 'type': 'number', 'minimum': 0 },
                        'license_key':         { 'type': 'string', },
                        'company_name':        { 'type': 'string', },
                        'compliant':           { 'type': 'boolean', },
                        'contact_email':       { 'type': 'string', },
                        'contact_name':        { 'type': 'string', },
                        'date_expired':        { 'type': 'boolean', },
                        'date_warning':        { 'type': 'boolean', },
                        'valid_key':           { 'type': 'boolean', },
                        'demo':                { 'type': 'boolean', },
                        'key_present':         { 'type': 'boolean', },
                    },
                },
                'ansible_version':  { 'type': 'string', 'pattern': '^(\d+\.)?(\d+\.)?(\d+)$'},
                'version':          { 'type': 'string', 'pattern': '^(\d+\.)?(\d+\.)?(\d+)(.*)$'},
                'project_base_dir': { 'type': 'string', 'minLength': 1, },
                'time_zone': { 'type': 'string', 'minLength': 1, },
                'project_local_paths': {
                    'type': 'array',
                    "items": {
                        "type": "string"
                    },
                    "minItems": 0,
                    "uniqueItems": True,
                },
            },
        }

    @property
    def get(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            '$ref': '#/definitions/config',
        })

class Awx_Schema_Me(Awx_Schema):
    component = '/me'

    @property
    def put(self):
        return {}

    @property
    def patch(self):
        return {}

    @property
    def post(self):
        return {}

    @property
    def get(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['count', 'next', 'previous', 'results', ],
            'additionalProperties': False,
            'properties': {
                'count': { 'type': 'number', 'minimum': 0, },
                'next': { 'type': ['string','null'], },
                'previous': { 'type': ['string','null'], },
                'results': {
                    'type': 'array',
                    'minItems': 1,
                    'maxItems': 1,
                    'uniqueItems': True,
                    'items': {
                        '$ref': '#definitions/user',
                    },
                },
            },
        })

class Awx_Schema_Authtoken(Awx_Schema):
    component = '/authtoken'

    @property
    def get(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'additionalProperties': False,
            'properties': {
                'detail': {
                    'type': 'string',
                    'pattern': "^Method '[A-Z]+' not allowed.$",
                },
            },
        })

    @property
    def put(self):
        return {}

    @property
    def patch(self):
        return {}

    @property
    def post(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'additionalProperties': False,
            'required': [ 'token', 'expires', ],
            'properties': {
                'token': { 'type': 'string', },
                'expires':  { 'type': 'string', 'format': 'date-time', },
            },
        })

class Awx_Schema_Dashboard(Awx_Schema):
    component = '/dashboard'

    def __init__(self):
        super(Awx_Schema_Dashboard, self).__init__()

        self.definitions['dashboard'] = {
            'type': 'object',
            'required': [ 'inventories', 'inventory_sources', 'groups', 'hosts', 'projects', 'scm_types', 'jobs', 'users', 'organizations', 'teams', 'credentials', 'job_templates', ],
            'additionalProperties': False,
            'properties': {
                'inventories': {
                    'type': 'object',
                    'required': [ 'url', 'inventory_failed', 'total', 'total_with_inventory_source', ],
                    'additionalProperties': False,
                    'properties': {
                        'url': { 'type': 'string', 'format': 'uri'},
                        'total': { 'type': 'number', 'minimum': 0, },
                        'inventory_failed': { 'type': 'number', 'minimum': 0, },
                        'total_with_inventory_source': { 'type': 'number', 'minimum': 0, },
                    }
                },
                'inventory_sources': {
                    'type': 'object',
                    'required': [ 'ec2', 'rax', ],
                    'additionalProperties': False,
                    'properties': {
                        'ec2': {
                            '$ref': '#/definitions/dashboard_inventory_sources',
                        },
                        'rax': {
                            '$ref': '#/definitions/dashboard_inventory_sources',
                        }
                    }
                },
                'groups': {
                    'type': 'object',
                    'required': [ 'url', 'total', 'failures_url', 'inventory_failed', 'job_failed', ],
                    'additionalProperties': False,
                    'properties': {
                        'url': { 'type': 'string', 'format': 'uri'},
                        'total': { 'type': 'number', 'minimum': 0, },
                        'failures_url': { 'type': 'string', 'format': 'uri'},
                        'inventory_failed': { 'type': 'number', 'minimum': 0, },
                        'job_failed': { 'type': 'number', 'minimum': 0, },
                    }
                },
                'hosts': {
                    'type': 'object',
                    'required': [ 'url', 'total', 'failures_url', 'failed', ],
                    'additionalProperties': False,
                    'properties': {
                        'url': { 'type': 'string', 'format': 'uri'},
                        'total': { 'type': 'number', 'minimum': 0, },
                        'failures_url': { 'type': 'string', 'format': 'uri'},
                        'failed': { 'type': 'number', 'minimum': 0, },
                    }
                },
                'projects': {
                    'type': 'object',
                    'required': [ 'url', 'total', 'failures_url', 'failed', ],
                    'additionalProperties': False,
                    'properties': {
                        'url': { 'type': 'string', 'format': 'uri'},
                        'total': { 'type': 'number', 'minimum': 0, },
                        'failures_url': { 'type': 'string', 'format': 'uri'},
                        'failed': { 'type': 'number', 'minimum': 0, },
                    }
                },
                'scm_types': {
                    'type': 'object',
                    'required': [ 'svn', 'git', 'hg', ],
                    'additionalProperties': False,
                    'properties': {
                        'svn': {
                            'type': 'object',
                            '$ref': '#/definitions/dashboard_scm_types',
                        },
                        'git': {
                            'type': 'object',
                            '$ref': '#/definitions/dashboard_scm_types',
                        },
                        'hg': {
                            'type': 'object',
                            '$ref': '#/definitions/dashboard_scm_types',
                        }
                    }
                },
                'jobs': {
                    'type': 'object',
                    'required': [ 'url', 'total', 'failure_url', 'failed', ],
                    'additionalProperties': False,
                    'properties': {
                        'url': { 'type': 'string', 'format': 'uri'},
                        'total': { 'type': 'number', 'minimum': 0, },
                        'failure_url': { 'type': 'string', 'format': 'uri'},
                        'failed': { 'type': 'number', 'minimum': 0, },
                    }
                },
                'users': {
                    '$ref': '#/definitions/dashboard_common_core',
                },
                'teams': {
                    '$ref': '#/definitions/dashboard_common_core',
                },
                'organizations': {
                    '$ref': '#/definitions/dashboard_common_core',
                },
                'credentials': {
                    '$ref': '#/definitions/dashboard_common_core',
                },
                'job_templates': {
                    '$ref': '#/definitions/dashboard_common_core',
                },
            }
        }

    @property
    def get(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            '$ref': '#/definitions/dashboard',
        })

class Awx_Schema_Activity_Stream(Awx_Schema):
    component = '/activity_stream'

    def __init__(self):
        super(Awx_Schema_Activity_Stream, self).__init__()

        self.definitions['activity_stream'] = {
            'type': 'object',
            'required': [ 'id', 'url', 'related', 'summary_fields', 'timestamp', 'operation', 'object1', 'object2', 'changes', ],
            'additionalProperties': False,
            'properties': {
                'id': { '$ref': '#/definitions/id', },
                'url': { 'type': 'string', 'format': 'uri'},
                'related': {
                    'type': 'object',
                    'required': [ 'actor', ],
                    'additionalProperties': True,
                    'properties': {
                        'actor': { 'type': 'string', 'format': 'uri'},
                    },
                },
                'summary_fields': {
                    'type': 'object',
                    'required': [ 'actor', ],
                    'additionalProperties': True,
                    'properties': {
                        'actor': {
                            'type': 'object',
                            'additionalProperties': True,
                        },
                    },
                },
                'timestamp':  { 'type': 'string', 'format': 'date-time', },
                'operation': { '$ref': '#/definitions/enum_activity_stream_operation', },
                'object1': { 'type': 'string', },
                'object2': { 'type': 'string', },
                'changes': {
                    'type': 'object',
                    'additionalProperties': True,
                },
            }
        }

    @property
    def get(self):
        return self.format_schema({
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['count', 'next', 'previous', 'results', ],
            'additionalProperties': False,
            'properties': {
                'count': { 'type': 'number', 'minimum': 0, },
                'next': { 'type': ['string','null'], },
                'previous': { 'type': ['string','null'], },
                'results': {
                    'type': 'array',
                    'minItems': 0,
                    'uniqueItems': True,
                    'items': {
                        '$ref': '#definitions/activity_stream',
                    },
                },
            },
        })

