# Copyright 2014 OpenStack Foundation.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import urllib

from manilaclient import base

RESOURCES_PATH = '/share-servers'
RESOURCES_NAME = 'share_servers'
RESOURCE_NAME = 'share_server'


class ShareServer(base.Resource):

    def __repr__(self):
        return "<ShareServer: %s>" % self.id

    def __getattr__(self, attr):
        if attr == 'share_network':
            return getattr(self, 'share_network_name')
        return getattr(self, attr)


class ShareServerManager(base.Manager):
    """Manage :class:`ShareServer` resources."""
    resource_class = ShareServer

    def get(self, server_id):
        """Get a share server.

        :param server_id: The ID of the share server to get.
        :rtype: :class:`ShareServer`
        """
        server = self._get("%s/%s" % (RESOURCES_PATH, server_id),
                           RESOURCE_NAME)
        # Split big dict 'backend_details' to separated strings
        # as next:
        # +---------------------+------------------------------------+
        # |       Property      |                Value               |
        # +---------------------+------------------------------------+
        # | details:instance_id |35203a78-c733-4b1f-b82c-faded312e537|
        # +---------------------+------------------------------------+
        for k, v in server._info["backend_details"].iteritems():
            server._info["details:%s" % k] = v
        return server

    def details(self, server_id):
        """Get a share server details.
        :param server_id: The ID of the share server to get details from.
        :rtype: list of :class:`ShareServerBackendDetails
        """
        return self._get("%s/%s/details" % (RESOURCES_PATH, server_id),
                         "details")

    def list(self, search_opts=None):
        """Get a list of share servers.

        :rtype: list of :class:`ShareServer`
        """
        query_string = ''
        if search_opts:
            opts = [(k, v) for (k, v) in search_opts.items() if v]
            query_string = urllib.urlencode(opts)
            query_string = '?' + query_string if query_string else ''
        return self._list(RESOURCES_PATH + query_string, RESOURCES_NAME)
