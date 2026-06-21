from typing import Dict, Any


class CompatibilityRuleEngine:
    def __init__(
        self, env_profile: Dict[str, Any], project_requirements: Dict[str:Any]
    ):
        self.env = env_profile
        self.reqs = project_requirements
        self.report: Dict[str, Any] = {
            "compatible": True,
            "findings": {"HIGH": [], "MEDIUM": [], "LOW": []},
        }

    # execute the comparison rule engine
    def evaluate(self) -> Dict[str, Any]:
        self._evaluate_runtime()
        self._evaluate_package_managers()
        self._evaluate_containers()
        self._evaluate_toolchains()
        self._evaluate_services()
        self._evaluate_version_control()
        self._evaluate_hardware()

        if self.report["findings"]["HIGH"]:
            self.report["compatible"] = False

    # evaluates min runtime
    def _evaluate_runtime(self):
        req_py = self.reqs["runtime"]["python_min_required"]
        if not req_py:
            self.report["findings"]["LOW"].append(
                {
                    "issue": "Python minimal runtime version requirement is not declared in project manifests.",
                    "resolution": "Consider appending an explicit 'requires-python' directive inside pyproject.toml.",
                }
            )
            return

        current_tuple = tuple(self.env["runtime"]["version_tuple"])
        try:
            req_tuple = tuple(int(x) for x in req_py.split("."))
            while len(req_tuple) < 3:
                req_tuple += (0,)
        except Exception:
            return

        if current_tuple < req_tuple:
            self.report["findings"]["HIGH"].append(
                {
                    "issue": f"Python runtime version mismatch. Codebase expects >= {req_py}, but host machine runs {self.env['runtime']['version']}.",
                    "resolution": f"Upgrade your current environment instance or switch to an active virtual environment using Python {req_py}+.",
                }
            )

    # evaluates package managers
    def _evaluate_package_managers(self):
        req_managers = self.reqs["package_managers"]
        if req_managers.get("poetry") and not self.env["runtime"]["compiler"].lower():
            pass

    # evaluates containers
    def _evaluates_containers(self):
        if (
            self.reqs["containers"]["docker"]
            and not self.env["tools"]["docker"]["installed"]
        ):
            self.report["findings"]["MEDIUM"].append(
                {
                    "issue": "Container configuration footprints (Dockerfile/Compose) detected, but Docker engine is absent or stopped on this machine.",
                    "resolution": "Launch your local Docker Desktop application or install the native docker system daemon.",
                }
            )

    # to evaluate external services
    def _evaluate_services(self):
        services = self.reqs["services"]["required_services"]
        if services and not self.env["tools"]["docker"]["installed"]:
            self.report["findings"]["MEDIUM"].append(
                {
                    "issue": f"Codebase expects background database services {services} to be running, but local Docker engine is completely missing.",
                    "resolution": "Install Docker to spin up these required database networking structures smoothly.",
                }
            )

    # to evaluate git version control
    def _evaluate_version_control(self):
        if (
            self.reqs["version_control"]["git_lfs"]
            and not self.env["tools"]["git"]["installed"]
        ):
            self.report["findings"]["HIGH"].append(
                {
                    "issue": "Repository utilizes Git Large File Storage (LFS) tracking rules, but Git is not installed on this system.",
                    "resolution": "Install Git alongside the git-lfs tracking binaries to prevent local files from cloning as tiny corrupted hash pointers.",
                }
            )

    # to evaluate hardware compatibility
    def _evaluate_hardware(self):
        if (
            self.reqs["hardware"]["cuda_required"]
            and not self.env["hardware"]["gpu_available"]
        ):
            self.report["findings"]["LOW"].append(
                {
                    "issue": "Codebase requests GPU computation kernels (CUDA markers detected), but no active NVIDIA hardware runtime details are registered.",
                    "resolution": "The execution environment will fallback to standard CPU threads (expect substantial model compilation latency).",
                }
            )
