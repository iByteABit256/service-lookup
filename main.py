import argparse
from pathlib import Path
from uri_updater import update_directory
from lookup_cluster import discover_services_and_port_forward, load_service_mappings
from kubeconfig_setup import generate_batch_file

def run_setup():
    # Generate the batch file
    batch_file_path = generate_batch_file()

    if batch_file_path:
        # Execute the batch file
        print("Executing generated script...")
        subprocess.run(batch_file_path, shell=True)
    else:
        print("Failed to create batch file.")

def main():
    parser = argparse.ArgumentParser(description="Update host:port in YAML service URLs by service name and Kubernetes cluster")
    parser.add_argument('-s', '--setup', action='store_true', help="Run setup to configure KUBECONFIG")
    parser.add_argument('-r', '--root', required=True, help="Root directory to search YAML files")
    parser.add_argument('-e', '--exclude', required=False, help="Excluded paths in root directory")
    parser.add_argument('-m', '--map', required=False, help="Comma-separated service=host:port pairs")
    parser.add_argument('-n', '--namespace', required=False, help="Kubernetes namespace to discover services")
    parser.add_argument('-v', '--services', required=False, help="Comma-separated list of service names to port forward")
    parser.add_argument('-f', '--mapping-file', default='service_mappings.json', help="Path to JSON file with service mappings")
    args = parser.parse_args()

    if args.setup:
        # Runs the KUBECONFIG setup process and then stops, nothing else should happen if other arguments are present
        run_setup()
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

    root_path = Path(args.root)
    exclude_paths = args.exclude.split(',') if args.exclude else []

    update_directory(root_path, replacements, exclude_paths)

if __name__ == "__main__":
    main()
