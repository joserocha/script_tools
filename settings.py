import logging
from rich.logging import RichHandler
from rich.table import Table
from rich.console import Console
from rich import box


# logging console
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(
        show_path=False,
        show_level=False
    )]
)
log = logging.getLogger("rich")

# console
console = Console()

# padding table
padding = (0, 0, 0, 12)

# namespace table
namespace_table = Table(title="Kubernete's Namespaces", box=box.ROUNDED, padding=padding)
namespace_table.add_column("Namespace", justify="left", style="white", no_wrap=True)
namespace_table.add_column("Found it ?", justify="center", style="white", no_wrap=True)

# secret table
secret_table = Table(title="Kubernete's Namespaces", box=box.ROUNDED, padding=padding)
secret_table.add_column("Secret", justify="left", style="white", no_wrap=True)
secret_table.add_column("Namespace", justify="left", style="white", no_wrap=True)
secret_table.add_column("Type", justify="left", style="white", no_wrap=True)
secret_table.add_column("Found it ?", justify="center", style="white", no_wrap=True)

# namespace list
namespace_list = []

# secret list
secret_list = []

# secret table
secret_prerow = []

# errors api
errorsApi_list = []

# errors decode
errorsDecode_list = []
