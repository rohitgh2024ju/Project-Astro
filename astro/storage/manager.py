import os
import json


# Find true project root
def find_workspace_root(start_path="."):
    # Traces upward from target path until it finds root anchor files
    curr_dir = os.path.abspath(start_path)
    root_anchors = {"main.py", ".git", ".astro", "requirements.txt", "pyproject.toml"}

    while True:
        curr_content = set(os.listdir(curr_dir))
        if curr_content.intersection(root_anchors):
            return curr_dir

        parent_dir = os.path.dirname(curr_dir)

        if parent_dir == curr_dir:
            return os.path.abspath(start_path)

        curr_dir = parent_dir


# Initiation of storage module
def init_astro_storage(project_path="."):
    # Keep the core hidden directory named after your tool: .astro/
    folder = os.path.join(project_path, ".astro")

    # This is our raw source-of-truth metadata file cache
    file_json = "files_metadata.json"
    files = [
        "file_graph.astro",
        "symbol_graph.astro",
        "unified_graph.astro",
        "env_profile.json",
    ]

    full_path_json = os.path.join(folder, file_json)

    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"Created hidden metadata directory : {folder}/")

    if not os.path.exists(full_path_json):
        with open(full_path_json, "w") as file_out:
            file_out.write("{}")  # empty json
        print(f"Initialized custom tracking file : {full_path_json}")

    for target_file in files:  # Fixed tracking loop name collision
        full_path_astro = os.path.join(folder, target_file)

        if not os.path.exists(full_path_astro):
            with open(full_path_astro, "w") as file_out:  # Fixed local scope shadow
                file_out.write("{}")  # Initialized as empty JSON layout
            print(f"Initialized custom tracking file : {full_path_astro}")


# Saving codebase to files_metadata.json
def save_codebase_map(project_path, codebase_data):
    full_path = os.path.join(project_path, ".astro", "files_metadata.json")

    with open(full_path, "w") as file_out:
        json.dump(codebase_data, file_out, indent=2)

    print(f"Codebase raw metadata architecture successfully cached inside {full_path}.")
