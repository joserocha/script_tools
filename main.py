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
args = argparse.ArgumentParser(usage='%(prog)s find output')

args.add_argument('find',
                  metavar='find',
                  help='string to find',
                  type=str)
args.add_argument('output',
                  metavar='output',
                  choices=['simple', 'detailed'],
                  help='specify the type of output',
                  type=str)

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

        # Empty list
        data = []

        # Iterate through retrieved namespaces
        for namespace in namespaces.items:

            # Retrieve all pods per namespace
            namespaced_pods = cluster.get_pods_by_namespace(namespace.metadata.name)

            # If returns None go to the next namespace
            if namespaced_pods is not None:

                # Iterate through retrieved pods
                for pod in namespaced_pods.items:

                    # Check if the pod is healthy and running
                    if pod.status.phase == 'Running':

                        # Execute the 'env' command
                        response = cluster.exec_command_pod(pod.metadata.name,
                                                            namespace.metadata.name)

                        # If returns None go to the next running pod
                        if response is None:
                            continue

                        # Split the response to get the exactly
                        # line where string was found it
                        lines = response.split('\n')
                        for l in lines:
                            if l.find(find_string) > -1:
                                data.append([namespace.metadata.name.lower(),
                                            'Pod',
                                            f'name: {pod.metadata.name.lower()}',
                                            f'{l}'])

                        # Exit the loop if string was found it
                        break
                    else:
                        # If pod is not healthy move to the next pod
                        continue

            # Retrieve all secrets per namespace
            namespaced_secrets = cluster.get_secret_by_namespace(namespace.metadata.name)

            # If returns None go to the next namespace
            if namespaced_secrets is not None:

                # Iterate through retrieved secrets
                for secret in namespaced_secrets.items:

                    # Check if secret has data
                    if secret.data is not None:

                        # Iterate through all keys and values
                        for key, value in secret.data.items():
                            try:
                                # Get key and decode value for plain text
                                k = key.lower() if key != '' else 'emp_k'
                                v = b64(value).decode('utf-8').lower() if value != '' else 'emp_v'

                                # Check if the string was found it
                                if (k.find(find_string) > -1 or v.find(find_string) > -1):
                                    data.append([namespace.metadata.name.lower(),
                                                'Secret',
                                                f'type: {secret.type.lower()}, ' \
                                                f'name: {secret.metadata.name.lower()}',
                                                f'{k}={v}'])

                            except UnicodeDecodeError as ex:
                                continue

            print(f'done: {namespace.metadata.name}')

    # Set options and creates a DataFrame
    pd.set_option('display.max_rows', None)
    df = pd.DataFrame(data,
                      columns=['Namespace',
                               'Kubernete\'s Object',
                               'Resource Scanned',
                               'Details'])

    # Initiate a Table instance to be modified
    table = Table(show_header = True,
                  header_style = "bold yellow",
                  show_lines = True)

    # Modify the table instance to have the data from the DataFrame
    # If simple exclude "Details" columns and drop duplicated values
    if output_format == 'simple':
        simple_df = df[['Namespace',
                        'Kubernete\'s Object',
                        'Resource Scanned']]
        table = df_to_table(simple_df.drop_duplicates(),
                            table)

    # If detailed print all values
    elif output_format == 'detailed':
        table = df_to_table(df, table)

    # Update the style of the table
    table.row_styles = ["none", "bright_green"]
    table.box = box.MINIMAL_HEAVY_HEAD

    # Print
    c.print(table)

    # Footer
    c.print(Padding("----", (1, 0, 0, 0)))
    c.print(Panel.fit("[yellow bold].:: THE END ::."))
