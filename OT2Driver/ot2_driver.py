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

# If your environment doesn't already have these, define them or adjust import paths
# from config import OT2_Config, PathLike, parse_ot2_args
# from protopiler.protopiler import ProtoPiler

# Example fallback definitions if not externally available
# Comment out if you already have them from your local modules
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
        resp = requests.get(test_conn_url, headers=self.headers)

        if resp.status_code != 200:
            raise RuntimeError(f"Could not connect to opentrons at {self.base_url}")

        # Toggle lights to confirm connectivity
        if "on" in resp.json() and not resp.json()["on"]:
            self.change_lights_status(status=True)
        else:
            self.change_lights_status(status=False)
            time.sleep(1)
            self.change_lights_status(status=True)

        self.current_run_id = None

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
            resp = requests.post(url=url, files=files, headers=self.headers, timeout=600)

        print(resp.json())
        protocol_id = resp.json()["data"]["id"]
        run_url = f"{self.base_url}/runs"
        run_json = {"data": {"protocolId": protocol_id}}
        run_resp = requests.post(run_url, headers=self.headers, json=run_json)
        run_id = run_resp.json()["data"]["id"]
        return protocol_id, run_id

    def execute(self, run_id: str) -> Dict[str, Dict[str, str]]:
        execute_url = f"{self.base_url}/runs/{run_id}/actions"
        execute_json = {"data": {"actionType": "play"}}
        execute_run_resp = requests.post(execute_url, headers=self.headers, json=execute_json)

        if execute_run_resp.status_code != 201:
            print(f"Could not run play action on {run_id}")
            print(execute_run_resp.json())

        # while self.check_run_status(run_id) not in {
        #     RunStatus.FAILED,
        #     RunStatus.SUCCEEDED,
        #     RunStatus.STOPPED,
        # }:
        #     time.sleep(1)

        return self.get_run(run_id)

    def pause(self, run_id: str):
        url = f"{self.base_url}/runs/{run_id}/actions"
        data = {"data": {"actionType": "pause"}}
        return requests.post(url, headers=self.headers, json=data)

    def resume(self, run_id: str):
        url = f"{self.base_url}/runs/{run_id}/actions"
        data = {"data": {"actionType": "play"}}
        return requests.post(url, headers=self.headers, json=data)

    def cancel(self, run_id: str):
        url = f"{self.base_url}/runs/{run_id}/actions"
        data = {"data": {"actionType": "stop"}}
        return requests.post(url, headers=self.headers, json=data)

    def check_run_status(self, run_id: str) -> RunStatus:
        url = f"{self.base_url}/runs/{run_id}"
        resp = requests.get(url, headers=self.headers)
        status = RunStatus(resp.json()["data"]["status"])
        return status

    def get_run(self, run_id: str) -> Dict:
        url = f"{self.base_url}/runs/{run_id}"
        resp = requests.get(url, headers=self.headers)
        return resp.json()

    def get_run_log(self, run_id: str) -> Dict:
        run_data = self.get_run(run_id)
        commands_url = f"{self.base_url}/runs/{run_id}/commands"
        commands_resp = requests.get(commands_url, headers=self.headers)
        run_data["commands"] = commands_resp.json()
        return run_data

    def get_runs(self) -> Optional[List[Dict[str, str]]]:
        runs_url = f"{self.base_url}/runs"
        runs_resp = requests.get(runs_url, headers=self.headers)
        if runs_resp.status_code == 200:
            runs_simplified = []
            for run in runs_resp.json()["data"]:
                runs_simplified.append(
                    {
                        "runID": run["id"],
                        "protocolID": run.get("protocolId"),
                        "status": run["status"],
                        "current": run["current"],
                    }
                )
            return runs_simplified
        return None

    def get_robot_status(self) -> RobotStatus:
        runs = self.get_runs()
        if not runs:
            return RobotStatus.OFFLINE
        for run in runs:
            if run["status"] in [elem.value for elem in RunStatus]:
                # if it's not succeeded or stopped
                if run["status"] not in ["succeeded", "stop-requested", "stopped"]:
                    return RobotStatus(run["status"])
        return RobotStatus.IDLE

    def reset_robot_data(self):
        delete_url = f"{self.base_url}/runs/"
        runs = self.get_runs()
        if runs:
            for run in runs:
                if run["status"] == "failed":
                    requests.delete(url=delete_url + run["runID"], headers=self.headers)

    def change_lights_status(self, status: bool = False):
        url = f"{self.base_url}/robot/lights"
        payload = {"on": status}
        requests.post(url, headers=self.headers, json=payload)

    def send_request(self, request_extension: str, **kwargs) -> requests.Response:
        request_extension = request_extension if request_extension[0] != "/" else request_extension[1:]
        url = f"{self.base_url}/{request_extension}"
        if "headers" not in kwargs:
            kwargs["headers"] = {"Opentrons-Version": "2"}
        if "method" not in kwargs:
            raise Exception("Please provide an HTTP request method via `method=` keyword.")
        kwargs["method"] = kwargs["method"].upper()
        return requests.request(url=url, **kwargs)

    def stream(self, command: str, params: dict, run_id: Optional[str] = None, execute: bool = True, intent: str = "setup") -> str:
        if not run_id:
            run_resp = requests.post(
                url=f"{self.base_url}/runs", headers=self.headers, json={"data": {}}, max_retries=self.retry_strategy
            )
            run_id = run_resp.json()["data"]["id"]

        enqueue_payload = {"data": {"commandType": command, "params": params, "intent": intent}}
        enqueue_resp = requests.post(
            url=f"{self.base_url}/runs/{run_id}/commands",
            headers=self.headers,
            json=enqueue_payload,
            max_retries=self.retry_strategy,
        )

        if execute:
            execute_command_resp = requests.post(
                url=f"{self.base_url}/runs/{run_id}/actions",
                headers=self.headers,
                json={"data": {"actionType": "play"}},
                max_retries=self.retry_strategy,
            )
        return run_id

