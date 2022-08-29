import base64
import settings
from kubernetes.client import ApiException
from kubernetes.stream import stream
from kubernetes import config, client


class Container:
    def __init__(self, search_string, output_format):
        # Loads authentication and cluster information
        config.load_kube_config('~/.kube/config')
        ctx = config.list_kube_config_contexts()[1]
        
        self.cluster = ctx['context']['cluster'].split('_')[::-1][0]

        # Instantiate Kubernete's class
        self.api = client.CoreV1Api()

        # Get data
        self.search_string = search_string.lower()
        self.output_format = output_format.lower()

    def run_for_all_running_pods(self):
        # Get all pods
        with settings.console.status(
            "[bold green] retrieving pods in all namespaces", spinner="bouncingBar"):

            pods = self.api.list_pod_for_all_namespaces(watch=False)

        settings.log.info("pods retrieved...")

        namespace_previous = ''
        namespace_current = ''

        # Get one pod per namespace and execute env command
        with settings.console.status(
            "[bold green] retrieving pods in all namespaces", spinner="bouncingBar"):

            for pod in pods.items:
                response = ''
                namespace_current = pod.metadata.namespace

                if namespace_previous != namespace_current:
                    try:
                        if pod.status.phase == "Running":
                            response = stream(
                                self.api.connect_get_namespaced_pod_exec,
                                pod.metadata.name,
                                pod.metadata.namespace,
                                command="env",
                                stderr=True,
                                stdin=False,
                                stdout=True,
                                tty=False
                            )
                            response = response.lower()

                            if response.find(self.search_string) > -1:
                                if self.output_format == "list":
                                    settings.namespace_list.append(f"{pod.metadata.namespace}")

                                if self.output_format == "table":
                                    settings.namespace_table.add_row(
                                        namespace_current, ":white_heavy_check_mark:")

                            else:
                                if self.output_format == "table":
                                    settings.namespace_table.add_row(
                                        namespace_current, ":negative_squared_cross_mark:")

                        namespace_previous = namespace_current

                    except ApiException:
                        settings.errorsApi_list.append(f"{pod.metadata.namespace}")

                    finally:
                        namespace_previous = namespace_current

    def run_for_all_secrets(self):
        with settings.console.status("[bold green] retrieving all secrets", spinner="bouncingBar"):
            secrets = self.api.list_secret_for_all_namespaces(watch=False)

        settings.log.info("secrets retrieved...")

        with settings.console.status(
            "[bold green]reading secrets data..", spinner="bouncingBar"):

            for secret in secrets.items:
                    try:
                        if secret.data is not None:
                            for key, value in secret.data.items():

                                if key != '':
                                    key = key.lower()
                                else:
                                    key = "EMPTY_STRING"

                                if value != '':
                                    value = base64.b64decode(value).decode("utf-8").lower()
                                else:
                                    value = "EMPTY_STRING"

                                if (key.find(self.search_string) > -1
                                    or value.find(self.search_string) > -1):
                                    if self.output_format == "list":
                                        vl_secret_l = f'{secret.metadata.name} - '\
                                                      f'{secret.metadata.namespace} - '\
                                                      f'{secret.type}'
                                        if vl_secret_l not in settings.secret_list:
                                            settings.secret_list.append(vl_secret_l)

                                    if self.output_format == "table":
                                        vl_secret_t = [secret.metadata.name, secret.metadata.namespace, secret.type, ":white_check_mark:"]
                                        if vl_secret_t not in settings.secret_prerow:
                                            settings.secret_prerow.append(vl_secret_t)

                                else:
                                    if self.output_format == "table":
                                        vl_secret_t = [secret.metadata.name, secret.metadata.namespace, secret.type, ":x:"]
                                        if vl_secret_t not in settings.secret_prerow:
                                            settings.secret_prerow.append(vl_secret_t)

                    except ApiException:
                        settings.errorsApi_list.append(
                            '{} - {} - {}'.format(
                                secret.metadata.name,
                                secret.metadata.namespace,
                                secret.type
                            )
                        )

                    except UnicodeDecodeError:
                        settings.errorsDecode_list.append(
                            '{} - {} - {}'.format(
                                secret.metadata.name,
                                secret.metadata.namespace,
                                secret.type
                            )
                        )
