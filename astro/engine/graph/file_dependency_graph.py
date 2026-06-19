import json
import os
from typing import Dict, Any, Optional


class FileDependencyEngine:
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root

        self.metadata_path = os.path.join(
            workspace_root, ".astro", "files_metadata.json"
        )

        self.output_path = os.path.join(workspace_root, ".astro", "file_graph.astro")

        self.metadata_data: Dict[str, Any] = {}
        self.file_graph: Dict[str, list[str]] = {}

    def run(self) -> None:
        """
        1. Load metadata
        2. Build graph
        3. Save graph
        """
        self._load_metadata()
        self.build_graph()
        self.save_graph()

    def _load_metadata(self) -> None:
        if not os.path.exists(self.metadata_path):
            raise FileNotFoundError(f"Metadata not found at: {self.metadata_path}")

        with open(self.metadata_path, "r", encoding="utf-8") as f:
            self.metadata_data = json.load(f)

    def _resolve_module_to_path(self, module_name: str) -> Optional[str]:
        """
        Converts:
            astro.storage.manager

        Into:
            C:/Project-Astro/astro/storage/manager.py
        """

        project_root = os.path.dirname(os.path.dirname(self.metadata_path))

        relative_module_path = module_name.replace(".", os.sep) + ".py"

        return os.path.abspath(os.path.join(project_root, relative_module_path))

    def build_graph(self) -> None:
        # Create all file nodes
        for file_path in self.metadata_data.keys():
            self.file_graph[file_path] = []

        # Create dependency edges
        for file_path, file_meta in self.metadata_data.items():
            dependencies_block = file_meta.get("dependencies", {})

            for imported_module in dependencies_block.keys():
                resolved_path = self._resolve_module_to_path(imported_module)

                if (
                    resolved_path
                    and resolved_path in self.metadata_data
                    and resolved_path != file_path
                ):
                    if resolved_path not in self.file_graph[file_path]:
                        self.file_graph[file_path].append(resolved_path)

    def save_graph(self) -> None:
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(self.file_graph, f, indent=2)

        print(f"Indexed {len(self.file_graph)} file nodes.")
        print(f"File Dependency Graph saved to: {self.output_path}")
