"""
    container.py
"""

from kubernetes.client import ApiException
from kubernetes.stream import stream
from kubernetes import config, client


def load_config():
    """load_config"""
    config.load_kube_config('~/.kube/config')


def get_cluster_name():
    """get_cluster_name"""
    ctx = config.list_kube_config_contexts()[1]
    return ctx['context']['cluster'].split('_')[::-1][0]


def get_all_namespaces():
    """get_all_namespaces"""
    api = client.CoreV1Api()
    return api.list_namespace()


def get_pods_by_namespace(namespace):
    """get_pods_by_namespace"""
    api = client.CoreV1Api()
    try:
        return api.list_namespaced_pod(namespace=namespace)

    except ApiException:
        return None


def exec_command_pod(pod_name, namespace_name):
    """exec_command_pod"""
    api = client.CoreV1Api()
    try:
        return stream(api.connect_get_namespaced_pod_exec,
                    pod_name,
                    namespace_name,
                    command='env',
                    stderr=True,
                    stdin=False,
                    stdout=True,
                    tty=False).lower()

    except ApiException:
        return None


def get_secret_by_namespace(namespace):
    """get_secret_by_namespace"""
    api = client.CoreV1Api()
    try:
        return api.list_namespaced_secret(namespace=namespace)

    except ApiException:
        return None
