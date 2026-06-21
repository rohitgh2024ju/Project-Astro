import os
import re
from typing import Dict, Any, List, Optional


class RequirementDiscoveryEngine:
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root

    def discover(self) -> Dict[str, Any]:
        return {
            "schema_version": 1,
            "runtime": {"python_min_required": self._discover_python_runtime()},
            "package_managers": self._discover_package_managers(),
            "toolchains": self._discover_toolchains(),
            "containers": self._discover_containers(),
            "services": self._discover_services(),
            "version_control": self._discover_vc_requirements(),
            "hardware": self._discover_hardware_demands(),
        }

    def _discover_python_runtime(self) -> Optional[str]:
        """Looks for python runtime limits. Returns None if completely undeclared."""
        toml_path = os.path.join(self.workspace_root, "pyproject.toml")
        if os.path.exists(toml_path):
            try:
                with open(toml_path, "r", encoding="utf-8") as f:
                    match = re.search(
                        r'requires-python\s*=\s*["\'](?:>=)?\s*([\d\.]+)["\']', f.read()
                    )
                    if match:
                        return match.group(1)
            except Exception:
                pass
        return None

    def _discover_package_managers(self) -> Dict[str, bool]:
        return {
            "poetry": os.path.exists(os.path.join(self.workspace_root, "poetry.lock")),
            "uv": os.path.exists(os.path.join(self.workspace_root, "uv.lock")),
            "pip": os.path.exists(
                os.path.join(self.workspace_root, "requirements.txt")
            ),
        }

    def _discover_toolchains(self) -> Dict[str, bool]:
        has_makefile = os.path.exists(os.path.join(self.workspace_root, "Makefile"))
        has_compiled_backend = False
        toml_path = os.path.join(self.workspace_root, "pyproject.toml")

        if os.path.exists(toml_path):
            try:
                with open(toml_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    has_compiled_backend = any(
                        b in content
                        for b in ["maturin", "setuptools-rust", "scikit-build"]
                    )
            except Exception:
                pass

        return {"gcc": has_makefile or has_compiled_backend}

    def _discover_containers(self) -> Dict[str, bool]:
        has_dockerfile = os.path.exists(os.path.join(self.workspace_root, "Dockerfile"))
        has_compose = any(
            os.path.exists(os.path.join(self.workspace_root, f))
            for f in ["docker-compose.yml", "docker-compose.yaml"]
        )
        return {"docker": has_dockerfile or has_compose}

    def _discover_services(self) -> Dict[str, List[str]]:
        """Scans both .env.example configuration files AND docker-compose definitions for service indicators."""
        detected = set()
        target_services = ["postgres", "redis", "mongodb", "mysql", "elasticsearch"]

        # Scan Path A: .env.example file keywords
        env_path = os.path.join(self.workspace_root, ".env.example")
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    content = f.read().lower()
                    for service in target_services:
                        if service in content:
                            detected.add(service)
            except Exception:
                pass

        # Scan Path B: Docker-compose layout blocks
        for compose_file in ["docker-compose.yml", "docker-compose.yaml"]:
            compose_path = os.path.join(self.workspace_root, compose_file)
            if os.path.exists(compose_path):
                try:
                    with open(compose_path, "r", encoding="utf-8") as f:
                        content = f.read().lower()
                        for service in target_services:
                            if re.search(rf"\b{service}\b", content):
                                detected.add(service)
                except Exception:
                    pass

        return {"required_services": sorted(list(detected))}

    def _discover_vc_requirements(self) -> Dict[str, bool]:
        has_lfs = False
        attr_path = os.path.join(self.workspace_root, ".gitattributes")

        if os.path.exists(attr_path):
            try:
                with open(attr_path, "r", encoding="utf-8") as f:
                    if "filter=lfs" in f.read():
                        has_lfs = True
            except Exception:
                pass

        return {
            "submodules": os.path.exists(
                os.path.join(self.workspace_root, ".gitmodules")
            ),
            "git_lfs": has_lfs,
        }

    def _discover_hardware_demands(self) -> Dict[str, bool]:
        req_path = os.path.join(self.workspace_root, "requirements.txt")
        has_cuda = False

        if os.path.exists(req_path):
            try:
                with open(req_path, "r", encoding="utf-8") as f:
                    content = f.read().lower()
                    gpu_keywords = [
                        "nvidia",
                        "cuda",
                        "cudnn",
                        "pytorch-cuda",
                        "cu11",
                        "cu12",
                    ]
                    if any(kw in content for kw in gpu_keywords):
                        has_cuda = True
            except Exception:
                pass

        return {"cuda_required": has_cuda}


"""
{
  "schema_version": 1,
  "runtime": {
    "python_min_required": "3.11"
  },
  "package_managers": {
    "poetry": true,
    "uv": false,
    "pip": false
  },
  "toolchains": {
    "gcc": true
  },
  "containers": {
    "docker": true
  },
  "services": {
    "required_services": [
      "postgres",
      "redis"
    ]
  },
  "version_control": {
    "submodules": false,
    "git_lfs": true
  },
  "hardware": {
    "cuda_required": true
  }
}
"""
