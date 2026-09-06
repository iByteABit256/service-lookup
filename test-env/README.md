# test-env/README.md

## Prerequisites
- Docker running
- `k3d` installed ([Install](https://k3d.io/v5.6.3/#installation))
- `kubectl` installed ([Install](https://kubernetes.io/docs/tasks/tools/#kubectl))

## First-time setup

    k3d cluster create --config test-env/k3d-config.yaml
    kubectl apply -f test-env/manifests/
    kubectl get pods -n dev --watch

## Running the tool

    uv run service-lookup \
      --root ./test-env/mock-application-properties \
      --namespace dev \
      --services service-a,service-b \
      --mapping-file ./test-env/service_mappings.json

## Reset test configs (undo YAML changes)
    git restore test-env/mock-application-properties/

## Stop/start cluster
    k3d cluster stop service-lookup-test
    k3d cluster start service-lookup-test
