from kubernetes import client, config
from collections import defaultdict

# Load kube config
config.load_kube_config()

# Create API clients
v1 = client.CoreV1Api()
rbac_v1 = client.RbacAuthorizationV1Api()

# Define high privilege actions and resources with API groups
high_privilege_actions = {
    '*': ['create', 'update', 'patch', 'delete', 'bind', 'get', 'exec'],
    'clusterroles': ['create', 'update', 'patch', 'delete', 'bind'],
    'clusterrolebindings': ['create', 'update', 'patch', 'delete', 'bind'],
    'roles': ['create', 'update', 'patch', 'delete', 'bind'],
    'rolebindings': ['create', 'update', 'patch', 'delete', 'bind'],
    'secrets': ['get', 'list', 'update', 'patch', 'delete'],
    'configmaps': ['get', 'list', 'create', 'update', 'patch', 'delete'],
    'pods/exec': ['create'],
    'pods': ['exec'],
    'serviceaccounts': ['create', 'update', 'patch', 'delete']
}

def is_high_privilege(privileges):
    reason = []
    # Check for wildcard high privileges
    if '*' in privileges:
        if '*' in privileges['*']:
            reason.append('*:*')

    # Check for specific high privilege actions
    for resource, verbs in privileges.items():
        if resource in high_privilege_actions:
            for verb in verbs:
                if verb == '*':
                    reason.append(f'{resource}:*')
                if verb in high_privilege_actions[resource]:
                    reason.append(f'{resource}:{verb}')

    return list(set(reason))

def get_roles():
    roles = rbac_v1.list_role_for_all_namespaces()
    cluster_roles = rbac_v1.list_cluster_role()
    return roles.items, cluster_roles.items

def get_bindings():
    role_bindings = rbac_v1.list_role_binding_for_all_namespaces()
    cluster_role_bindings = rbac_v1.list_cluster_role_binding()
    return role_bindings.items, cluster_role_bindings.items

def get_pods():
    pods = v1.list_pod_for_all_namespaces()
    return pods.items

def rbac_to_text(rbac: defaultdict[list], _type: str):
    line = ''
    for resource, verbs in rbac.items():
        line += f'{_type}:{resource}:{','.join(verbs)},'
    return line[:-1]

def main():
    roles, cluster_roles = get_roles()
    role_bindings, cluster_role_bindings = get_bindings()
    pods = get_pods()

    identities = defaultdict(lambda: {
        'rbac': {'roles': defaultdict(list), 'cluster_roles': defaultdict(list)},
        'name': 'default',
        'pods': [],
        'namespace': '',
        'type': 'default_service_account',
        'users': []
    })

    # Helper function to determine identity type
    def get_identity_type(kind, namespace):
        if kind == "ServiceAccount":
            if namespace == "kube-system":
                return "system_service_account"
            else:
                return "service_account"
        elif kind == "User":
            return "user"
        elif kind == "Group":
            return "group"
        return kind

    # Collect RBAC permissions from role bindings
    for binding in role_bindings:
        subjects = binding.subjects
        role_ref = binding.role_ref
        binding_namespace = binding.metadata.namespace

        for subject in subjects:
            kind = subject.kind
            name = subject.name
            if not name:
                print(subject)
            namespace = subject.namespace if subject.namespace else "default"
            key = f"{kind.lower()}_{namespace}_{name}" if kind == "ServiceAccount" else f"{kind.lower()}_{name}"

            identities[key]['name'] = name
            identities[key]['namespace'] = namespace
            identities[key]['type'] = get_identity_type(kind, namespace)

            for role in roles:
                if role.metadata.name == role_ref.name and role.metadata.namespace == binding_namespace:
                    for rule in role.rules:
                        for resource in rule.resources:
                            for verb in rule.verbs:
                                identities[key]['rbac']['roles'][resource].append(verb)

    # Collect RBAC permissions from cluster role bindings
    for binding in cluster_role_bindings:
        subjects = binding.subjects
        role_ref = binding.role_ref

        if not subjects:
            continue

        for subject in subjects:
            kind = subject.kind
            name = subject.name
            namespace = subject.namespace if subject.namespace else "default"
            key = f"{kind.lower()}_{namespace}_{name}" if kind == "ServiceAccount" else f"{kind.lower()}_{name}"

            identities[key]['name'] = name
            identities[key]['namespace'] = namespace
            identities[key]['type'] = get_identity_type(kind, namespace)
            for role in cluster_roles:
                if role.metadata.name == role_ref.name:
                    for rule in role.rules:
                        if not rule.resources:
                            continue
                        for resource in rule.resources:
                            for verb in rule.verbs:
                                identities[key]['rbac']['cluster_roles'][resource].append(verb)

    # Collect Pods
    for pod in pods:
        namespace = pod.metadata.namespace
        service_account = pod.spec.service_account_name
        if service_account:
            key = f"serviceaccount_{namespace}_{service_account}"

            identities[key]['pods'].append(pod.metadata.name)

    # Save results to csv
    with open('./identities.csv', 'w') as fp:
        headers = ['Name', 'Type', 'Namespace', 'RBAC', 'Pods', 'Is HP', 'Reason']
        line = f"{','.join(headers)}\n"
        fp.write(line)
        for identity, data in identities.items():
            name = data['name']
            _type = data['type']
            namespace = data['namespace']
            rbac = f'{rbac_to_text(data['rbac']['roles'], 'role')},{rbac_to_text(data['rbac']['cluster_roles'], 'clusterRole')}'
            if rbac == ',':
                rbac = ''
            elif rbac.endswith(','):
                rbac = rbac[:-1]
            elif rbac.startswith(','):
                rbac = rbac[1:]
            pods = ','.join(data['pods'])
            reason = f'{','.join(is_high_privilege(data['rbac']['roles']) + is_high_privilege(data['rbac']['cluster_roles']))}'
            is_hp = True if reason else False
            
            line = f'{name},{_type},{namespace},"{rbac}","{pods}",{is_hp},"{reason}"\n'
            fp.write(line)

if __name__ == "__main__":
    main()