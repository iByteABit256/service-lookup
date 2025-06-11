"""Setups kubeconfig based on Lens configuration"""

from pathlib import Path

def run_setup():
    """Creates batch file and prints remaining instructions"""

    # Generate the batch file
    batch_file_path = generate_batch_file()

    if batch_file_path:
        # Execute the batch file
        print(f"Batch file created at: {batch_file_path}")
        print("Please run the following command in your command prompt" \
            " to set the KUBECONFIG variable:")
        print(f"{batch_file_path}")
    else:
        print("Failed to create batch file.")

def generate_batch_file():
    """Generates batch file for kubeconfig"""
    # Define the Lens kubeconfigs directory
    lens_kubeconfigs_dir = Path.home() / "AppData" / "Roaming" / "Lens" / "kubeconfigs"

    # Verify the directory exists
    if not lens_kubeconfigs_dir.exists():
        print("Lens kubeconfigs directory not found. \
            Please ensure Lens is installed and configured.")
        return None

    # Find all kubeconfig files in the Lens directory
    kubeconfig_files = list(lens_kubeconfigs_dir.glob('*'))

    if not kubeconfig_files:
        print("No kubeconfig files found in the Lens directory.")
        return None

    # Construct the KUBECONFIG variable
    kubeconfig_paths = [str(file) for file in kubeconfig_files]

    # Include the default kubeconfig location
    default_kubeconfig = Path.home() / ".kube" / "config"
    if default_kubeconfig.exists():
        kubeconfig_paths.insert(0, str(default_kubeconfig))

    # Generate the batch file content
    kubeconfig_env_value = ";".join(kubeconfig_paths)
    batch_content = f"@echo off\nset KUBECONFIG={kubeconfig_env_value}" \
        "\necho KUBECONFIG set to %KUBECONFIG%\n"

    # Write the batch file
    batch_file_path = Path.home() / "set_kubeconfig.bat"
    with open(batch_file_path, 'w', encoding="utf-8") as batch_file:
        batch_file.write(batch_content)

    return str(batch_file_path)
