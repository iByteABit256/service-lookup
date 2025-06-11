import subprocess
import json
import socket

def get_free_port():
    """Find an available port on the local machine."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))  # Bind to a free port provided by the host
        return s.getsockname()[1]

def load_service_mappings(mapping_file):
    """Load service mappings from a JSON file."""
    try:
        with open(mapping_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Mapping file {mapping_file} not found.")
        return {}
    except json.JSONDecodeError:
        print("Error decoding JSON mapping file.")
        return {}

def discover_services_and_port_forward(namespace, service_filter, service_mappings):
    try:
        # Execute the kubectl command to list services in the namespace
        result = subprocess.run(
            ["kubectl", "get", "services", "-n", namespace, "-o", "json"],
            capture_output=True,
            text=True,
            check=True
        )

        # Parse the JSON output
        services = json.loads(result.stdout)

        # Initialize replacements dictionary
        replacements = {}

        # Process each service
        for local_name in service_filter:
            k8s_service_name = service_mappings.get(local_name)

            if not k8s_service_name:
                print(f"No mapping found for local service name '{local_name}'.")
                continue

            # Find the corresponding Kubernetes service
            service = next((s for s in services.get("items", []) if s["metadata"]["name"] == k8s_service_name), None)

            if not service:
                print(f"Kubernetes service '{k8s_service_name}' not found.")
                continue

            ports = service.get("spec", {}).get("ports", [])
            if ports:
                # Choose the first port from the service spec
                target_port = ports[0]["port"]
                # Get a free local port
                local_port = get_free_port()
                replacements[local_name] = f"localhost:{local_port}"

                # Port forward the service
                print(f"Port-forwarding service {k8s_service_name} from target port {target_port} to local port {local_port}")
                subprocess.Popen(
                    ["kubectl", "port-forward", f"service/{k8s_service_name}", f"{local_port}:{target_port}", "-n", namespace],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )

        return replacements

    except subprocess.CalledProcessError as e:
        print(f"Error listing services: {e.stderr}")
        return {}
