# Service-Lookup Utility

A Python-based tool for updating YAML configuration files with dynamic host and port information from Kubernetes clusters. This utility is designed to streamline service discovery and configuration management in microservice environments.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features

- **Dynamic Service Discovery**: Automatically discover services running in a Kubernetes cluster and update your YAML configuration files accordingly.
- **Port Forwarding**: Port forward Kubernetes services to your local machine for development and testing purposes.
- **Custom Mappings**: Use custom mappings to handle services with different names locally and in Kubernetes.
- **Exclusion of Files**: Specify paths to exclude from YAML updates.
- **Setup from Lens Utility**: Configure your environment with a simple setup command if using [Lens](https://k8slens.dev/).

## Example
```bash
service-lookup --root . --namespace dev --services service1,service2 --use-lens --exclude ./target

Port-forwarding service service1 from target port 8080 to local port 24836
Port-forwarding service service2 from target port 8080 to local port 24837

✅ Updated: .\service1\service1-adapter\src\main\resources\application-service1-adapter.yml
✅ Updated: .\service2\service2-adapter\src\main\resources\application-service2-adapter.yml

Press 'ctrl+q' to clean ports and exit.

✅ Process 3740 terminated.
✅ Process 30260 terminated.
✅ Process 31400 terminated.
```

## Requirements

- Python 3.12 or later
- `kubectl` installed and configured
- Access to a Kubernetes cluster

### For Local Build
- [uv](https://docs.astral.sh/uv/)

## Installation from PyPI

```bash
pip install service-lookup
```

### Add to PATH

In order to be able to call `service-lookup` directly from any directory, you must add the Python scripts directory to your PATH environment variable.

The default location for Windows is `<User_Directory>/AppData/Local/Programs/Python/<Python_Version>/Scripts`.

## Installation From Repository

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/iByteABit256/service-lookup.git
   cd service-lookup
   ```

2. **Install Dependencies**:
   ```bash
   uv sync
   ```

3. **Add to pip modules (Optional)**
   ```bash
   pip install .
   ```

4. **Ensure `kubectl` is Installed**:
   Make sure you have `kubectl` installed and configured to access your Kubernetes cluster. You should either have a `.kubeconfig` file or run the setup command if you're using [Lens](https://k8slens.dev/).

## Usage

To use the utility, run the main script with the desired options:

### Basic Command

```bash
service-lookup --root /path/to/root --namespace your-namespace --services service1,service2 --exclude path/to/exclude,another/path/to/exclude
```

### Setup Environment from Kubernetes Lens

To set up your environment based on your [Lens](https://k8slens.dev/) configuration, use the `--use-lens` parameter:

```bash
service-lookup --root /path/to/root --namespace your-namespace --services service1,service2 --exclude path/to/exclude,another/path/to/exclude --use-lens
```

### With Mappings

If you have predefined mappings:

```bash
service-lookup --root /path/to/root --map service1=localhost:8080,service2=localhost:8081 --exclude path/to/exclude,another/path/to/exclude
```

### Options

- `-r`, `--root`: Root directory to search YAML files.
- `-e`, `--exclude`: Comma-separated list of paths to exclude.
- `-m`, `--map`: Comma-separated service=host:port pairs.
- `-n`, `--namespace`: Kubernetes namespace to discover services.
- `-s`, `--services`: Comma-separated list of service names to port forward. Default value is '*' which means every service in the mapping file.
- `-f`, `--mapping-file`: Path to JSON file with service_name -> kubernetes_service_name mappings.
- `-l`, `--use-lens`: Use kubeconfigs from Lens.

## Configuration

### Service Mappings

Create a `service_mappings.json` file to map local service names to Kubernetes service names:

```json
{
    "local-service-a-name": "kubernetes-service-a-name",
    "local-service-b-name": "kubernetes-service-b-name"
}
```

Running without the `--services` option searches for every service in the mappings file above.

### Exclusion Paths

Use the `--exclude` option to specify paths in the root directory that should be excluded from updates.

## Contributing

All contributions are welcome! To contribute:

1. Fork the repository on GitHub.
2. Create a new branch for your feature or fix.
3. Commit your changes and push your branch to GitHub.
4. Submit a pull request for review.

## License

This project is licensed under the GNU GPL-3.0 License. See the [LICENSE](LICENSE) file for more details.
