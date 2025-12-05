# Arkitekt + Mikro imports
from arkitekt_next import register, easy, progress, log
from koil.vars import check_cancelled

# OT2 Driver imports
import time
import asyncio
import requests
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib3 import Retry
from dotenv import load_dotenv
import os

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


# ------------------------------------------------------------------------- #
# Arkitekt registered functions
# ------------------------------------------------------------------------- #
@register
def run_washing_protocol():
    log("run_washing_protocol started")
    print("run_washing_protocol started")
    time.sleep(1)
    log("run_washing_protocol finished")
    print("run_washing_protocol finished")


@register
def run_staining_protocol():
    log("run_staining_protocol started")
    print("run_staining_protocol started")
    time.sleep(1)
    log("run_staining_protocol finished")
    print("run_staining_protocol finished")


@register
def run_dummy_protocol():
    log("run_dummy_protocol started")
    print("run_dummy_protocol started")
    time.sleep(1)
    log("run_dummy_protocol finished")
    print("run_dummy_protocol finished")


@register
def get_run_status() -> RunStatus:
    log("get_run_status started")
    print("get_run_status started")
    time.sleep(1)
    log("get_run_status finished")
    print("get_run_status finished")
    return RunStatus.IDLE


# ------------------------------------------------------------------------- #
# Arkitekt provisioning
# ------------------------------------------------------------------------- #
if __name__ == "__main__":
    load_dotenv()
    app_name = os.getenv("ARKITEKT_APPNAME", "OT2")
    if app_name == "":
        print(
            "ARKITEKT_APPNAME is not set. Please set the ARKITEKT_APPNAME environment variable. For example put it in .env file."
        )
        exit(1)
    app_url = os.getenv("ARKITEKT_URL", "go.arkitekt.live")
    app = easy(identifier=app_name, url=app_url, redeem_token=os.getenv("REDEEM_TOKEN"))
    app.enter()
    app.run()
