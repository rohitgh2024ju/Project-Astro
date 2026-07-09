import json
import os
from typing import Dict, List, Set, Tuple, Optional, Any

class UnifiedDependencyEngine:
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.file_graph = os.path.join(workspace_root, ".astro", "file_graph.astro")
        self.symbol_graph = os.path.join(workspace_root, ".astro", "symbol_graph.astro")
        self.output_path = os.path.join(workspace_root, ".astro", "unified_graph.astro")
        self.file_data: Dict[str, List[str]] = {}
        self.symbol_data: Dict[str, Any] = {"nodes": [], "edges": []}     
        self.graph = {
            "nodes": [],
            "edges": []
        }

    def run(self) -> None:
        self.load_input_graphs()
        self.merge_graphs()
        self.save_graph()

    def load_input_graphs(self) -> None:
        if not os.path.exists(self.file_graph):
            raise FileNotFoundError(f"File-level graph missing at: {self.file_graph}")
        with open(self.file_graph, "r", encoding="utf-8") as f:
            self.file_data = json.load(f)
        if not os.path.exists(self.symbol_graph):
            raise FileNotFoundError(f"Symbol-level graph missing at: {self.symbol_graph}")
        with open(self.symbol_graph, "r", encoding="utf-8") as f:
            self.symbol_data = json.load(f)

    def f_id(self, absolute_path: str) -> str:
        if not os.path.isabs(absolute_path):
            return absolute_path.replace(os.sep, "/")
        return os.path.relpath(absolute_path, self.workspace_root).replace(os.sep, "/")

    def merge_graphs(self) -> None:
        reg_files: Set[str] = set()
        for abs_path in self.file_data.keys():
            f_id = self.f_id(abs_path)
            reg_files.add(f_id)
            
            self.graph["nodes"].append({
                "id": f_id,
                "name": os.path.basename(abs_path),
                "kind": "FILE",
                "file": f_id
            })

        for source, targets in self.file_data.items():
            source_id = self.f_id(source)
            for target_path in targets:
                target_id = self.f_id(target_path)
                if target_id not in reg_files:
                    reg_files.add(target_id)
                    self.graph["nodes"].append({
                        "id": target_id,
                        "name": os.path.basename(target_path),
                        "kind": "FILE",
                        "file": target_id
                    })
                self.graph["edges"].append({
                    "source": source_id,
                    "target": target_id,
                    "type": "DEPENDS_ON"
                })

        # Append Symbol Nodes with workspace-relative file locations
        for symbol_node in self.symbol_data.get("nodes", []):
            rel_file = self.f_id(symbol_node["file"])
            node_copy = dict(symbol_node)
            node_copy["file"] = rel_file             
            self.graph["nodes"].append(node_copy)

            # Create cross-layer boundary edge (FILE -> SYMBOL)
            if rel_file in reg_files:
                self.graph["edges"].append({
                    "source": rel_file ,
                    "target": symbol_node["id"],
                    "type": "CONTAINS"
                })

        # Append Symbol-to-Symbol Interaction Edges
        for symbol_edge in self.symbol_data.get("edges", []):
            self.graph["edges"].append(symbol_edge)

    def save_graph(self) -> None:
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(self.graph, f, indent=2)
        print(f"Indexed {len(self.graph['nodes'])} unified nodes.")
        print(f"Mapped {len(self.graph['edges'])} total semantic edge connections.")
        print(f"Unified Semantic Graph saved to: {os.path.abspath(self.output_path)}")
