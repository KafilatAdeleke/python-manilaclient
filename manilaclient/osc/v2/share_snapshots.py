#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

import logging

from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from manilaclient import api_versions
from manilaclient.common._i18n import _
from manilaclient.common import cliutils

LOG = logging.getLogger(__name__)


class CreateShareSnapshot(command.ShowOne):
    """Create a share snapshot."""
    _description = _(
        "Create a snapshot of the given share")

    def get_parser(self, prog_name):
        parser = super(CreateShareSnapshot, self).get_parser(prog_name)
        parser.add_argument(
            "share",
            metavar="<share>",
            help=_("Name or ID of the share to create snapshot of")
        )
        parser.add_argument(
            "--force",
            action='store_true',
            default=False,
            help=_("Optional flag to indicate whether to snapshot "
                   "a share even if it's busy. (Default=False)")
        )
        parser.add_argument(
            "--name",
            metavar="<name>",
            default=None,
            help=_("Add a name to the snapshot (Optional).")
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            default=None,
            help=_("Add a description to the snapshot (Optional).")
        )
        return parser

    def take_action(self, parsed_args):
        share_client = self.app.client_manager.share

        share = utils.find_resource(share_client.shares,
                                    parsed_args.share)

        share_snapshot = share_client.share_snapshots.create(
            share=share,
            force=parsed_args.force,
            name=parsed_args.name or None,
            description=parsed_args.description or None
        )
        share_snapshot._info.pop('links', None)

        return self.dict2columns(share_snapshot._info)


