"""OpenStackClient plugin for Cybera."""

from osc_lib import utils

DEFAULT_API_VERSION = '1'
API_VERSION_OPTION = 'os_cybera_api_version'
API_NAME = "cybera"
API_VERSIONS = {
    "1": "cybera_osc.v1.client.Client",
}


def make_client(instance):
    pass

def build_option_parser(parser):
    """Hook to add global options."""
    parser.add_argument(
        '--os-cybera-api-version',
        metavar='<cybera-api-version>',
        default=utils.env(
            'OS_CYBERA_API_VERSION',
            default=DEFAULT_API_VERSION),
        help=('Cybera API version, default=' +
              DEFAULT_API_VERSION +
              ' (Env: OS_CYBERA_API_VERSION)'))
    return parser

