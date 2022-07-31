import subprocess
import click


@click.command()
@click.argument("path", default="snakeeyes")
def cli(path):
    """
    Run a test covarage report
    :param path: Test covarage path.
    :return: Subproccess call result
    """
    cmd = f"python -m pytest --cov-report term-missing --cov {path}"
    return subprocess.call(cmd, shell=True)
