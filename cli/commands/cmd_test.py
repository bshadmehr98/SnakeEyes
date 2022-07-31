import subprocess
import os
import click


@click.command()
@click.argument("path", default=os.path.join("snakeeyes", "tests"))
def cli(path):
    """
    Run tests with pytest
    :param path: Test path.
    :return: Subproccess call result
    """
    cmd = f"python -m pytest {path}"
    return subprocess.call(cmd, shell=True)
