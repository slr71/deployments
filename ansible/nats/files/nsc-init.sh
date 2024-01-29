#!/bin/bash

# Exit when any command fails
set -e

namespace=$1

# used to nsc init to NATS
nsc_init=$(cat <<EOF
#!/bin/bash

# Initialize NATS Streaming Cluster
nsc init --config-dir /nsc/nats/nsc/stores --name de

# Add operator
nsc add operator -n cyverse --sys

# Generate operator key
operator_key=\$(nsc generate nkey -o --store | awk '{print \$NF}' | sed 's/^.*\///')

# Edit operator
nsc edit operator --sk "\$operator_key"

# Add account
nsc add account -n de -K "\$operator_key"

# Generate account key
account_key=\$(nsc generate nkey -a --store | awk '{print \$NF}' | sed 's/^.*\///')

# Edit account
nsc edit account -n de --sk "\$account_key"

# Add user
nsc add user --account de --name services -K "\$account_key"

EOF
)

run_nsc_setup() {
  local namespace="$1"
  local pod_name=$(kubectl get pod -n $namespace | awk '/^nats-box/ {print $1}')
  local file_path=/nsc/nkeys/creds/cyverse
  # Check if the file exists inside the pod
  if kubectl exec "$pod_name" -n "$namespace" -- ls "$file_path" &>/dev/null; then
    echo -e "${GREEN}File $file_path exists in the pod. Skipping init..."
  else
    echo "File $file_path does not exist in the pod. Init nsc.."
    echo "$nsc_init" | kubectl exec -i "$pod_name" -n "$namespace" -- sh
    # TODO restart dependent services
  fi
}

run_nsc_setup "$namespace"
