import sys  # noqa: E402
from astro.cli_controller import run_add, run_check, env_profile
import os


def main():
    print("Astro Engine: Ground Control to Major Tom. We are ready.")
    # sys.argv is list of typed text, sys.argv[0] is script name
    arguments = sys.argv[1:]

    if not arguments:
        print("Usage: python main.py [add|check] [path]")
        return

    # fetch actual command
    command = arguments[0]

    if command == "add":
        path = arguments[1] if len(arguments) > 1 else "."
        print(
            f"Astro ADD triggered, parsing files from root file '{path}' and building graph map"
        )
        run_add(path)

        size_metadata = os.path.getsize("./.astro/files_metadata.json")
        size_file_graph = os.path.getsize("./.astro/file_graph.astro")
        size_file_env = os.path.getsize("./.astro/env_profile.json")

        print(f"Metadata file size : {size_metadata / 1024:.2f} KB")
        print(f"File Dependency file size : {size_file_graph / 1024:.2f} KB")
        print(f"Environmental Profile file size : {size_file_env / 1024:.2f} KB")

    elif command == "check":
        path = arguments[1] if len(arguments) > 1 else "."
        print(f"Astro check triggered: analyzing files in '{path}' for mutations...")

        run_check(path)

    elif command == "doctor":
        print("Env Profile-")
        env_profile()

    else:
        print(f"UNKNOWN command: {command}\nAvailable commands: add, check")


if __name__ == "__main__":
    main()

# python main.py add .
# python main.py doctor
