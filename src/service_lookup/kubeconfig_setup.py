""" Finds Lens kubeconfig by namespace and cluster """

import json
import os
import time
from pathlib import Path

from ruamel.yaml import YAML

from .kubectl_service import KubectlService

yaml = YAML()
yaml.preserve_quotes = True

def update_namespace_cache(cache_file, data):
    with open(cache_file, 'w') as namespace_json:
        json.dump(data, namespace_json)

def get_lens_kubeconfig_for_namespace(namespace, request_timeout, cache_invalidation_seconds,
                                      invalidate_cache, cluster=None):
    """Find the Lens kubeconfig file for a given namespace.

    A specific cluster name can be given, otherwise the first match will be returned.
    """

    lens_kubeconfigs_dir = Path.home() / "AppData" / "Roaming" / "Lens" / "kubeconfigs" \
        if os.name == 'nt' else Path.home() / ".lens" / "kubeconfigs"

    if not lens_kubeconfigs_dir.exists():
        print("Lens kubeconfigs directory not found. Ensure Lens is installed and configured.")
        return None

    kubeconfig_files = list(lens_kubeconfigs_dir.glob('*'))
    if not kubeconfig_files:
        print("No kubeconfig files found in the Lens directory.")
        return None

    cache_file = Path.home() / ".cache" / "service-lookup" / "namespaces.yaml"
    cache_updated = False
    if not cache_file.exists():
        cache_file.parent.mkdir(exist_ok=True, parents=True)
        update_namespace_cache(cache_file, dict())

    with open(cache_file) as namespace_json:
        data = json.load(namespace_json)

    cache_age = os.stat(cache_file).st_mtime
    if invalidate_cache or cache_age < time.time() - cache_invalidation_seconds:
        data = dict()

    for kubeconfig_file in kubeconfig_files:
        try:
            with open(kubeconfig_file, encoding="utf-8") as f:
                kubeconfig_data = yaml.load(f)

            print(f"Checking kubeconfig: '{kubeconfig_file}'...")

            kubectl = KubectlService(kubeconfig_file)

            for context in kubeconfig_data.get('contexts', []):
                cluster_curr = context.get('context', {}).get('cluster')

                # Skip unnecessary check if specific cluster was given
                if cluster is not None and cluster_curr != cluster:
                    continue

                if str(kubeconfig_file) in data:
                    namespaces = data[str(kubeconfig_file)]
                else:
                    namespaces = kubectl.get_namespaces(context.get('name'), request_timeout)
                    data[str(kubeconfig_file)] = namespaces
                    cache_updated = True

                if namespaces is None:
                    continue

                found_namespace = next((ns for ns in namespaces.get('items')
                    if namespace_matches(namespace, ns.get('metadata').get('name'))), None)

                if found_namespace is not None:
                    if cache_updated:
                        update_namespace_cache(cache_file, data)
                    return str(kubeconfig_file)
        except OSError as e:
            print(f"Error reading {kubeconfig_file}: {e}")

    if cache_updated:
        update_namespace_cache(cache_file, data)
    print(f"Error: No matching kubeconfig found for namespace '{namespace}'.")
    print(f"Warning: Using '{kubeconfig_files[0]}' as a fallback.")
    return kubeconfig_files[0]

def namespace_matches(namespace, actual_namespace):
    """Matches input namespace with the ones found from the cluster.

    It also matches namespaces with an added suffix separated with . or -
    """
    return namespace in actual_namespace.split('.') or namespace in actual_namespace.split('-')
