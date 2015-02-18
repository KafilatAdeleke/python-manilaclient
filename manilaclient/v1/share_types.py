# Copyright (c) 2011 Rackspace US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
Share Type interface.
"""

from manilaclient import base
from manilaclient.openstack.common.apiclient import base as common_base


class ShareType(common_base.Resource):
    """A Share Type is the type of share to be created."""

    def __repr__(self):
        return "<ShareType: %s>" % self.name

    def get_keys(self):
        """Get extra specs from a share type.

        :param share_type: The :class:`ShareType` to get extra specs from
        """
        _resp, body = self.manager.api.client.get(
            "/types/%s/extra_specs" % common_base.getid(self))
        return body["extra_specs"]

    def set_keys(self, metadata):
        """Set extra specs on a share type.

        :param type : The :class:`ShareType` to set extra spec on
        :param metadata: A dict of key/value pairs to be set
        """
        body = {'extra_specs': metadata}
        return self.manager._create(
            "/types/%s/extra_specs" % common_base.getid(self),
            body,
            "extra_specs",
            return_raw=True,
        )

    def unset_keys(self, keys):
        """Unset extra specs on a share type.

        :param type_id: The :class:`ShareType` to unset extra spec on
        :param keys: A list of keys to be unset
        """

        # NOTE(jdg): This wasn't actually doing all of the keys before
        # the return in the loop resulted in ony ONE key being unset.
        # since on success the return was NONE, we'll only interrupt the loop
        # and return if there's an error
        resp = None
        for k in keys:
            resp = self.manager._delete(
                "/types/%s/extra_specs/%s" % (common_base.getid(self), k))
            if resp is not None:
                return resp


class ShareTypeManager(base.ManagerWithFind):
    """Manage :class:`ShareType` resources."""

    resource_class = ShareType

    def list(self, search_opts=None):
        """Get a list of all share types.

        :rtype: list of :class:`ShareType`.
        """
        return self._list("/types", "share_types")

    def get(self, share_type):
        """Get a specific share type.

        :param share_type: The ID of the :class:`ShareType` to get.
        :rtype: :class:`ShareType`
        """
        return self._get("/types/%s" % common_base.getid(share_type),
                         "share_type")

    def delete(self, share_type):
        """Delete a specific share_type.

        :param share_type: The name or ID of the :class:`ShareType` to get.
        """
        self._delete("/types/%s" % common_base.getid(share_type))

    def create(self, name):
        """Create a share type.

        :param name: Descriptive name of the share type
        :rtype: :class:`ShareType`
        """

        body = {
            "share_type": {
                "name": name,
            }
        }

        return self._create("/types", body, "share_type")
