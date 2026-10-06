"""Opentrons OT-2 as an Arkitekt app.

Uploads a protocol to the OT-2 over its HTTP API (port 31950), runs it and waits until it has
finished. config.yaml names the robot and the protocols that run_protocol offers.

Run:  uv run app.py   then open http://localhost:8080/ to bind it.
OT2_CONFIG picks another config.yaml (default: next to this file).
Without a robot: uv run scripts/ot2_mock_rest.py, and set ot2.ip to 127.0.0.1.
"""

import os
import shutil
import threading
from pathlib import Path
from typing import Annotated

import koil
import yaml
from arkitekt import App, Description, Effects, Task
from arkitekt.widgets import withChoices

from arkitekt_bind import serve
from OT2Driver.ot2_driver import OT2_Config, OT2_Driver, RunStatus

HERE = Path(__file__).resolve().parent
CONFIG = Path(os.getenv("OT2_CONFIG", HERE / "config.yaml"))

if not CONFIG.exists():  # first start: copy the defaults where they can be edited
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(HERE / "config.example.yaml", CONFIG)
cfg = yaml.safe_load(CONFIG.read_text())
PROTOCOLS = cfg["protocols"]
FINISHED = (RunStatus.SUCCEEDED, RunStatus.FAILED, RunStatus.STOPPED)

app = App(cfg.get("app", "ot2windy"), "1.0.0", effects=Effects.IRREVERSIBLE)

Protocol = Annotated[str, withChoices(*PROTOCOLS), Description("Protocol from config.yaml")]

_driver = None
_driver_lock = threading.Lock()


def driver() -> OT2_Driver:
    """The connection to the OT-2, opened on first use (it blinks the lights once)."""
    global _driver
    with _driver_lock:
        if _driver is None:
            ot2 = cfg["ot2"]
            _driver = OT2_Driver(OT2_Config(ip=ot2["ip"], port=ot2.get("port", 31950)))
        return _driver


def protocol_file(name: str) -> Path:
    """protocols/<file> next to config.yaml, else the protocol shipped with the app."""
    if name not in PROTOCOLS:
        raise ValueError(f"Unknown protocol {name!r}; config.yaml has {list(PROTOCOLS)}")
    for folder in (CONFIG.parent / "protocols", HERE / "OT2Driver" / "protocols"):
        if (folder / PROTOCOLS[name]).exists():
            return folder / PROTOCOLS[name]
    raise FileNotFoundError(f"{PROTOCOLS[name]} is in neither {CONFIG.parent / 'protocols'} "
                            f"nor the protocols shipped with the app")


@app.action(locks=["ot2"])
def run_protocol(protocol: Protocol, *, task: Task) -> str:
    """Run Protocol

    Uploads the protocol, runs it and waits until the OT-2 has finished. Returns the run id.
    Cancelling the task stops the run on the robot.
    """
    ot2 = driver()
    protocol_id, run_id = ot2.transfer(str(protocol_file(protocol)))
    ot2.current_run_id = run_id
    task.log(f"{protocol}: protocol {protocol_id}, run {run_id}")
    ot2.execute(run_id)
    status = None
    try:
        while status not in FINISHED:
            koil.sleep(cfg.get("poll_interval", 1))
            new = ot2.check_run_status(run_id)
            if new != status:
                task.log(f"Run {run_id}: {new.value}")
                status = new
    except BaseException:
        ot2.cancel(run_id)  # cancelled (or the robot stopped answering): stop the run too
        raise
    if status != RunStatus.SUCCEEDED:
        raise RuntimeError(f"{protocol} ended {status.value} (run {run_id})")
    return run_id


@app.action
def get_robot_status() -> str:
    """Robot Status

    idle, running, paused, finishing, failed or offline.
    """
    return driver().get_robot_status().value


@app.action
def set_lights(on: bool = True) -> None:
    """Set Lights

    Switches the deck lights: a quick check that the OT-2 is reachable.
    """
    driver().change_lights_status(status=on)


if __name__ == "__main__":
    serve(app, CONFIG, int(os.getenv("PORT", "8080")))
