#!/bin/bash

# Define variables
TOKEN_FILE="/var/run/secrets/kubernetes.io/serviceaccount/token"
NAMESPACE_FILE="/var/run/secrets/kubernetes.io/serviceaccount/namespace"
KUBE_API_SERVER="https://kubernetes.default.svc.cluster.local"
CSV_FILE="permissions.csv"

# Check if token file exists
if [ ! -f "$TOKEN_FILE" ]; then
    echo "Token file not found!"
    exit 1
fi

# Get the token
TOKEN=$(cat "$TOKEN_FILE")
NAMESPACE=$(cat "$NAMESPACE_FILE")

# Predefined list of resources and verbs worth checking
declare -A CHECK_LIST=(
    ["clusterroles"]="create update patch delete bind"
    ["clusterrolebindings"]="create update patch delete bind"
    ["roles"]="create update patch delete bind"
    ["rolebindings"]="create update patch delete bind"
    ["secrets"]="get list update delete"
    ["configmaps"]="get list create update patch delete"
    ["pods/exec"]="create"
    ["pods"]="exec"
    ["serviceaccounts"]="create update patch delete"
)

# Function to query Kubernetes API
query_kube_api() {
    local endpoint="$1"
    curl -s --cacert /var/run/secrets/kubernetes.io/serviceaccount/ca.crt \
         --header "Authorization: Bearer $TOKEN" \
         "$KUBE_API_SERVER$endpoint"
}

# Function to make a POST request
post_request() {
    local endpoint="$1"
    local data="$2"
    curl -s --cacert /var/run/secrets/kubernetes.io/serviceaccount/ca.crt \
         --header "Authorization: Bearer $TOKEN" \
         --header "Content-Type: application/json" \
         --request POST \
         --data "$data" \
         "$KUBE_API_SERVER$endpoint"
}

# Function to get API groups
get_api_groups() {
    response=$(query_kube_api "/apis")
    echo "$response" | awk '
    /"name":/ {
      group=$2
      gsub(/"|,/, "", group)
      print group
    }
    '
}

# Function to get resources and verbs
get_resources_and_verbs() {
    # Query core API resources
    response=$(query_kube_api "/api/v1")
    echo "$response" | awk '
    BEGIN {
      resource = ""
      verbs = ""
    }
    /"name":/ {
      resource=$2
      gsub(/"|,/, "", resource)
    }
    /"verbs": \[/ {
      in_verbs=1
      verbs=""
      next
    }
    in_verbs && /]/ {
      in_verbs=0
      next
    }
    in_verbs {
      gsub(/"|,/, "", $0)
      if (length($0) > 0) {
        verbs = verbs (length(verbs) ? " " : "") $0
      }
    }
    /}/ {
      if (length(resource) > 0 && length(verbs) > 0) {
        print ":" resource ":" verbs
      }
    }
    ' | while IFS=":" read -r api_group resource verbs; do
      for verb in $(echo "$verbs" | tr -s ' '); do
        check_permission "$resource" "$verb" "$api_group"
      done
    done

    # Query additional API groups
    for group in $(get_api_groups); do
        response=$(query_kube_api "/apis/$group")
        pref_version=$(echo $response | grep -oP '"preferredVersion":\s*{\s*"groupVersion":\s*"\K[^"]+')
        response=$(query_kube_api "/apis/$pref_version")
        echo "$response" | awk '
        BEGIN {
          resource = ""
          verbs = ""
        }
        /"name":/ {
          resource=$2
          gsub(/"|,/, "", resource)
        }
        /"verbs": \[/ {
          in_verbs=1
          verbs=""
          next
        }
        in_verbs && /]/ {
          in_verbs=0
          next
        }
        in_verbs {
          gsub(/"|,/, "", $0)
          if (length($0) > 0) {
            verbs = verbs (length(verbs) ? " " : "") $0
          }
        }
        /}/ {
          if (length(resource) > 0 && length(verbs) > 0) {
            print group ":" resource ":" verbs
          }
        }
        ' | while IFS=":" read -r api_group resource verbs; do
          for verb in $(echo "$verbs" | tr -s ' '); do
            check_permission "$resource" "$verb" "$pref_version"
          done
        done
    done
}

# Check the permission for a specific resource and verb
check_permission() {
    local resource="$1"
    local verb="$2"
    local api_group="$3"

    local data=$(cat <<EOF
{
    "apiVersion": "authorization.k8s.io/v1",
    "kind": "SelfSubjectAccessReview",
    "spec": {
        "resourceAttributes": {
            "namespace": "$(echo $NAMESPACE)",
            "verb": "$verb",
            "resource": "$resource"
        }
    }
}
EOF
)
    response=$(post_request "/apis/authorization.k8s.io/v1/selfsubjectaccessreviews" "$data")

    if echo "$response" | grep -q '"allowed": true'; then
        worth_checking=""
        for res in "${!CHECK_LIST[@]}"; do
            if [[ "$resource" == "$res" ]] && [[ "${CHECK_LIST[$res]}" == *"$verb"* ]]; then
                worth_checking="Yes"
                break
            fi
        done
        echo "$api_group,$resource,$verb,$worth_checking" >> "$CSV_FILE"
    fi
}


# Main script
echo "Checking permissions..."

echo "API Group,Resource,Verb,Known High Privilege" > "$CSV_FILE"

# Get resources and verbs
get_resources_and_verbs

echo "Permission check complete. Results saved to $CSV_FILE"
