"""Looks up services in a Kubernetes cluster, and returns a map with the forwarded local ports"""

import json
import socket
import subprocess

from ruamel.yaml import YAML

from .kubectl_service import KubectlService

yaml = YAML()
yaml.preserve_quotes = True

def get_free_port():
    """Find an available port on the local machine."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))  # Bind to a free port provided by the host
        return s.getsockname()[1]

def load_service_mappings(mapping_file):
    """Load service mappings from a JSON file."""
    try:
        with open(mapping_file, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Mapping file '{mapping_file}' not found. "
            f"Check the --mapping-file argument or create the file."
        ) from e
    except json.JSONDecodeError as e:
        raise ValueError(f"Mapping file '{mapping_file}' contains invalid JSON.") from e

def get_context_from_kubeconfig(kubecfg):
    """Extract the context name from a kubeconfig file."""
    try:
        with open(kubecfg, encoding='utf-8') as f:
            config = yaml.load(f)
            current_context = config.get('current-context')
            if current_context:
                return current_context
            print("No current context found in the kubeconfig.")
            return None
    except OSError as e:
        print(f"Error reading kubeconfig {kubecfg}: {e}")
        return None

def port_forward_services(service_filter, service_mappings, services, namespace, kubectl):
    """Port forward services, return a [service_name, local_port] map"""

    replacements = {}

    for local_name in service_filter:
        k8s_service_name = service_mappings.get(local_name)
        service = next((s for s in services.get("items", [])
            if s["metadata"]["name"] == k8s_service_name), None)

        if service and k8s_service_name:
            ports = service.get("spec", {}).get("ports", [])
            if ports:
                local_port = get_free_port()
                replacements[local_name] = f"localhost:{local_port}"
                target_port = ports[0]["port"]

                kubectl.port_forward(namespace, k8s_service_name, local_port, target_port)
        else:
            print(f"No mapping found or service '{local_name}' not found in the namespace.")

        print()
    return replacements


def discover_services_and_port_forward(namespace, service_filter,
    service_mappings, kubecfg):

    """Looks up services in a Kubernetes cluster, returns a map with the forwarded local ports."""
    try:
        context_name = get_context_from_kubeconfig(kubecfg)
        if not context_name:
            print("Failed to determine context.")
            return {}

        kubectl = KubectlService(kubecfg)

        kubectl.use_context(context_name)

        services = kubectl.get_services(namespace)

        return port_forward_services(service_filter, service_mappings, services, namespace, kubectl)

    except subprocess.CalledProcessError as e:
        print(f"Error executing kubectl: {e.stderr}")
        return {}
