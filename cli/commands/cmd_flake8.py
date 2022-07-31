import subprocess
import click


@click.command()
@click.option(
    "--skip-init/--no-skip-init", default=True, help="Skip __init__.py files?"
)
@click.argument("path", default="snakeeyes")
def cli(skip_init, path):
    """
    Run flake8 to analyse youre code base.
    :param skip_init: Skip checking __init__.py files.
    :param path: Project path.
    :return: Subproccess call result
    """

    flake8_flag_exclude = ""
    if skip_init:
        flake8_flag_exclude += " --exclude __init__.py"
    cmd = f"flake8 {path}{flake8_flag_exclude}"
    return subprocess.call(cmd, shell=True)
