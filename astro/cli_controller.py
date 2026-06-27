import os
import json
from astro.storage.manager import (
    init_astro_storage,
    save_codebase_map,
    find_workspace_root,
)
from astro.parser.code_parser import get_all_py_files, CodeParser
from astro.engine.file_dependency_graph import FileDependencyEngine
from astro.engine.symbol_depencency_graph import SymbolDependencyEngine

# Text formatting
class Color:
    # Text Style Codes
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    # Foreground Color Codes
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"


def run_add(project_path="."):
    print(f"{Color.GREEN}{Color.BOLD}Astro ADD: scanning '{project_path}'{Color.RESET}")
    workspace_root = find_workspace_root(project_path)

    # Create astro repository storage files
    init_astro_storage(workspace_root)

    # Old record check
    cache_path = os.path.join(workspace_root, ".astro", "files_metadata.json")
    existing_records = {}

    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                existing_records = json.load(f)
        except Exception:
            existing_records = {}

    # Initialize a clean dict to only keep track of active live files
    updated_record = {}
    parsed_counter = 0

    files = get_all_py_files(project_path)
    print(f"{Color.BOLD}{Color.YELLOW}Found {len(files)} files to index.{Color.RESET}")

    for file in files:
        print(f" - {file}")

    for file_path in files:
        abs_live_path = os.path.abspath(file_path)

        # Instantiate the new CodeParser class for hashing and parsing
        parser_instance = CodeParser(abs_live_path)
        live_hash = parser_instance.file_hash

        if not live_hash:
            continue

        # Check cache validation hit
        if (
            abs_live_path in existing_records
            and existing_records[abs_live_path].get("hash") == live_hash
        ):
            updated_record[abs_live_path] = existing_records[abs_live_path]
        else:
            print(
                f"{Color.BOLD}{Color.YELLOW}File modified or new -> parsing: {file_path}{Color.RESET}"
            )
            # Execute class parser execution cycle
            metadata = parser_instance.parse()

            updated_record[abs_live_path] = metadata
            parsed_counter += 1

    # Save finalized global snapshot back to disk
    save_codebase_map(workspace_root, updated_record)

    # Track deleted files by comparing structural key differences
    deleted_counter = 0
    for old_path in existing_records:
        if old_path not in updated_record:
            deleted_counter += 1

    if parsed_counter == 0 and deleted_counter == 0:
        print(
            f"{Color.BOLD}{Color.GREEN}Everything is up to date. No changes detected.{Color.RESET}"
        )
    else:
        print(
            f"{Color.BOLD}{Color.GREEN}Sync complete. {parsed_counter} files modified/added, {deleted_counter} files tracking deleted.{Color.RESET}"
        )

    # build graph
    fileEngine = FileDependencyEngine(workspace_root)
    fileEngine.run()
    
    symbolEngine = SymbolDependencyEngine(workspace_root)
    symbolEngine.run()
    


def run_check(project_path="."):
    print(
        f"{Color.CYAN}{Color.BOLD}Astro CHECK: Analyzing {project_path} for mutations...{Color.RESET}"
    )
    # Next play: Wire this up to call Layer 2 (GraphEngine + IntegrityAnalyzer)
    # and Layer 3 (ConfigAnalyzer) from here using files_metadata.json
