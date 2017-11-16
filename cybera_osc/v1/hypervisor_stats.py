import json
import logging
import os
import time
import cybera_utils

from osc_lib import utils
from osc_lib.command import command
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)
class CliHypervisorStats(command.Command):
    _description = _("Display stats about a hypervisor")

    def get_parser(self, prog_name):
        parser = super(CliHypervisorStats, self).get_parser(prog_name)
        parser.add_argument(
            '--hypervisor',
            metavar='<hypervisor>',
            required=False,
            help=_('Only display on specific hypervisors')
        )
        parser.add_argument(
            '--format',
            metavar='<format>',
            required=True,
            default='json',
            help=_('Format of the output (JSON or graphite)')
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        if parsed_args.hypervisor:
            hypervisors = compute_client.hypervisors.search(parsed_args.hypervisor)
        else:
            hypervisors = compute_client.hypervisors.list()

        report = {}
        wanted_stats = ["free_disk_gb", "local_gb", "free_ram_mb", "memory_mb_used",
                        "memory_mb", "vcpus", "vcpus_used", "running_vms", "current_workload"]
        for h in hypervisors:
            stats = utils.find_resource(compute_client.hypervisors,
                                        h.id)._info.copy()

            v = {}
            for w in wanted_stats:
                v[w] = stats[w]

            report[stats["hypervisor_hostname"]] = v

        if parsed_args.format == "graphite":
            t = int(time.time())
            for h, s in report.iteritems():
                for k, v in s.iteritems():
                    print "%s.hypervisor_stats.%s %s %s" % (h, k, v, t)
        if parsed_args.format == "json":
            print json.dumps(report)
