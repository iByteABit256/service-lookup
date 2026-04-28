"""Driver for service-lookup utility"""

import argparse
from pathlib import Path

import keyboard

from .clean_processes import clean_ports
from .config import get_configuration
from .kubeconfig_setup import get_lens_kubeconfig_for_namespace
from .lookup_cluster import discover_services_and_port_forward, load_service_mappings
from .uri_updater import update_directory


def wait_for_user_command():
    """Wait for a specific user command to trigger cleanup."""

    print("Press 'ctrl+q' to clean ports and exit.")
    keyboard.wait('ctrl+q')
    print("Cleaning up ports and exiting...")

def main():
    """Driver for service-lookup utility"""
    parser = argparse.ArgumentParser(description="Update host:port in YAML service \
        URLs by service name and Kubernetes cluster")
    parser.add_argument('-k', '--kubeconfig', help="Specify kubeconfig file path")
    parser.add_argument('-l', '--use-lens', action='store_true',
        help="Search kubeconfigs from Lens")
    parser.add_argument('-r', '--root', help="Root directory to search YAML files, \
the default is the current directory", default=".")
    parser.add_argument('-e', '--exclude', help="Excluded paths in root directory")
    parser.add_argument('-m', '--map', help="Comma-separated service=host:port pairs")
    parser.add_argument('-c', '--cluster', help="Specify Kubernetes cluster, \
otherwise first matching namespace from any cluster will be used when using the --use-lens option")
    parser.add_argument('-n', '--namespace', help="Kubernetes namespace to discover services")
    parser.add_argument('-t', '--request-timeout', help="The length of time to wait before \
giving up on a single server request, default is 10s", default="10s")
    parser.add_argument('-s', '--services',
        help="Comma-separated list of service names to port forward. \
Default value is '*' which means every service in the mapping file", default="*")
    parser.add_argument('-f', '--mapping-file',
        default='service_mappings.json',
        help="Path to JSON file with service_name -> kubernetes_service_name mappings")
    args = parser.parse_args()

    configuration = get_configuration()

    if args.map:
        replacements = dict(pair.split('=') for pair in args.map.split(','))
    elif args.services and args.namespace:
        service_mappings = load_service_mappings(args.mapping_file)

        if args.services == "*":
            service_filter = list(service_mappings.keys())
            print(f"Searching all services from mapping file: {service_filter}\n")
        else:
            service_filter = args.services.split(',')

        kubeconfig = get_kubeconfig(args.use_lens, args.kubeconfig, args.namespace,
                                    args.request_timeout, args.cluster, configuration)

        replacements = discover_services_and_port_forward(
            args.namespace, service_filter, service_mappings, kubeconfig)
    else:
        print("Error: You must either provide a Kubernetes cluster namespace \
and selected services, or a service=host:port map.")
        return

    root_path = Path(args.root)
    exclude_paths = args.exclude.split(',') if args.exclude else []

    used_services = update_directory(root_path, replacements, exclude_paths)
    unused_services = set(replacements.keys()) - used_services

    print(f"The following port forwarded services were not used, \
they are going to be cleaned:\n{unused_services}\n")
    clean_ports([replacements[unused_service] for unused_service in unused_services])

    wait_for_user_command()

    print(f"Exiting and cleaning port forwarded services:\n{used_services}\n")
    clean_ports([replacements[used_service] for used_service in used_services])

def get_kubeconfig(use_lens, kubeconfig, namespace, request_timeout, cluster, configuration):
    """Gets the appropriate kubeconfig depending on the options given."""

    if use_lens or configuration.use_lens_by_default:
        return get_lens_kubeconfig_for_namespace(namespace, request_timeout, cluster)
    if kubeconfig is None:
        return Path.home() / ".kube" / "config"
    return kubeconfig

if __name__ == "__main__":
    main()
