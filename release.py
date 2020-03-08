"""
Updates the version number and prepares package for uploading to PyPi.
"""

import argparse
import subprocess
import sys
from typing import List, Optional


def execute_subprocess(cmd: List[str]) -> subprocess.CompletedProcess:
    try:
        process = subprocess.run(
            cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        return process
    except subprocess.CalledProcessError as e:
        raise ValueError(
            f"The command {e.cmd} raised the following error: "
            f"{e.stderr.decode('utf-8')}"
        )


def get_current_git_version_number() -> float:
    current_git_version_process = execute_subprocess(
        ["git", "describe", "--tags", "--abbrev=0"],
    )
    return float(current_git_version_process.stdout.decode("utf-8").rstrip())


def get_current_version_number() -> float:
    with open("VERSION", "r") as version_file:
        return float(version_file.read().strip())


def get_new_version_number(new_version: Optional[float] = None) -> str:
    """
    Updates git version and VERSION file number with the given value
    or by an increment of 0.01.
    """
    current_git_version = get_current_git_version_number()
    current_version = get_current_version_number()
    if current_git_version != current_version:
        raise ValueError(
            f"Git version {current_git_version} does not match version "
            f"in VERSION file {current_version}"
        )
    if not new_version:
        new_version = current_git_version + 0.01
    if not new_version > current_version:
        raise ValueError(
            f"New version number {new_version} must be greater than the "
            f"current version {current_version}"
        )
    return format(new_version, ".2f")


def get_tag_message_from_user() -> str:
    """
    Allows for multiline git tag messages to be added.
    """
    print("Add msg for git tag below:")
    contents = ""
    input_line = "start"
    while input_line != "":
        input_line = input()
        contents += "\n" + input_line
    return contents


def update_version_number(version_number: str) -> None:
    """
    Updates git version and VERSION file number
    """
    with open("VERSION", "w") as new_version_file:
        new_version_file.write(version_number)
    msg = get_tag_message_from_user()
    execute_subprocess(["git", "tag", version_number, "-m", msg])


def push_tags() -> None:
    commands = [
        ["git", "add", "VERSION"],
        ["git", "commit", "-m", "Updated version number"],
        ["git", "push", "origin", "master"],
        ["git", "push", "--tags"],
    ]
    for command in commands:
        cmd_process = execute_subprocess(command)
        print(cmd_process.stdout.decode("utf-8"))
        print(cmd_process.stderr.decode("utf-8"))


def prepare_package() -> None:
    setup_process = execute_subprocess(["python", "setup.py", "sdist"])
    print(setup_process.stdout.decode("utf-8"))


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="updates version number, creates package and uploads to PyPi"
    )
    parser.add_argument("--new_version", "-v", type=float, help="new version number")
    return parser


def main() -> None:
    parser = get_parser()
    args = vars(parser.parse_args(sys.argv[1:]))
    new_version_number = get_new_version_number(
        new_version=args.get("new_version", None)
    )
    update_version_number(new_version_number)
    prepare_package()
    push_tags()
    print("Upload to PyPi with the following command:\ntwine upload dist/*")


if __name__ == "__main__":
    main()
