from manilaclient import client
from manilaclient.v1 import limits
from manilaclient.v1 import quota_classes
from manilaclient.v1 import quotas
from manilaclient.v1 import shares
from manilaclient.v1 import share_snapshots


class Client(object):
    """Top-level object to access the OpenStack Volume API.

    Create an instance with your creds::

        >>> client = Client(USERNAME, PASSWORD, PROJECT_ID, AUTH_URL)

    Then call methods on its managers::

        >>> client.share.list()
        ...
    """

    def __init__(self, username, api_key, project_id=None, auth_url='',
                 insecure=False, timeout=None, tenant_id=None,
                 proxy_tenant_id=None, proxy_token=None, region_name=None,
                 endpoint_type='publicURL', extensions=None,
                 service_type='share', service_name=None,
                 share_service_name=None, retries=None,
                 http_log_debug=False,
                 cacert=None):
        # FIXME(comstud): Rename the api_key argument above when we
        # know it's not being used as keyword argument
        password = api_key
        self.limits = limits.LimitsManager(self)

        self.quota_classes = quota_classes.QuotaClassSetManager(self)
        self.quotas = quotas.QuotaSetManager(self)

        self.shares = shares.ShareManager(self)
        self.share_snapshots = share_snapshots.ShareSnapshotManager(self)

        # Add in any extensions...
        if extensions:
            for extension in extensions:
                if extension.manager_class:
                    setattr(self, extension.name,
                            extension.manager_class(self))

        self.client = client.HTTPClient(
            username,
            password,
            project_id,
            auth_url,
            insecure=insecure,
            timeout=timeout,
            tenant_id=tenant_id,
            proxy_token=proxy_token,
            proxy_tenant_id=proxy_tenant_id,
            region_name=region_name,
            endpoint_type=endpoint_type,
            service_type=service_type,
            service_name=service_name,
            share_service_name=share_service_name,
            retries=retries,
            http_log_debug=http_log_debug,
            cacert=cacert)

    def authenticate(self):
        """Authenticate against the server.

        Normally this is called automatically when you first access the API,
        but you can call this method to force authentication right now.

        Returns on success; raises :exc:`exceptions.Unauthorized` if the
        credentials are wrong.
        """
        self.client.authenticate()
