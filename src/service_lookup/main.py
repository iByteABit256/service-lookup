"""Driver for service-lookup utility"""

import argparse
import time
from pathlib import Path
import keyboard
from .uri_updater import update_directory
from .lookup_cluster import discover_services_and_port_forward, load_service_mappings
from .kubeconfig_setup import get_kubeconfigs
from .clean_processes import clean_ports

def wait_for_user_command():
    """Wait for a specific user command to trigger cleanup."""

    print("Press 'ctrl+q' to clean ports and exit.")
    keyboard.wait('ctrl+q')
    print("Cleaning up ports and exiting...")

def main():
    """Driver for service-lookup utility"""
    parser = argparse.ArgumentParser(description="Update host:port in YAML service \
        URLs by service name and Kubernetes cluster")
    parser.add_argument('-l', '--use-lens', action='store_true',
        help="Search kubeconfigs from Lens")
    parser.add_argument('-r', '--root', help="Root directory to search YAML files")
    parser.add_argument('-e', '--exclude', help="Excluded paths in root directory")
    parser.add_argument('-m', '--map', help="Comma-separated service=host:port pairs")
    parser.add_argument('-n', '--namespace', help="Kubernetes namespace to discover services")
    parser.add_argument('-s', '--services',
        help="Comma-separated list of service names to port forward. \
Default value is '*' which means every service in the mapping file", default="*")
    parser.add_argument('-f', '--mapping-file',
        default='service_mappings.json',
        help="Path to JSON file with service_name -> kubernetes_service_name mappings")
    args = parser.parse_args()

    if args.map:
        replacements = dict(pair.split('=') for pair in args.map.split(','))
    elif args.services and args.namespace:
        service_mappings = load_service_mappings(args.mapping_file)

        if args.services == "*":
            service_filter = list(service_mappings.keys())
            print(f"Searching all services from mapping file: {service_filter}\n")
        else:
            service_filter = args.services.split(',')

        replacements = discover_services_and_port_forward(
            args.namespace, service_filter, service_mappings, args.kubeconfig
        )
    else:
        print("Error: You must either provide a Kubernetes cluster namespace \
and selected services, or a service=host:port map.")
        return

    if not args.root:
        print("Error: Root directory to be searched must be provided.")
        return

    root_path = Path(args.root)
    exclude_paths = args.exclude.split(',') if args.exclude else []

    used_services = update_directory(root_path, replacements, exclude_paths)
    unused_services = set(replacements.keys()) - used_services

    time.sleep(1) # Waits for the port forwarded service to start before killing it
    print(f"The following port forwarded services were not used, \
they are going to be cleaned:\n{unused_services}\n")
    clean_ports([replacements[unused_service] for unused_service in unused_services])

    wait_for_user_command()

    print(f"Exiting and cleaning port forwarded services:\n{used_services}\n")
    clean_ports([replacements[used_service] for used_service in used_services])

if __name__ == "__main__":
    main()
