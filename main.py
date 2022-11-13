"""
    main.py
"""
import os
import argparse
from base64 import b64decode as b64
import pandas as pd
from rich.padding import Padding
from rich.panel import Panel
from rich.console import Console
from rich import box
from rich.table import Table
from modules import cluster
from modules.table import df_to_table


# Add command line arguments
args = argparse.ArgumentParser()

args.add_argument('find',
                  help='string to find',
                  type=str)
args.add_argument('output',
                  choices=['simple', 'detailed'],
                  help='specify the type of output',
                  type=str)
args.add_argument("-v",
                  "--verbose",
                  help="increase output verbosity",
                  action="store_true")

params = args.parse_args()


if __name__ == '__main__':
    # Get params
    find_string = getattr(params, "find").lower()
    output_format = getattr(params, "output").lower()

    # Clear the screen
    if os.name == 'posix':
        os.system('clear')
    else:
        os.system('cls')

    # Get kube configuration and cluster's name
    cluster.load_config()
    cluster_name = cluster.get_cluster_name()

    # Print the header
    c = Console()
    c.print(Panel.fit("[yellow bold].:: SEARCH FOR STRING IN KUBERNETES CLUSTER ::."))
    c.print(Padding(f"----" \
                    f"\nLooking for: {find_string}" \
                    f"\nCluster name: {cluster_name}" \
                    f"\nOutput format: {output_format}" \
                    f"\n----", (0, 0, 1, 0)))

    # Get all namespaces
    namespaces = cluster.get_all_namespaces()

    # Status
    with c.status("[bold green]Working on namespaces...") as status:

        # Empty lists
        data_p = []
        data_s = []

        # Iterate through retrieved namespaces
        for namespace in namespaces.items:

            if params.verbose:
                print(f'start: {namespace.metadata.name}')

            # Retrieve all pods per namespace
            namespaced_pods = cluster.get_pods_by_namespace(namespace.metadata.name)

            # If returns None go to the next namespace
            if namespaced_pods is None:
                if params.verbose:
                    print(f'-- fail retrieving pods: {namespace.metadata.name}')
                    continue
            else:
                # Iterate through retrieved pods
                for pod in namespaced_pods.items:

                    # Check if the pod it is healthy and running
                    if pod.status.phase == 'Running':

                        # Execute the 'env' command
                        response = cluster.exec_command_pod(pod.metadata.name,
                                                            namespace.metadata.name)

                        # If returns None go to the next running pod
                        if response is None:
                            if params.verbose:
                                print(f'-- fail scanning pod: {namespace.metadata.name}')
                                continue
                        else:
                            # Split the response to get the exactly
                            # line where string was found it
                            lines = response.split('\n')
                            for l in lines:
                                if l.find(find_string) > -1:
                                    data_p.append([namespace.metadata.name.lower(),
                                                  'Pod',
                                                  f'name: {pod.metadata.name.lower()}',
                                                  f'{l}'])

                            # Exit the loop if string was found it
                            break
                if params.verbose:
                    print(f'-- success scanning pod: {namespace.metadata.name}')

            # Retrieve all secrets per namespace
            namespaced_secrets = cluster.get_secret_by_namespace(namespace.metadata.name)

            # If returns None go to the next namespace
            if namespaced_secrets is None:
                if namespaced_secrets is None:
                    if params.verbose:
                        print(f'-- fail retrieving secrets: {namespace.metadata.name}')
            else:
                # Iterate through retrieved secrets
                for secret in namespaced_secrets.items:

                    # User-defined data. Ignore other types of secret
                    if secret.type == 'Opaque':

                        # Check if secret has data
                        if secret.data is not None:

                            # Iterate through all keys and values
                            for key, value in secret.data.items():
                                try:
                                    # Get key and decode value for plain text
                                    k = key.lower() if key != '' else 'emp_k'
                                    v = b64(value).decode('utf-8').lower() \
                                        if value != '' else 'emp_v'

                                    # Check if the string was found it
                                    if (k.find(find_string) > -1 or v.find(find_string) > -1):
                                        data_s.append([namespace.metadata.name.lower(),
                                                      'Secret',
                                                      f'type: {secret.type.lower()}, ' \
                                                      f'name: {secret.metadata.name.lower()}',
                                                      f'{k}={v}'])

                                except UnicodeDecodeError as ex:
                                    continue
                if params.verbose:
                    print(f'-- success reading secrets: {namespace.metadata.name}')

            if params.verbose:
                print(f'done: {namespace.metadata.name}')

    # Set panda options and creates a DataFrame
    pd.set_option('display.max_rows', None)

    # Create two DataFrames
    df_p = pd.DataFrame(data_p,
                        columns=['Namespace',
                                 'Kubernete\'s Object',
                                 'Resource Scanned',
                                 'Details'])

    df_s = pd.DataFrame(data_s,
                        columns=['Namespace',
                                 'Kubernete\'s Object',
                                 'Resource Scanned',
                                 'Details'])

    # Initiate a Table instance to be modified
    table_p = Table(show_header = True,
                    header_style = "bold yellow",
                    show_lines = True)

    table_p.row_styles = ["none", "bright_green"]
    table_p.box = box.MINIMAL_HEAVY_HEAD

    table_s = Table(show_header = True,
                    header_style = "bold yellow",
                    show_lines = True)

    table_s.row_styles = ["none", "bright_green"]
    table_s.box = box.MINIMAL_HEAVY_HEAD

    # param = 'simple' then drop duplicate and ommit last column
    # param = 'detailed' then show every line and every column
    if output_format == 'simple':
        simple_df_p = df_p[['Namespace',
                           'Kubernete\'s Object',
                           'Resource Scanned']]
        table_p = df_to_table(simple_df_p.drop_duplicates(), table_p)

        simple_df_s = df_s[['Namespace',
                           'Kubernete\'s Object',
                           'Resource Scanned']]
        table_s = df_to_table(simple_df_s.drop_duplicates(), table_s)

    if output_format == 'detailed':
        table_p = df_to_table(df_p, table_p)
        table_s = df_to_table(df_s, table_s)

    # Print
    c.print(table_p)
    c.print('')
    c.print(table_s)

    # Footer
    c.print(Padding("----", (1, 0, 0, 0)))
    c.print(Panel.fit("[yellow bold].:: THE END ::."))