class DeleteShareSnapshot(command.Command):
    """Delete one or more share snapshots"""
    _description = _(
        "Delete one or more share snapshots")

    def get_parser(self, prog_name):
        parser = super(DeleteShareSnapshot, self).get_parser(prog_name)
        parser.add_argument(
            "snapshot",
            metavar="<snapshot>",
            nargs="+",
            help=_("Name or ID of the snapshot(s) to delete")
        )
        parser.add_argument(
            "--force",
            action='store_true',
            default=False,
            help=_("Delete the snapshot(s) ignoring the current state.")
        )
        return parser

    def take_action(self, parsed_args):
        share_client = self.app.client_manager.share
        result = 0

        for snapshot in parsed_args.snapshot:
            try:
                snapshot_obj = utils.find_resource(
                    share_client.share_snapshots,
                    snapshot)
                if parsed_args.force:
                    share_client.share_snapshots.force_delete(
                        snapshot_obj)
                else:
                    share_client.share_snapshots.delete(
                        snapshot_obj)
            except Exception as e:
                result += 1
                LOG.error(_(
                    "Failed to delete snapshot with "
                    "name or ID '%(snapshot)s': %(e)s"),
                    {'snapshot': snapshot, 'e': e})

        if result > 0:
            total = len(parsed_args.snapshot)
            msg = (_("%(result)s of %(total)s snapshots failed "
                   "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ShowShareSnapshot(command.ShowOne):
    """Display a share snapshot"""
    _description = _(
        "Show details about a share snapshot")

    def get_parser(self, prog_name):
        parser = super(ShowShareSnapshot, self).get_parser(prog_name)
        parser.add_argument(
            "snapshot",
            metavar="<snapshot>",
            help=_("Name or ID of the snapshot to display")
        )
        return parser

    def take_action(self, parsed_args):
        share_client = self.app.client_manager.share

        share_snapshot = utils.find_resource(
            share_client.share_snapshots,
            parsed_args.snapshot)

        export_locations = (
            share_client.share_snapshot_export_locations.list(
                share_snapshot))
        export_locations = (
            cliutils.transform_export_locations_to_string_view(
                export_locations))

        data = share_snapshot._info
        data['export_locations'] = export_locations
        data.pop('links', None)

        return self.dict2columns(data)


class SetShareSnapshot(command.Command):
    """Set share snapshot properties."""
    _description = _("Set share snapshot properties")

    def get_parser(self, prog_name):
        parser = super(SetShareSnapshot, self).get_parser(prog_name)
        parser.add_argument(
            "snapshot",
            metavar="<snapshot>",
            help=_('Name or ID of the snapshot to set a property for')
        )
        parser.add_argument(
            "--name",
            metavar="<name>",
            default=None,
            help=_("Set a name to the snapshot.")
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            default=None,
            help=_("Set a description to the snapshot.")
        )
        parser.add_argument(
            "--status",
            metavar="<status>",
            choices=['available', 'error', 'creating', 'deleting',
                     'manage_starting', 'manage_error',
                     'unmanage_starting', 'unmanage_error',
                     'error_deleting'],
            help=_("Assign a status to the snapshot (Admin only). "
                   "Options include : available, error, creating, "
                   "deleting, manage_starting, manage_error, "
                   "unmanage_starting, unmanage_error, error_deleting.")
        )
        return parser

    def take_action(self, parsed_args):
        share_client = self.app.client_manager.share
        result = 0

        share_snapshot = utils.find_resource(
            share_client.share_snapshots,
            parsed_args.snapshot)

        kwargs = {}

        if parsed_args.name is not None:
            kwargs['display_name'] = parsed_args.name
        if parsed_args.description is not None:
            kwargs['display_description'] = parsed_args.description

        try:
            share_client.share_snapshots.update(
                share_snapshot,
                **kwargs
            )
        except Exception as e:
            result += 1
            LOG.error(_(
                "Failed to set share snapshot properties "
                "'%(properties)s': %(exception)s"),
                {'properties': kwargs,
                 'exception': e})

        if parsed_args.status:
            try:
                share_client.share_snapshots.reset_state(
                    share_snapshot,
                    parsed_args.status
                )
            except Exception as e:
                result += 1
                LOG.error(_(
                    "Failed to update snapshot status to "
                    "'%(status)s': %(e)s"),
                    {'status': parsed_args.status, 'e': e})

        if result > 0:
            raise exceptions.CommandError(_("One or more of the "
                                          "set operations failed"))


class UnsetShareSnapshot(command.Command):
    """Unset a share snapshot property."""
    _description = _("Unset a share snapshot property")

    def get_parser(self, prog_name):
        parser = super(UnsetShareSnapshot, self).get_parser(prog_name)
        parser.add_argument(
            "snapshot",
            metavar="<snapshot>",
            help=_("Name or ID of the snapshot to set a property for")
        )
        parser.add_argument(
            "--name",
            action='store_true',
            help=_("Unset snapshot name."),
        )
        parser.add_argument(
            "--description",
            action='store_true',
            help=_("Unset snapshot description."),
        )
        return parser

    def take_action(self, parsed_args):
        share_client = self.app.client_manager.share

        share_snapshot = utils.find_resource(
            share_client.share_snapshots,
            parsed_args.snapshot)

        kwargs = {}
        if parsed_args.name:
            kwargs['display_name'] = None
        if parsed_args.description:
            kwargs['display_description'] = None
        if kwargs:
            try:
                share_client.share_snapshots.update(
                    share_snapshot,
                    **kwargs
                )
            except Exception as e:
                raise exceptions.CommandError(_(
                    "Failed to unset snapshot display name "
                    "or display description : %s" % e))


class ListShareSnapshot(command.Lister):
    """List snapshots."""
    _description = _("List snapshots")

    def get_parser(self, prog_name):
        parser = super(ListShareSnapshot, self).get_parser(prog_name)
        parser.add_argument(
            "--all-projects",
            action='store_true',
            default=False,
            help=_("Display snapshots from all projects (Admin only).")
        )
        parser.add_argument(
            "--name",
            metavar="<name>",
            default=None,
            help=_("Filter results by name.")
        )
        parser.add_argument(
            '--description',
            metavar="<description>",
            default=None,
            help=_("Filter results by description. Available only for "
                   "microversion >= 2.36.")
        )
        parser.add_argument(
            '--status',
            metavar="<status>",
            default=None,
            help=_('Filter results by status')
        )
        parser.add_argument(
            '--share',
            metavar='<share>',
            default=None,
            help=_('Name or ID of a share to filter results by.')
        )
        parser.add_argument(
            '--usage',
            metavar='<usage>',
            default=None,
            choices=['used', 'unused'],
            help=_("Option to filter snapshots by usage.")
        )
        parser.add_argument(
            "--limit",
            metavar="<num-snapshots>",
            type=int,
            default=None,
            action=parseractions.NonNegativeAction,
            help=_("Limit the number of snapshots returned")
        )
        parser.add_argument(
            "--marker",
            metavar="<snapshot>",
            help=_("The last share ID of the previous page")
        )
        parser.add_argument(
            '--sort',
            metavar="<key>[:<direction>]",
            default='name:asc',
            help=_("Sort output by selected keys and directions(asc or desc) "
                   "(default: name:asc), multiple keys and directions can be "
                   "specified separated by comma")
        )
        parser.add_argument(
            "--name~",
            metavar="<name~>",
            default=None,
            help=_("Filter results matching a share snapshot name pattern. "
                   "Available only for microversion >= 2.36.")
        )
        parser.add_argument(
            '--description~',
            metavar="<description~>",
            default=None,
            help=_("Filter results matching a share snapshot description "
                   "pattern. Available only for microversion >= 2.36.")
        )
        parser.add_argument(
            '--detail',
            action='store_true',
            default=False,
            help=_("List share snapshots with details")
        )
        return parser

    def take_action(self, parsed_args):
        share_client = self.app.client_manager.share

        share_id = None
        if parsed_args.share:
            share_id = utils.find_resource(share_client.shares,
                                           parsed_args.share).id
        columns = ['ID', 'Name']

        search_opts = {
            'offset': parsed_args.marker,
            'limit': parsed_args.limit,
            'all_tenants': parsed_args.all_projects,
            'name': parsed_args.name,
            'status': parsed_args.status,
            'share_id': share_id,
            'usage': parsed_args.usage,
        }

        if share_client.api_version >= api_versions.APIVersion("2.36"):
            search_opts['name~'] = getattr(parsed_args, 'name~')
            search_opts['description~'] = getattr(parsed_args, 'description~')
            search_opts['description'] = parsed_args.description
        elif (parsed_args.description or getattr(parsed_args, 'name~') or
              getattr(parsed_args, 'description~')):
            raise exceptions.CommandError(
                "Pattern based filtering (name~, description~ and description)"
                " is only available with manila API version >= 2.36")

        if parsed_args.detail:
            columns.extend([
                'Status',
                'Description',
                'Created At',
                'Size',
                'Share ID',
                'Share Proto',
                'Share Size',
                'User ID'
            ])

        if parsed_args.all_projects:
            columns.append('Project ID')
        snapshots = share_client.share_snapshots.list(search_opts=search_opts)

        snapshots = utils.sort_items(snapshots, parsed_args.sort, str)

        return (columns,
                (utils.get_item_properties(s, columns) for s in snapshots))