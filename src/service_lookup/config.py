"""Parses configuration file"""
from dataclasses import dataclass
from pathlib import Path

import toml_rs


@dataclass
class ServiceLookupConfiguration:
    use_lens_by_default: bool = False
    revert_after_cleanup: bool = False

def get_configuration():
    configuration = ServiceLookupConfiguration()

    config_file = Path.home() / ".config" / "service-lookup" / "config.toml"

    if config_file.is_file():
        with open(config_file, "rb") as f:
            try:
                config_data = toml_rs.load(f)
                if "use_lens_by_default" in config_data:
                    configuration.use_lens_by_default = config_data["use_lens_by_default"]

                if "revert_after_cleanup" in config_data:
                    configuration.revert_after_cleanup = config_data["revert_after_cleanup"]
            except toml_rs.TOMLDecodeError as e:
                print("Error loading configuration file, check config.toml syntax.")
                print(e, end="\n\n")
    else:
        print(f"No configuration find found at {config_file}, using defaults.")

    return configuration
