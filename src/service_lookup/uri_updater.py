"""Updates URI properties found in YAML files under the given root"""

import re
from pathlib import Path
from ruamel.yaml import YAML

yaml = YAML()
yaml.preserve_quotes = True

def replace_host_port(url, new_host_port):
    """Replace only the host:port part in a URL, keeping the rest."""
    return re.sub(r"(http://)([^/]+)", rf"\1{new_host_port}", url)

def update_yaml_urls_by_key(file_path, replacements):
    """Update URI properties by service name"""
    with open(file_path, 'r', encoding="utf-8") as f:
        data = yaml.load(f)

    updated = set()

    if not isinstance(data, dict):
        return updated

    def recurse_dict(d):
        nonlocal updated

        if not isinstance(d, dict):
            return

        for key, value in d.items():
            # Service name is a parent property
            if isinstance(value, dict):
                for service, new_host_port in replacements.items():
                    if key == service and "url" in value and isinstance(value["url"], str):
                        old_url = value["url"]
                        new_url = replace_host_port(old_url, new_host_port)
                        if old_url != new_url:
                            value["url"] = new_url
                            updated.add(service)

            # Service name is a leaf property
            elif isinstance(value, str):
                for service, new_host_port in replacements.items():
                    if key == service:
                        old_url = value
                        new_url = replace_host_port(old_url, new_host_port)
                        if old_url != new_url:
                            d[key] = new_url
                            updated.add(service)
            recurse_dict(value)

    recurse_dict(data)

    if len(updated) > 0:
        with open(file_path, 'w', encoding="utf-8") as f:
            yaml.dump(data, f)
        print(f"✅ Updated: {file_path}")

    return updated

def update_directory(root_path: Path, replacements: dict[str, str], exclude_paths: list[str]):
    """Updates URI properties in YAML files under the root path"""

    exclude_paths = [Path(exclude).resolve() for exclude in exclude_paths]
    yaml_files = list(root_path.rglob("*.yml")) + list(root_path.rglob("*.yaml"))
    used_services = set()

    for file in yaml_files:
        if any(file.resolve().is_relative_to(exclude) for exclude in exclude_paths):
            print(f"❌ Skipped: {file} (excluded)")
            continue

        used_services = used_services.union(update_yaml_urls_by_key(file, replacements))

    print()
    return used_services
