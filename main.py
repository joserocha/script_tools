import argparse
import settings
from rich.padding import Padding
from rich.panel import Panel
from container import Container


# Create the argument parser
args = argparse.ArgumentParser(
    usage="%(prog)s find output"
)

# Add the arguments
args.add_argument(
    "find",
    metavar="find",
    help="string to find",
    type=str
)
args.add_argument(
    "output",
    metavar="output",
    choices=["table", "list"],
    help='specify the type of output',
    type=str
)

# Parse the args
params = args.parse_args()
# params = "teste"


if __name__ == '__main__':
    # Instantiate Container Class
    kube = Container(getattr(params, "find"), getattr(params, "output"))

    # Mount the header
    settings.console.print(
        Panel.fit("[yellow bold].:: SEARCH FOR STRING IN KUBERNETES CLUSTER ::.")
    )
    settings.console.print(
        Padding(
            f"----"\
            f"\nLooking for: {getattr(params, 'find')}"\
            f"\nCluster name: {kube.cluster}"\
            f"\n----", (0, 0, 1, 0))
    )

    # Call method to execute env command in running pods and search for a specific string
    kube.run_for_all_running_pods()

    # Call method to decode secrets and search for a specific string
    kube.run_for_all_secrets()

    # Create an empty line
    settings.console.print("")

    ####
    ## Output as list (print only matched namespaces)
    ####
    if getattr(params, "output") == "list":

        if len(settings.namespace_list) > 0:
            settings.log.info("the following pods / namespaces contains the searched string:")
            for n in settings.namespace_list:
                settings.console.print(f'[yellow]{"": <10} {n}')
        else:
            settings.log.info("no pod / namespace contains the searched string")

        if len(settings.secret_list) > 0:
            settings.console.print("")
            settings.log.info("the following secrets / namespaces contains the searched string:")
            for d in settings.secret_list:
                settings.console.print(f'[yellow]{"": <10} {d}')
        else:
            settings.log.info("no secret / namespace contains the searched string")

    ####
    ## Output as table (print all namespaces)
    ####
    # if getattr(params, "output") == "table":
    #     settings.log.info("the result in all namespaces:")
    #     settings.console.print("")
    #     settings.console.print(f'{settings.namespace_table}')
    #     settings.console.print("")

    #     settings.log.info("the result in all secrets:")
    #     for row in zip(*settings.secret_prerow):
    #         settings.secret_table.add_row(*row)
    #     settings.console.print(settings.secret_table)
    #     settings.console.print("")

    ####
    ## Output any Api raised error
    ####
    if len(settings.errorsApi_list) > 0:
        settings.console.print("")
        settings.log.info("the following namespaces raised Api exceptions")
        for e in settings.errorsApi_list:
            settings.console.print(f'[red]{"": <10} {e}')

    ####
    ## Output any Decode raised error
    ####
    if len(settings.errorsDecode_list) > 0:
        settings.console.print("")
        settings.log.info("the following namespaces raised Decoded exceptions")
        for e in settings.errorsDecode_list:
            settings.console.print(f'[red]{"": <10} {e}')

    settings.console.print(Panel.fit("[yellow bold].:: THE END ::."))
