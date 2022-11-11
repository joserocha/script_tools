"""
    main.py
"""
import os
import argparse
from base64 import b64decode as b64
from typing import Optional
import pandas as pd
from rich.padding import Padding
from rich.panel import Panel
from rich.console import Console
from rich import box
from rich.table import Table
from rich.align import Align
from modules import cluster


def df_to_table(
    pandas_dataframe: pd.DataFrame,
    rich_table: Table,
    show_index: bool = False,
    index_name: Optional[str] = None,
) -> Table:
    """Convert a pandas.DataFrame obj into a rich.Table obj.
    Args:
        pandas_dataframe (DataFrame): A Pandas DataFrame to be converted to a rich Table.
        rich_table (Table): A rich Table that should be populated by the DataFrame values.
        show_index (bool): Add a column with a row count to the table. Defaults to True.
        index_name (str, optional): The column name to give to the index column.
        Defaults to None, showing no value.
    Returns:
        Table: The rich Table instance passed, populated with the DataFrame values."""

    if show_index:
        index_name = str(index_name) if index_name else ""
        rich_table.add_column(index_name)

    for column in pandas_dataframe.columns:
        rich_table.add_column(Align(str(column), align='center'))

    for index, value_list in enumerate(pandas_dataframe.values.tolist()):
        row = [str(index)] if show_index else []
        row += [str(x) for x in value_list]
        rich_table.add_row(*row)

    return rich_table


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
    find_string = getattr(params, "find").lower()
    output_format = getattr(params, "output").lower()

    if os.name == 'posix':
        os.system('clear')
    else:
        os.system('cls')

    data = []
    cluster.load_config()
    cluster_name = cluster.get_cluster_name()

    c = Console()

    c.print(Panel.fit("[yellow bold].:: SEARCH FOR STRING IN KUBERNETES CLUSTER ::."))
    c.print(Padding(f"----" \
                    f"\nLooking for: {find_string}" \
                    f"\nCluster name: {cluster_name}" \
                    f"\n----", (0, 0, 1, 0)))

    namespaces = cluster.get_all_namespaces()
    for namespace in namespaces.items:

        if namespace.metadata.name == 'accounts':

            namespaced_pods = cluster.get_pods_by_namespace(namespace.metadata.name)
            for pod in namespaced_pods.items:
                if pod.status.phase == 'Running':
                    response = cluster.exec_command_pod(pod.metadata.name,
                                                        namespace.metadata.name)
                    if response is None:
                        data.append([namespace.metadata.name.lower(),
                                    'Running Pod',
                                    f'{pod.metadata.name.lower()} -> \
                                        Problema em executar o comando env',
                                    'Erro'])
                        continue

                    lines = response.split('\n')
                    for l in lines:
                        if l.find(find_string) > -1:
                            data.append([namespace.metadata.name.lower(),
                                        'Pod',
                                        f'name: {pod.metadata.name.lower()}',
                                        f'{l}'])

                    break
                else:
                    continue

            namespaced_secrets = cluster.get_secret_by_namespace(namespace.metadata.name)
            for secret in namespaced_secrets.items:
                if secret.data is not None:

                    for key, value in secret.data.items():
                        try:
                            k = key.lower() if key != '' else 'empty_key'
                            v = b64(value).decode('utf-8').lower() if value != '' else 'empty_value'

                            if (k.find(find_string) > -1 or v.find(find_string) > -1):
                                data.append([namespace.metadata.name.lower(),
                                            'Secret',
                                            f'type: {secret.type.lower()}, \
                                              name: {secret.metadata.name.lower()}',
                                            f'{k}={v}'])

                        except UnicodeDecodeError as ex:
                            data.append([namespace.metadata.name.lower(),
                                        'Secret',
                                        '',
                                        f'{key.lower()} -> Deu erro de decode'])

    pd.set_option('display.max_rows', None)
    df = pd.DataFrame(data,
                      columns=['Namespace',
                               'Kubernete\'s Object',
                               'Resource Scanned',
                               'Details'])

    # Initiate a Table instance to be modified
    table = Table(show_header=True, header_style="bold yellow")

    # Modify the table instance to have the data from the DataFrame
    if output_format == 'simple':
        simple_df = df[['Namespace', 'Kubernete\'s Object', 'Resource Scanned']]
        table = df_to_table(simple_df.drop_duplicates(), table)
    elif output_format == 'detailed':
        table = df_to_table(df, table)

    # Update the style of the table
    table.row_styles = ["none", "bright_green"]
    table.box = box.ROUNDED

    c.print(table)

    c.print(Padding("----", (1, 0, 0, 0)))
    c.print(Panel.fit("[yellow bold].:: THE END ::."))
