# fastapi_opentrons_sim.py
#
# Run:
#   uvicorn fastapi_opentrons_sim:app --host 0.0.0.0 --port 8000 --reload
#
# This simulates a minimal subset of the Opentrons HTTP API v2.

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
import uuid
import uvicorn

app = FastAPI(title="Opentrons-Sim")

# In-memory store
lights_state = {"on": True}
protocols_db: Dict[str, dict] = {}
runs_db: Dict[str, dict] = {}
commands_db: Dict[str, List[dict]] = {}

class LightsPayload(BaseModel):
    on: bool

class ProtocolFile(BaseModel):
    name: str

class ProtocolData(BaseModel):
    id: str
    createdAt: str
    files: List[ProtocolFile]
    source: str

class ProtocolUploadResponse(BaseModel):
    data: ProtocolData

class CreateRunPayload(BaseModel):
    protocolId: Optional[str] = None

class RunData(BaseModel):
    id: str
    protocolId: Optional[str]
    status: str
    createdAt: str
    current: bool

class RunsListResponse(BaseModel):
    data: List[RunData]

class RunActionsPayload(BaseModel):
    actionType: str

class CommandPayload(BaseModel):
    commandType: str
    params: dict
    intent: Optional[str] = "setup"

@app.get("/health")
def get_health():
    return {
        "name": "opentrons-sim",
        "api_version": "2.0.0",
        "fw_version": "sim_fw",
        "board_revision": "sim_board",
        "logs": []
    }

@app.get("/robot/lights")
def get_robot_lights():
    return {"on": lights_state["on"]}

@app.post("/robot/lights")
def post_robot_lights(payload: LightsPayload):
    lights_state["on"] = payload.on
    return {"on": lights_state["on"]}

@app.post("/protocols")
def post_protocols():
    """
    Simulates uploading a protocol.
    Return a fake protocol ID and relevant metadata.
    """
    protocol_id = f"protocol_{uuid.uuid4().hex[:6]}"
    protocols_db[protocol_id] = {
        "id": protocol_id,
        "createdAt": "2025-01-01T12:00:00",
        "files": [{"name": "protocol.py"}],
        "analysisSummaries": [],
        "source": "file"
    }
    return {"data": protocols_db[protocol_id]}

@app.get("/protocols")
def list_protocols():
    return {"data": list(protocols_db.values())}

@app.get("/protocols/{protocol_id}")
def get_protocol(protocol_id: str):
    if protocol_id not in protocols_db:
        raise HTTPException(status_code=404, detail="Protocol not found")
    return {"data": protocols_db[protocol_id]}

@app.delete("/protocols/{protocol_id}")
def delete_protocol(protocol_id: str):
    if protocol_id not in protocols_db:
        raise HTTPException(status_code=404, detail="Protocol not found")
    del protocols_db[protocol_id]
    return {"data": {"id": protocol_id, "message": "Protocol deleted"}}

@app.post("/runs")
def create_run(payload: CreateRunPayload):
    run_id = f"run_{uuid.uuid4().hex[:6]}"
    runs_db[run_id] = {
        "id": run_id,
        "status": "idle",
        "protocolId": payload.protocolId,
        "createdAt": "2025-01-01T12:05:00",
        "current": True
    }
    commands_db[run_id] = []
    return {"data": runs_db[run_id]}

@app.get("/runs")
def list_runs():
    return {"data": list(runs_db.values())}

@app.get("/runs/{run_id}")
def get_run(run_id: str):
    if run_id not in runs_db:
        raise HTTPException(status_code=404, detail="Run not found")
    return {"data": runs_db[run_id]}

@app.delete("/runs/{run_id}")
def delete_run(run_id: str):
    if run_id not in runs_db:
        raise HTTPException(status_code=404, detail="Run not found")
    del runs_db[run_id]
    commands_db.pop(run_id, None)
    return {"data": {"id": run_id, "message": "Run deleted"}}

@app.post("/runs/{run_id}/actions")
def post_run_actions(run_id: str, payload: RunActionsPayload):
    if run_id not in runs_db:
        raise HTTPException(status_code=404, detail="Run not found")

    action_type = payload.actionType
    if action_type == "play":
        if runs_db[run_id]["status"] in ["idle", "paused"]:
            runs_db[run_id]["status"] = "running"
        # simulate finishing
        else:
            pass
    elif action_type == "pause":
        if runs_db[run_id]["status"] == "running":
            runs_db[run_id]["status"] = "paused"
    elif action_type == "stop":
        if runs_db[run_id]["status"] in ["running", "paused", "idle"]:
            runs_db[run_id]["status"] = "stop-requested"

    action_id = f"action_{uuid.uuid4().hex[:6]}"
    return {"data": {"id": action_id, "actionType": action_type}}

@app.post("/runs/{run_id}/commands")
def post_run_commands(run_id: str, payload: CommandPayload):
    if run_id not in runs_db:
        raise HTTPException(status_code=404, detail="Run not found")

    command_id = f"command_{uuid.uuid4().hex[:6]}"
    cmd = {
        "id": command_id,
        "commandType": payload.commandType,
        "params": payload.params,
        "intent": payload.intent,
        "status": "queued",
        "createdAt": "2025-01-01T12:07:00",
    }
    commands_db[run_id].append(cmd)
    return {"data": cmd}

@app.get("/runs/{run_id}/commands")
def get_all_commands_for_run(run_id: str):
    if run_id not in runs_db:
        raise HTTPException(status_code=404, detail="Run not found")
    return {"data": commands_db.get(run_id, [])}

@app.get("/runs/{run_id}/commands/{command_id}")
def get_command_for_run(run_id: str, command_id: str):
    if run_id not in runs_db:
        raise HTTPException(status_code=404, detail="Run not found")
    for c in commands_db.get(run_id, []):
        if c["id"] == command_id:
            return {"data": c}
    raise HTTPException(status_code=404, detail="Command not found")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=31950)
    