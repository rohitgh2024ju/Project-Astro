import json
import os
from typing import Dict, List, Any, Optional

class SymbolDependencyEngine:
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.metadata_path = os.path.join(workspace_root, ".astro", "files_metadata.json")
        self.output_path = os.path.join(workspace_root, ".astro", "symbol_graph.astro") 
          
        self.metadata_data: Dict[str,Any] = {}
        self.file_graph: Dict[str,list[str]] = {}
    
        self.local_def: Dict[str,list[Dict[str,Any]]] = {}
        self.symbol: Dict[str,Dict[str,Any]] = {}
        
        self.graph = {
            "nodes": [],
            "edges": []
        }

    def run(self) -> None:
        self._load_metadata()
        self._build_global_definition()
        self._edge_creation()   
        self._save_graph()


    def _load_metadata(self) -> None:
        if not os.path.exists(self.metadata_path):
            raise FileNotFoundError(f"Parser metadata missing at: {self.metadata_path}")    
        with open(self.metadata_path, "r", encoding="utf-8") as f:
            self.metadata_data = json.load(f)
        print(f"Loaded metadata for {len(self.metadata_data)} files.")


    def _generate_name(self, file_path: str, symbol_path: str) -> str:
        rel_path = os.path.relpath(file_path, self.workspace_root).replace(os.sep, "/")
        return f"absolute::{rel_path}::{symbol_path}"


    def _resolve_path(self, current_file: str, module_name: str) -> Optional[str]:
        cleaned_module = module_name.lstrip(".")
        relative_path = cleaned_module.replace(".", os.sep) + ".py"
        target_path = os.path.abspath(os.path.join(self.workspace_root, relative_path))
        if target_path in self.metadata_data:
            return target_path    
        current_dir = os.path.dirname(current_file)
        target_path = os.path.abspath(os.path.join(current_dir, relative_path))
        if target_path in self.metadata_data:
            return target_path           
        return None


    # PART-1:Creating the nodes
    def _build_global_definition(self) -> None:
        """
        Scans all files to register declared classes, functions, methods, and
        global state variables into a global indexed namespace.
        """
        for file_path, file_meta in self.metadata_data.items():
            self.local_def[file_path] = []
            definitions = file_meta.get("definitions", {})
            # Extract Classes
            class_defs = definitions.get("class_definition", {})
            for class_name, class_meta in class_defs.items():
                class_id = self._generate_name(file_path, class_name)
                class_node = {
                    "id": class_id,
                    "name": class_name,
                    "kind": "CLASS",
                    "file": file_path,
                    "meta": class_meta
                }
                self.symbol[class_id] = class_node
                self.graph["nodes"].append(class_node)
                self.local_def[file_path].append(class_node)

            # Extract Functions
            func_defs = definitions.get("function_definition", {})
            for func_name, func_meta in func_defs.items():
                func_id = self._generate_name(file_path, func_name)
                func_node = {
                    "id": func_id,
                    "name": func_name,
                    "kind": "FUNCTION",
                    "file": file_path,
                    "meta": func_meta
                }
                self.symbol[func_id] = func_node
                self.graph["nodes"].append(func_node)
                self.local_def[file_path].append(func_node)
                
    #PART-2:Defining the relationship edges
    def _edge_creation(self) -> None:
        for file_path, file_meta in self.metadata_data.items():
            
            # 1. Maps local imports tracking external bindings
            imports_store: Dict[str, str] = {}
            dependencies = file_meta.get("dependencies", {})
            for module_name, symbols in dependencies.items():
                target_path = self._resolve_path(file_path, module_name)
                if target_path:
                    for sym_name in symbols:
                        target_name = self._generate_name(target_path, sym_name)
                        imports_store[sym_name] = target_name

            # 2. Links CALLS in form of edges
            calls_block = file_meta.get("calls",{})
            for caller_name,call_list in calls_block.items():
                caller_name = self._generate_name(file_path, caller_name)
                if caller_name in self.symbol:
                    for call_site in call_list:
                        called_symbol = call_site.get("name")
                        if called_symbol:
                            resolved_name = self._resolve_symbols(file_path, called_symbol,imports_store)
                            if resolved_name:
                                self.graph["edges"].append({
                                    "source": caller_name,
                                    "target": resolved_name,
                                    "type": "CALLS"
                                })

    
    def _resolve_symbols(self, file_path: str, symbol_name: str,imports_store: Dict[str, str]) -> Optional[str]:
        # 1.Checking if the name references an imported symbol
        if symbol_name in imports_store:
            target_name = imports_store[symbol_name]
            if target_name in self.symbol:
                return target_name

        # 2. Check if the name is defined locally
        local_name = self._generate_name(file_path, symbol_name)
        if local_name in self.symbol:
            return local_name

        # 3. Check for sub-nested structures(e.g.:ClassName.method)
        if "." in symbol_name:
            root_name = symbol_name.split(".")[0]
            if root_name in imports_store:
                base_name = imports_store[root_name]
                base_node = self.symbol.get(base_name)
                if base_node:
                    suffix_name = symbol_name[len(root_name)+1:]
                    nested_name = self._generate_name(base_node["file"], f"{base_node['name']}.{suffix_name}")
                    if nested_name in self.symbol:
                        return nested_name
        return None


    def _save_graph(self) -> None:
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)        
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(self.graph, f, indent=2)
        print(f"Indexed {len(self.graph['nodes'])} symbol nodes.")
        print(f"Mapped {len(self.graph['edges'])} structural symbol relationships.")
        print(f"Symbol Dependency Graph saved to: {self.output_path}")
