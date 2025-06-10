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
- **Setup Utility**: Configure your environment with a simple setup command.

## Requirements

- Python 3.7 or later
- `kubectl` installed and configured
- Access to a Kubernetes cluster
- [uv](https://docs.astral.sh/uv/)

### Installation from PyPI

Once the package is published on PyPI, you can install it using pip:
```bash
pip install service-lookup
```

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

3. **Ensure `kubectl` is Installed**:
   Make sure you have `kubectl` installed and configured to access your Kubernetes cluster.

## Usage

To use the utility, run the main script with the desired options:

### Basic Command

```bash
python main.py --root /path/to/root --namespace your-namespace --services service1,service2 --exclude path/to/exclude
```

### Setup Environment

To set up your environment for Kubernetes configuration, use:

```bash
python main.py --setup
```

### With Mapping

If you have predefined mappings:


```bash
python main.py --map service1=localhost:8080,service2=localhost:8081
```

### Options

- `-r`, `--root`: Root directory to search YAML files.
- `-e`, `--exclude`: Comma-separated list of paths to exclude.
- `-m`, `--map`: Comma-separated service=host:port pairs.
- `-n`, `--namespace`: Kubernetes namespace to discover services.
- `-v`, `--services`: Comma-separated list of service names to port forward.
- `-f`, `--mapping-file`: Path to JSON file with service mappings.
- `-s`, `--setup`: Run setup to configure KUBECONFIG.

## Configuration

### Service Mappings

Create a `service_mappings.json` file to map local service names to Kubernetes service names:

```json
{
    "local-service-a-name": "kubernetes-service-a-name",
    "local-service-b-name": "kubernetes-service-b-name"
}
```

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

## Contact

For questions or feedback, please reach out via the project's GitHub issues page or contact the maintainer directly.
