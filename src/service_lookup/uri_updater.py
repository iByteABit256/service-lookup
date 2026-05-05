"""Updates URI properties found in YAML files under the given root"""

import os
import re
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile

from ruamel.yaml import YAML

yaml = YAML()
yaml.preserve_quotes = True

def replace_host_port(url, new_host_port):
    """Replace only the host:port part in a URL, keeping the rest."""
    return re.sub(r"(http://)([^/]+)", rf"\1{new_host_port}", url)

def restore_files(cached_files):
    """Restores all updated files and deletes the temp files"""
    for file_path, cached_file_path in cached_files.items():
        print(f"Reverting {file_path}...")
        shutil.copy(cached_file_path, file_path)
        os.remove(cached_file_path)
        print("ok.\n")

def cache_yaml(file_path):
    """Creates a temp file for the files about to be changed so they can be reverted after cleanup"""
    with NamedTemporaryFile(prefix=f"temp-{Path(file_path).stem}-",
                                   suffix=Path(file_path).suffix,
                                   delete=False) as temp_file:
        cache_file_path = temp_file.name
        shutil.copy(file_path, cache_file_path)
    return cache_file_path

def should_update_url(key, value, service):
    """Check if this key-value pair should have its URL updated"""
    if key != service:
        return False

    # Parent property case
    if isinstance(value, dict) and "url" in value and isinstance(value["url"], str):
        return True

    # Leaf property case
    return isinstance(value, str)

def update_dict_url(value_dict, new_host_port):
    """Update URL in a dictionary. Returns True if updated, False otherwise."""
    if not isinstance(value_dict, dict) or "url" not in value_dict:
        return False
    old_url = value_dict["url"]
    new_url = replace_host_port(old_url, new_host_port)
    if old_url != new_url:
        value_dict["url"] = new_url
        return True
    return False

def update_string_url(value_str, new_host_port):
    """Update URL string. Returns new string or original if unchanged."""
    if not isinstance(value_str, str):
        return None
    old_url = value_str
    new_url = replace_host_port(old_url, new_host_port)
    return new_url if old_url != new_url else value_str

def apply_url_update(value, new_host_port):
    """Apply the URL update to either a dict or string value."""
    if isinstance(value, dict):
        return update_dict_url(value, new_host_port)
    if isinstance(value, str):
        return update_string_url(value, new_host_port)
    return False

def recurse_dict(d, replacements, updated):
    """Recursively traverse dictionary and update URLs"""
    if not isinstance(d, dict):
        return

    for key, value in d.items():
        for service, new_host_port in replacements.items():
            if should_update_url(key, value, service):
                result = apply_url_update(value, new_host_port)
                if result is True: # Updated dict
                    updated.add(service)
                elif result != value: # Updated string
                    d[key] = result
                    updated.add(service)

        # Always recurse into nested structures
        recurse_dict(value, replacements, updated)

def update_yaml_urls_by_key(file_path, replacements, restore_files_flag):
    """Update URI properties by service name"""
    with open(file_path, encoding="utf-8") as f:
        try:
            data = yaml.load(f)
        except Exception as e:
            print(f"Skipping {file_path}: could not parse YAML ({e})")
            return (set(), None)

    updated = set()
    cached_file_path = None

    if isinstance(data, dict):
        recurse_dict(data, replacements, updated)

        if updated:
            if restore_files_flag:
                cached_file_path = cache_yaml(file_path)
            with open(file_path, 'w', encoding="utf-8") as f:
                yaml.dump(data, f)
            print(f" Updated: {file_path}")

    return (updated, cached_file_path)

def update_directory(root_path: Path, replacements: dict[str, str], exclude_paths: list[str], restore_files: bool):
    """Updates URI properties in YAML files under the root path"""

    exclude_paths = [Path(exclude).resolve() for exclude in exclude_paths]
    yaml_files = list(root_path.rglob("*.yml")) + list(root_path.rglob("*.yaml"))
    used_services = set()
    cached_files = dict()

    for file in yaml_files:
        if any(file.resolve().is_relative_to(exclude) for exclude in exclude_paths):
            print(f"❌ Skipped: {file} (excluded)")
            continue

        updated, cached_file_path = update_yaml_urls_by_key(file, replacements, restore_files)
        used_services = used_services.union(updated)
        if cached_file_path is not None:
            cached_files[file] = cached_file_path

    print()
    return (used_services, cached_files)
