import platform
import os
import sys
import shutil
import subprocess
from typing import Dict, Any
import json


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


# Analyze and collects telemetry from host machine to build environment profile
class EnvironmentDiscoveryEngine:
    def __init__(self, astro_dir: str = ".astro"):
        self.profile: Dict[str, Any] = {}
        self.astro_dir = astro_dir
        self.cache_path = os.path.join(astro_dir, "env_profile.json")

    # Get existing profile otherwise scan system
    def get_profile(self, force_refresh: bool = False) -> Dict[str, Any]:
        if not force_refresh and os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, "r") as f:
                    profile = json.load(f)
                if profile:
                    self.profile = profile
                    return self.profile
            except Exception:  # Corrupted or unparsable file
                pass

        return self.refresh_cache()

    # Refresh cache profile
    def refresh_cache(self) -> Dict[str, Any]:
        if not os.path.exists(self.astro_dir):
            os.makedirs(self.astro_dir, exist_ok=True)

        self.profile = self.collect_profile()

        with open(self.cache_path, "w") as f:
            json.dump(self.profile, f, indent=2)

        print(
            f"{Color.GREEN}{Color.BOLD}Environment Metadata is saved successfully at {self.cache_path}{Color.RESET}"
        )
        return self.profile

    # Returns all unified environment profile
    def collect_profile(self) -> Dict[str, Any]:
        profile = {
            "os": self._get_os_info(),
            "runtime": self._get_runtime_info(),
            "hardware": self._get_hardware_info(),
            "tools": self._get_tools_available(),
        }

        return profile

    # Get os info
    def _get_os_info(self) -> Dict[str, str]:
        return {
            "platform": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "architecture": platform.machine(),
        }

    # Get runtime info
    def _get_runtime_info(self) -> Dict[str, Any]:
        return {
            "interpreter": platform.python_implementation(),
            "version": platform.python_version(),
            "version_tuple": list(sys.version_info[:3]),
            "compiler": platform.python_compiler(),
        }

    # Get hardware info
    def _get_hardware_info(self) -> Dict[str, Any]:
        info = {
            "total_ram_gb": self._get_total_ram(),
            "gpu_available": False,
            "gpu_details": "None",
        }

        if shutil.which("nvidia-smi"):
            try:
                res = subprocess.run(
                    ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                if res.returncode == 0:
                    info["gpu_available"] = True
                    info["gpu_details"] = res.stdout.strip()
            except Exception:
                pass
        return info

    # Get total ram info across all os
    def _get_total_ram(self) -> float:
        try:
            # POSIX Standard Path (Linux / macOS)
            return round(
                os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / (1024**3), 2
            )
        except (ValueError, AttributeError):
            pass

        # Robust Windows Path (Handles wmic deprecation)
        if platform.system() == "Windows":
            try:
                # Fallback to standard PowerShell query - completely native on Windows
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
                    bytes_ram = int(res.stdout.strip())
                    return round(bytes_ram / (1024**3), 2)
            except Exception:
                pass

            # Deprecated WMIC legacy path as a secondary fallback
            try:
                res = subprocess.run(
                    ["wmic", "ComputerSystem", "get", "TotalPhysicalMemory"],
                    stdout=subprocess.PIPE,
                    text=True,
                )
                lines = res.stdout.strip().split("\n")
                if len(lines) > 1 and lines[1].strip().isdigit():
                    bytes_ram = int(lines[1].strip())
                    return round(bytes_ram / (1024**3), 2)
            except Exception:
                pass

        return -1.0

    # Get external service tools
    def _get_tools_available(self) -> Dict[str, bool]:
        return {
            "docker": shutil.which("docker") is not None,
            "git": shutil.which("git") is not None,
            "gcc": shutil.which("gcc") is not None,
            "nvcc": shutil.which("nvcc") is not None,
        }

    # Run engine entry point
    def run(self, force_refresh: bool = False) -> Dict[str, Any]:
        return self.get_profile(force_refresh)
