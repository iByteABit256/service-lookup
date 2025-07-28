
"""
kubectl_service.py

Provides a KubectlService class that wraps kubectl commands\
for interacting with Kubernetes clusters.

This abstraction allows:
- Switching Kubernetes contexts
- Retrieving services from a namespace
- Port-forwarding services to localhost
"""

import subprocess
import threading
import json

class KubectlService:
    """
    A wrapper class for interacting with the Kubernetes CLI (kubectl) using a specified kubeconfig.

    This service provides higher-level methods to interact with Kubernetes clusters, such as:
    - Switching contexts
    - Retrieving services in a namespace
    - Port-forwarding services to localhost
    """

    def __init__(self, kubeconfig):
        """
        Initialize the KubectlService with a specific kubeconfig file.

        Args:
            kubeconfig (str or Path): Path to the kubeconfig file to use for kubectl commands.
        """
        self.kubeconfig = str(kubeconfig)

    def run_kubectl(self, args, capture_output=True, check=True, text=True):
        """
        Run a kubectl command with the given arguments.

        Args:
            args (list[str]): List of kubectl command arguments.
            capture_output (bool): Whether to capture stdout and stderr. Default is True.
            check (bool): Whether to raise an error if the command fails. Default is True.
            text (bool): Whether to decode output as text. Default is True.

        Returns:
            subprocess.CompletedProcess: Result of the kubectl subprocess.
        """
        cmd = ["kubectl", "--kubeconfig", self.kubeconfig] + args
        result = subprocess.run(cmd, capture_output=capture_output, check=check, text=text)
        return result

    def use_context(self, context):
        """
        Switch to the specified Kubernetes context.

        Args:
            context (str): The name of the Kubernetes context to switch to.
        """
        print(f"Switching context to '{context}' using kubeconfig '{self.kubeconfig}'\n")
        self.run_kubectl(["config", "use-context", context])

    def get_services(self, namespace):
        """
        Retrieve all services in the specified Kubernetes namespace.

        Args:
            namespace (str): The namespace from which to list services.

        Returns:
            dict: A dictionary representing the JSON output of the services list.
        """
        result = self.run_kubectl(["get", "services", "-n", namespace, "-o", "json"])
        return json.loads(result.stdout)

    def port_forward(self, namespace, service_name, local_port, target_port):
        """
        Port forward a Kubernetes service to the local machine.

        Args:
            namespace (str): The namespace where the service resides.
            service_name (str): The name of the Kubernetes service to forward.
            local_port (int): The local port to forward to.
            target_port (int): The target port of the Kubernetes service.

        Returns:
            process: Port forwarded process.
        """
        print(f"Port-forwarding service {service_name} from target port "
              f"{target_port} to local port {local_port}")

        process = subprocess.Popen(
            ["kubectl", "--kubeconfig", self.kubeconfig, "port-forward",
             f"service/{service_name}", f"{local_port}:{target_port}", "-n", namespace],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        # Wait until "Forwarding from" is shown in output
        def wait_for_ready():
            for line in process.stdout:
                print(f"[kubectl:{service_name}] {line.strip()}")
                if "Forwarding from" in line:
                    break

        wait_thread = threading.Thread(target=wait_for_ready)
        wait_thread.start()
        wait_thread.join(timeout=10)

        if wait_thread.is_alive():
            print(f"[!] Timeout: Port forward for {service_name} may not have started properly.")
        else:
            print(f"[✓] Port forward for {service_name} is ready.")

        return process