# Create a global driver instance
driver = OT2_Driver(
    config=OT2_Config(
        ip="169.254.254.239",  # set your OT2 IP here
        port=31950
    )
)
def watch_run_completion(run_id: str) -> Dict:
    """
    Watches a run until it completes or fails.
    """
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
    """
    Waits for the staining protocol to complete and returns run log.
    """
    global task
    if task is None:
        return None
    return await task

@register
def run_washing_protocol():
    """
    Run the washing protocol on the OT2
    """
    protocol_id, run_id = driver.transfer(protocol_path="./OT2Driver/protocols/washing.py")
    driver.current_run_id = run_id
    progress(0, f"Protocol-ID: {protocol_id}")
    print(f"Run-ID: {run_id}")
    driver.execute(run_id)
    watch_run_completion(run_id)

@register
def run_staining_protocol():
    """
    Run the staining protocol on the OT2
    """
    protocol_id, run_id = driver.transfer(protocol_path="./OT2Driver/protocols/staining.py")
    driver.current_run_id = run_id
    progress(0, f"Protocol-ID: {protocol_id} started")
    print(f"Run-ID: {run_id}")
    driver.execute(run_id)
    watch_run_completion(run_id)

@register
def run_dummy_protocol():
    """
    Run a quick dummy protocol on the OT2
    """
    protocol_id, run_id = driver.transfer(protocol_path="./OT2Driver/protocols/dummy.py")
    driver.current_run_id = run_id
    progress(0, f"Protocol-ID: {protocol_id} started")
    print(f"Run-ID: {run_id}")
    driver.execute(run_id)
    watch_run_completion(run_id)

@register
def get_run_status() -> RunStatus:
    """
    Get the status of the current run
    """
    run_status = driver.check_run_status(run_id=driver.current_run_id)
    return run_status

# Start Arkitekt provisioning
with easy("OT2", url="go.arkitekt.live") as e:
    e.run()
