# Arkitekt + Mikro imports
from arkitekt_next import register, easy, progress
from koil.vars import check_cancelled

# OT2 Driver imports
import time
import asyncio
import requests
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib3 import Retry

# Example fallback definitions if not externally available
class PathLike:
    pass


task: Optional[asyncio.Task] = None


class OT2_Config:
    def __init__(
        self,
        ip: str,
        port: int = 31950,
        name: str = "OT2",
        version: str = "2",
        simulate: bool = False,
    ):
        self.ip = ip
        self.port = port
        self.name = name
        self.version = version
        self.simulate = simulate


class RobotStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    FINISHING = "finishing"
    FAILED = "failed"
    PAUSED = "paused"
    OFFLINE = "offline"


class RunStatus(Enum):
    __repr__ = lambda self: self.value

    IDLE = "idle"
    RUNNING = "running"
    FINISHING = "finishing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    PAUSED = "paused"
    STOPPING = "stop-requested"
    STOPPED = "stopped"


class ProtoPiler:
    def __init__(self, template_dir: Optional[Path] = None):
        self.template_dir = template_dir

    def load_config(
        self,
        config_path,
        resource_file=None,
        resource_path=None,
        protocol_out_path=None,
    ):
        pass

    def yaml_to_protocol(
        self,
        config_path,
        resource_file=None,
        resource_file_out=None,
        payload: Optional[Dict[str, Any]] = None,
    ):
        """
        Stub that just returns dummy .py
        """
        proto_out = str(config_path).replace(".yml", ".py")
        return proto_out, str(resource_file_out) if resource_file_out else None


