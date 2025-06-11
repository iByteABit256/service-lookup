import argparse
from pathlib import Path
from .uri_updater import update_directory
from .lookup_cluster import discover_services_and_port_forward, load_service_mappings
from .kubeconfig_setup import run_setup
from .clean_processes import clean_ports

def main():
    parser = argparse.ArgumentParser(description="Update host:port in YAML service URLs by service name and Kubernetes cluster")
    parser.add_argument('-s', '--setup', action='store_true', help="Run setup to configure KUBECONFIG from Lens")
    parser.add_argument('-r', '--root', help="Root directory to search YAML files")
    parser.add_argument('-e', '--exclude', help="Excluded paths in root directory")
    parser.add_argument('-m', '--map', help="Comma-separated service=host:port pairs")
    parser.add_argument('-n', '--namespace', help="Kubernetes namespace to discover services")
    parser.add_argument('-v', '--services', help="Comma-separated list of service names to port forward")
    parser.add_argument('-f', '--mapping-file', default='service_mappings.json', help="Path to JSON file with service mappings")
    parser.add_argument('-c', '--clean', nargs='+', help="Specify ports to clean up port-forwarded processes")
    args = parser.parse_args()

    if args.setup:
        # Runs the KUBECONFIG setup process and then stops, nothing else should happen if other arguments are present
        run_setup()
        return

    if args.clean:
        clean_ports(args.clean)
        return

    if args.map:
        replacements = dict(pair.split('=') for pair in args.map.split(','))
    elif args.services and args.namespace:
        service_mappings = load_service_mappings(args.mapping_file)
        service_filter = args.services.split(',')
        replacements = discover_services_and_port_forward(args.namespace, service_filter, service_mappings)
    else:
        print("Error: You must either provide a Kubernetes cluster namespace and selected services, or a service=host:port map.")
        return

    if not args.root:
        print("Error: Root directory to be searched must be provided.")
        return

    root_path = Path(args.root)
    exclude_paths = args.exclude.split(',') if args.exclude else []

    update_directory(root_path, replacements, exclude_paths)

if __name__ == "__main__":
    main()
