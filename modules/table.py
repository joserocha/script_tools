"""
    table.py
"""
from typing import Optional
from rich.table import Table
import pandas as pd


def df_to_table(pandas_dataframe: pd.DataFrame,
                rich_table: Table,
                show_index: bool = False,
                index_name: Optional[str] = None) -> Table:
    """get_pods_by_namespace"""
    if show_index:
        index_name = str(index_name) if index_name else ""
        rich_table.add_column(index_name)

    for column in pandas_dataframe.columns:
        rich_table.add_column(str(column))

    for index, value_list in enumerate(pandas_dataframe.values.tolist()):
        row = [str(index)] if show_index else []
        row += [str(x) for x in value_list]
        rich_table.add_row(*row)

    return rich_table
