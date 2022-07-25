import os

from invoke import task, Context

from rich.console import Console
console = Console(style="bold")


PACKAGE_NAME = "outbox_streaming"


@task
def lint(c):
    c: Context

    console.print("Running black...")
    c.run(f"black {PACKAGE_NAME}", pty=True)

    console.print("Running flake8...")
    c.run(f"flake8 {PACKAGE_NAME}", pty=True)

    console.print("Running isort...")
    c.run(f"isort {PACKAGE_NAME}", pty=True)

    console.print("Running mypy...")
    c.run(f"mypy {PACKAGE_NAME}", pty=True)


@task
def test(c):
    c: Context
    c.run("pytest -svvv", pty=True)