class OT2_Driver:
    def __init__(
        self,
        config: OT2_Config,
        retries: int = 5,
        retry_backoff: float = 1.0,
        retry_status_codes: Optional[List[int]] = None,
    ) -> None:
        self.config: OT2_Config = config
        template_dir = Path(__file__).parent.resolve() / "protopiler/protocol_templates"
        self.protopiler: ProtoPiler = ProtoPiler(template_dir=template_dir)

        self.retry_strategy = Retry(
            total=retries,
            backoff_factor=retry_backoff,
            status_forcelist=retry_status_codes,
        )

        self.base_url = f"http://{self.config.ip}:{self.config.port}"
        self.headers = {"Opentrons-Version": "2"}

        test_conn_url = f"{self.base_url}/robot/lights"
        resp = self._request("get", test_conn_url, headers=self.headers)

        # Toggle lights to confirm connectivity
        if "on" in resp.json() and not resp.json()["on"]:
            self.change_lights_status(status=True)
        else:
            self.change_lights_status(status=False)
            time.sleep(1)
            self.change_lights_status(status=True)

        self.current_run_id = None

    # --------------------------------------------------------------------- #
    # unified request helper
    # --------------------------------------------------------------------- #
    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Unified wrapper for HTTP requests with retry and error handling.
        """
        session = requests.Session()
        adapter_kwargs = {}
        retry_cfg = kwargs.pop("max_retries", self.retry_strategy)
        if retry_cfg:
            adapter_kwargs["max_retries"] = retry_cfg
        session.mount("http://", requests.adapters.HTTPAdapter(**adapter_kwargs))
        session.mount("https://", requests.adapters.HTTPAdapter(**adapter_kwargs))

        try:
            response = session.request(method=method, url=url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as exc:
            print(f"[HTTP {method.upper()}] {url} -> {exc}")
            raise

    # --------------------------------------------------------------------- #
    # protocol compilation & transfer
    # --------------------------------------------------------------------- #
    def compile_protocol(
        self,
        config_path: str,
        resource_file: Optional[str] = None,
        resource_path: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        protocol_out_path: Optional[str] = None,
    ) -> Tuple[str, Optional[str]]:
        if ".py" not in str(config_path):
            self.protopiler.load_config(
                config_path=config_path,
                resource_file=resource_file,
                resource_path=resource_path,
                protocol_out_path=protocol_out_path,
            )
            proto_out, resource_out = self.protopiler.yaml_to_protocol(
                config_path,
                resource_file=resource_file,
                resource_file_out=resource_path,
                payload=payload,
            )
            return proto_out, resource_out
        else:
            return config_path, None

    def transfer(self, protocol_path: str) -> Tuple[str, str]:
        url = f"{self.base_url}/protocols"
        protocol_path = Path(protocol_path)
        with protocol_path.open("rb") as f:
            files = {"files": f}
            resp = self._request("post", url, files=files, headers=self.headers, timeout=600)

        protocol_id = resp.json()["data"]["id"]
        run_url = f"{self.base_url}/runs"
        run_json = {"data": {"protocolId": protocol_id}}
        run_resp = self._request("post", run_url, headers=self.headers, json=run_json)
        run_id = run_resp.json()["data"]["id"]
        return protocol_id, run_id

    def execute(self, run_id: str) -> Dict[str, Dict[str, str]]:
        execute_url = f"{self.base_url}/runs/{run_id}/actions"
        execute_json = {"data": {"actionType": "play"}}
        self._request("post", execute_url, headers=self.headers, json=execute_json)
        return self.get_run(run_id)

    # --------------------------------------------------------------------- #
    # run control helpers
    # --------------------------------------------------------------------- #
    def pause(self, run_id: str):
        url = f"{self.base_url}/runs/{run_id}/actions"
        data = {"data": {"actionType": "pause"}}
        return self._request("post", url, headers=self.headers, json=data)

    def resume(self, run_id: str):
        url = f"{self.base_url}/runs/{run_id}/actions"
        data = {"data": {"actionType": "play"}}
        return self._request("post", url, headers=self.headers, json=data)

    def cancel(self, run_id: str):
        url = f"{self.base_url}/runs/{run_id}/actions"
        data = {"data": {"actionType": "stop"}}
        return self._request("post", url, headers=self.headers, json=data)

    def check_run_status(self, run_id: str) -> RunStatus:
        url = f"{self.base_url}/runs/{run_id}"
        resp = self._request("get", url, headers=self.headers)
        return RunStatus(resp.json()["data"]["status"])

    def get_run(self, run_id: str) -> Dict:
        url = f"{self.base_url}/runs/{run_id}"
        resp = self._request("get", url, headers=self.headers)
        return resp.json()

    def get_run_log(self, run_id: str) -> Dict:
        run_data = self.get_run(run_id)
        commands_url = f"{self.base_url}/runs/{run_id}/commands"
        commands_resp = self._request("get", commands_url, headers=self.headers)
        run_data["commands"] = commands_resp.json()
        return run_data

    # --------------------------------------------------------------------- #
    # robot status helpers
    # --------------------------------------------------------------------- #
    def get_runs(self) -> Optional[List[Dict[str, str]]]:
        runs_url = f"{self.base_url}/runs"
        runs_resp = self._request("get", runs_url, headers=self.headers)
        runs_simplified = [
            {
                "runID": run["id"],
                "protocolID": run.get("protocolId"),
                "status": run["status"],
                "current": run["current"],
            }
            for run in runs_resp.json()["data"]
        ]
        return runs_simplified

    def get_robot_status(self) -> RobotStatus:
        runs = self.get_runs()
        if not runs:
            return RobotStatus.OFFLINE
        for run in runs:
            if run["status"] in [elem.value for elem in RunStatus]:
                if run["status"] not in ["succeeded", "stop-requested", "stopped"]:
                    return RobotStatus(run["status"])
        return RobotStatus.IDLE

    def reset_robot_data(self):
        delete_url = f"{self.base_url}/runs/"
        runs = self.get_runs()
        if runs:
            for run in runs:
                if run["status"] == "failed":
                    self._request("delete", delete_url + run["runID"], headers=self.headers)

    def change_lights_status(self, status: bool = False):
        url = f"{self.base_url}/robot/lights"
        payload = {"on": status}
        self._request("post", url, headers=self.headers, json=payload)

    # --------------------------------------------------------------------- #
    # generic & streaming helpers
    # --------------------------------------------------------------------- #
    def send_request(self, request_extension: str, **kwargs) -> requests.Response:
        request_extension = request_extension.lstrip("/")
        url = f"{self.base_url}/{request_extension}"
        headers = kwargs.pop("headers", {"Opentrons-Version": "2"})
        method = kwargs.pop("method", None)
        if method is None:
            raise Exception("Please provide an HTTP request method via `method=` keyword.")
        return self._request(method, url, headers=headers, **kwargs)

    def stream(
        self,
        command: str,
        params: dict,
        run_id: Optional[str] = None,
        execute: bool = True,
        intent: str = "setup",
    ) -> str:
        if not run_id:
            run_resp = self._request(
                "post",
                f"{self.base_url}/runs",
                headers=self.headers,
                json={"data": {}},
            )
            run_id = run_resp.json()["data"]["id"]

        enqueue_payload = {"data": {"commandType": command, "params": params, "intent": intent}}
        self._request(
            "post",
            f"{self.base_url}/runs/{run_id}/commands",
            headers=self.headers,
            json=enqueue_payload,
        )

        if execute:
            self._request(
                "post",
                f"{self.base_url}/runs/{run_id}/actions",
                headers=self.headers,
                json={"data": {"actionType": "play"}},
            )
        return run_id


# ------------------------------------------------------------------------- #
# Helper functions
# ------------------------------------------------------------------------- #
driver = OT2_Driver(
    config=OT2_Config(
        ip="192.168.5.156",
        port=31950,
    )
)


def watch_run_completion(run_id: str) -> Dict:
    while True:
        status = driver.check_run_status(run_id)
        if status in [RunStatus.SUCCEEDED, RunStatus.FAILED, RunStatus.STOPPED]:
            break
        try:
            check_cancelled()
        except Exception:
            driver.cancel(run_id)
            while True:
                status = driver.check_run_status(run_id)
                if status in [RunStatus.FAILED, RunStatus.STOPPED]:
                    break
                time.sleep(1)
        time.sleep(1)
    return driver.get_run_log(run_id)


async def await_staining_result() -> Optional[Dict]:
    global task
    if task is None:
        return None
    return await task


# ------------------------------------------------------------------------- #
# Arkitekt registered functions
# ------------------------------------------------------------------------- #
@register
def run_washing_protocol():
    protocol_id, run_id = driver.transfer(protocol_path="./OT2Driver/protocols/washing.py")
    driver.current_run_id = run_id
    progress(0, f"Protocol-ID: {protocol_id}")
    driver.execute(run_id)
    watch_run_completion(run_id)


@register
def run_staining_protocol():
    protocol_id, run_id = driver.transfer(protocol_path="./OT2Driver/protocols/staining.py")
    driver.current_run_id = run_id
    progress(0, f"Protocol-ID: {protocol_id} started")
    driver.execute(run_id)
    watch_run_completion(run_id)


@register
def run_dummy_protocol():
    protocol_id, run_id = driver.transfer(protocol_path="./OT2Driver/protocols/dummy.py")
    driver.current_run_id = run_id
    progress(0, f"Protocol-ID: {protocol_id} started")
    driver.execute(run_id)
    watch_run_completion(run_id)


@register
def get_run_status() -> RunStatus:
    return driver.check_run_status(run_id=driver.current_run_id)


# ------------------------------------------------------------------------- #
# Arkitekt provisioning
# ------------------------------------------------------------------------- #
with easy("OT2", url="go.arkitekt.live") as e:
    e.run()
