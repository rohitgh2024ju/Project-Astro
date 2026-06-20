import platform
import os
import sys
import shutil
import subprocess
import re
from datetime import datetime
from typing import Dict, Any
import json


class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"


class EnvironmentDiscoveryEngine:
    def __init__(self, astro_dir: str = ".astro"):
        self.profile: Dict[str, Any] = {}
        self.astro_dir = astro_dir
        self.cache_path = os.path.join(astro_dir, "env_profile.json")


    def get_profile(self, force_refresh: bool = False) -> Dict[str, Any]:
        if not force_refresh and os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, "r") as f:
                    profile = json.load(f)

                # Structural schema validation matching target layout
                if profile and profile.get("schema_version") == 1:
                    self.profile = profile

                    profile_time = datetime.fromisoformat(profile["metadata"]["generated_at"])
                    current_time = datetime.now()

                    delta = (current_time- profile_time).days

                    return self.profile, delta
            except Exception:
                pass

        return self.refresh_cache()

    def refresh_cache(self) -> Dict[str, Any]:
        if not os.path.exists(self.astro_dir):
            os.makedirs(self.astro_dir, exist_ok=True)

        self.profile = self.collect_profile()

        with open(self.cache_path, "w") as f:
            json.dump(self.profile, f, indent=2)

        print(
            f"{Color.GREEN}{Color.BOLD}Environment Metadata is saved successfully at {self.cache_path}{Color.RESET}"
        )
        return self.profile, 0

    def collect_profile(self) -> Dict[str, Any]:
        return {
            "schema_version": 1,
            "metadata": {
                "generated_at": datetime.datetime.now().isoformat(timespec="seconds")
            },
            "os": self._get_os_info(),
            "runtime": self._get_runtime_info(),
            "hardware": self._get_hardware_info(),
            "tools": {
                "docker": self._get_tool_details(
                    "docker", ["docker", "--version"], r"version\s+([\d\.]+)"
                ),
                "git": self._get_tool_details(
                    "git", ["git", "--version"], r"git\s+version\s+(\d+\.\d+\.\d+)"
                ),
                "gcc": self._get_tool_details(
                    "gcc", ["gcc", "--version"], r"gcc(?:\.exe)?.*?(\d+\.\d+\.\d+)"
                ),
                "nvcc": self._get_tool_details(
                    "nvcc", ["nvcc", "--version"], r"release\s+([\d\.]+)"
                ),
            },
        }

    def _get_os_info(self) -> Dict[str, str]:
        return {
            "platform": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "architecture": platform.machine(),
        }

    def _get_runtime_info(self) -> Dict[str, Any]:
        return {
            "interpreter": platform.python_implementation(),
            "version": platform.python_version(),
            "version_tuple": list(sys.version_info[:3]),
            "compiler": platform.python_compiler(),
        }

    def _get_hardware_info(self) -> Dict[str, Any]:
        info = {
            "total_ram_gb": self._get_total_ram(),
            "gpu_available": False,
            "gpu_details": None,  # Matched target JSON data type default
        }

        if shutil.which("nvidia-smi"):
            try:
                res = subprocess.run(
                    ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                if res.returncode == 0 and res.stdout.strip():
                    info["gpu_available"] = True
                    info["gpu_details"] = res.stdout.strip()
            except Exception:
                pass
        return info

    def _get_total_ram(self) -> float:
        try:
            return round(
                os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / (1024**3), 2
            )
        except (ValueError, AttributeError):
            pass

        if platform.system() == "Windows":
            try:
                res = subprocess.run(
                    [
                        "powershell",
                        "-Command",
                        "(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory",
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                if res.returncode == 0 and res.stdout.strip().isdigit():
                    return round(int(res.stdout.strip()) / (1024**3), 2)
            except Exception:
                pass

        return -1.0

    def _get_tool_details(
        self, name: str, cmd: list, version_regex: str
    ) -> Dict[str, Any]:
        details = {"installed": False, "version": None}

        if shutil.which(name):
            details["installed"] = True
            try:
                res = subprocess.run(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                output = res.stdout + res.stderr
                match = re.search(version_regex, output, re.IGNORECASE)
                if match:
                    details["version"] = match.group(1)
            except Exception:
                pass

        return details

    # Run engine entry point
    def run(self, force_refresh: bool = False) -> Dict[str, Any]:
        return self.get_profile(force_refresh)


"""
{
  "schema_version": 1,

  "metadata": {
    "generated_at": "2026-06-20T20:00:00"
  },

  "os": {
    "platform": "Windows",
    "release": "10",
    "version": "10.0.26100",
    "architecture": "AMD64"
  },

  "runtime": {
    "interpreter": "CPython",
    "version": "3.9.13",
    "version_tuple": [3, 9, 13],
    "compiler": "MSC v.1929 64 bit (AMD64)"
  },

  "hardware": {
    "total_ram_gb": 15.7,
    "gpu_available": false,
    "gpu_details": null
  },

  "tools": {
    "docker": {
      "installed": false,
      "version": null
    },

    "git": {
      "installed": true,
      "version": "2.50.1"
    },

    "gcc": {
      "installed": true,
      "version": "14.2.0"
    },

    "nvcc": {
      "installed": false,
      "version": null
    }
  }
}
"""
