#!/usr/bin/env python
# coding: utf-8

"""
Simple client code for the Opentrons in Python - adapted from OFM Client 
Copyright 2020 Richard Bowman, released under LGPL 3.0 or later
Copyright 2021 Benedict Diederich, released under LGPL 3.0 or later
"""

import requests
import numpy as np
import logging
import zeroconf
import requests 
from enum import Enum
from typing import Dict
import os 
import time
#import matplotlib.pyplot as plt

ACTION_RUNNING_KEYWORDS = ["idle", "pending", "running"]
ACTION_OUTPUT_KEYS = ["output", "return"]


class RunStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    FINISHING = "finishing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    PAUSED = "paused"
    STOPPING = "stop-requested"
    STOPPED = "stopped"
    
class OpentronsClient(object):
    headers = {'opentrons-version': '*'}

    def __init__(self, host, port=31950):
        if isinstance(host, zeroconf.ServiceInfo):
            # If we have an mDNS ServiceInfo object, try each address
            # in turn, to see if it works (sometimes you get addresses
            # that don't work, if your network config is odd).
            # TODO: figure out why we can get mDNS packets even when
            # the microscope is unreachable by that IP
            for addr in host.parsed_addresses():
                if ":" in addr:
                    self.host = f"[{addr}]"
                else:
                    self.host = addr
                self.port = host.port
                try:
                    self.get_json(self.base_url)
                    break
                except:
                    logging.info(f"Couldn't connect to {addr}, we'll try another address if possible.")
        else:
            self.host = host
            self.port = port
            #self.get_json(self.base_url)
        logging.info(f"Connecting to microscope {self.host}:{self.port}")
        #self.populate_extensions()

    extensions = None

    @property
    def base_url(self):
        return f"http://{self.host}:{self.port}"

    def get_json(self, path):
        """Perform an HTTP GET request and return the JSON response"""
        if not path.startswith("http"):
            path = self.base_url + path
        r = requests.get(path)
        r.raise_for_status()
        return r.json()

    def post_json(self, path, payload={}):
        """Make an HTTP POST request and return the JSON response"""
        if not path.startswith("http"):
            path = self.base_url + path
        r = requests.post(path, json=payload, headers=self.headers)
        r.raise_for_status()
        r = r.json()
        return r

    def post_file(self, path, file_path):
        url = path if path.startswith("http") else (self.base_url + path)
        with open(file_path, "rb") as f:
            # The OT-2 expects "files" as form-data for protocol uploads
            files = {"files": f}
            r = requests.post(url, files=files)
        r.raise_for_status()
        return r.json()
    
    def transfer(self, protocol_path: str):
        url = f"{self.base_url}/protocols"
        
        # open file :
        with open(protocol_path, "rb") as f:
            # The OT-2 expects "files" as form-data for protocol uploads
            files = {"files": f}
            resp = requests.post(url=url, files=files, headers=self.headers, timeout=600)
        protocol_id = resp.json()["data"]["id"]
        run_url = f"{self.base_url}/runs"
        run_json = {"data": {"protocolId": protocol_id}}
        run_resp = requests.post(run_url, headers=self.headers, json=run_json)
        run_id = run_resp.json()["data"]["id"]
        return protocol_id, run_id
    

    def check_run_status(self, run_id: str) -> RunStatus:
        url = f"{self.base_url}/runs/{run_id}"
        resp = requests.get(url, headers=self.headers)
        status = RunStatus(resp.json()["data"]["status"])
        return status    
    
    def execute(self, run_id: str) -> Dict[str, Dict[str, str]]:
        execute_url = f"{self.base_url}/runs/{run_id}/actions"
        execute_json = {"data": {"actionType": "play"}}
        execute_run_resp = requests.post(execute_url, headers=self.headers, json=execute_json)

        if execute_run_resp.status_code != 201:
            print(f"Could not run play action on {run_id}")
            print(execute_run_resp.json())

        while self.check_run_status(run_id) not in {
            RunStatus.FAILED,
            RunStatus.SUCCEEDED,
            RunStatus.STOPPED,
        }:
            time.sleep(1)
            print (f"Waiting for run {run_id} to finish...")
        status = self.check_run_status(run_id)
        print(f"Run {run_id} finished with status: {status}")
        return self.get_run(run_id)
    
        
    def toggle_light(self, state=True):
        """Turn on/off light of the robot"""
        payload = {
            "on":"true" if state else "false",
        }
        path = "/robot/lights"
        r = self.post_json(path, payload)
        return r
    
    def cancel(self, run_id: str):
        url = f"{self.base_url}/runs/{run_id}/actions"
        data = {"data": {"actionType": "stop"}}
        return requests.post(url, headers=self.headers, json=data)
    
    def pipette_home(self, location="right"):
        #%% homing the robot
        payload = {
            "target": "robot",
            "mount": "right"
        }
        path = "/robot/home"
        r = self.post_json(path, payload)
        return r
    
    def positions(self):
        #%% get positions of robot
        path = "/robot/positions"
        r = self.get_json(path)
        return r
    
    #%% PIPETTE
    def add_pipette(self, name='p300_single_gen2', position='right'):
        # assign/add a pipette to the robot
        payload = {
            "name": name, 
            "position": position
        }
        path = '/hardware/pipette/add'
        r = self.post_json(path, payload)
        return r
    
    def upload_protocol(self, protocol_filename):
        # Upload a protocol file from ./protocols folder
        file_path = os.path.join("./protocols", protocol_filename)
        resp = self.post_file("/protocols", file_path)
        # Grab the protocol ID from response
        protocol_id = resp["data"]["id"]
        return protocol_id

    def start_run(self, protocol_id):
        # Create a run referencing the uploaded protocol
        payload = {"data": {"protocolId": protocol_id}}
        run_resp = self.post_json("/runs", payload)
        run_id = run_resp["data"]["id"]

        # Start the run
        action_payload = {"data": {"actionType": "play"}}
        self.post_json(f"/runs/{run_id}/actions", action_payload)
        return run_id

    def stop_run(self, run_id):
        # Stop the run
        action_payload = {"data": {"actionType": "stop"}}
        self.post_json(f"/runs/{run_id}/actions", action_payload)

    def get_run_status(self, run_id):
        # Query the run status
        resp = self.get_json(f"/runs/{run_id}")
        return resp["data"]["status"]

    def get_run(self, run_id: str) -> Dict:
        url = f"{self.base_url}/runs/{run_id}"
        resp = requests.get(url, headers=self.headers)
        return resp.json()

    ''' 
    #
    First, start a “liveProtocol” session via HTTP:
    POST /sessions
    {
        "data": {
            "sessionType": "liveProtocol"
        }
    }

    This will return a `sessionId`. You can use this session ID to load a pipette and a labware:
    POST /sessions/:sessionId/commands/execute
    {
        "data": {
            "command": "equipment.loadPipette",
            "data": {
                "pipetteName": "p300_single",
                "mount": "right"
            }
        }
    }

    POST /sessions/:sessionId/commands/execute
    {
        "data": {
            "command": "equipment.loadLabware",
            "data": {
                "loadName": "opentrons_96_tiprack_300ul",
                "version": 1,
                "namespace": "opentrons",
                "location": { "slot": 5 }
            }
        }
    }

    Those responses will come back with a `result.pipetteId` and a `result.labwareId`, respectively, which you can use in future commands, like:
    POST /sessions/:sessionId/commands/execute
    {
        "data": {
            "command": "pipette.pickUpTip",
            "data": {
                "pipetteId": "b1c58fa0-7fea-43c7-b6da-f23525f8f66f",
                "labwareId": "a3d31c93-aeb5-45f5-8503-5a6993e925aa",
                "wellName": "A1"
            }
        }
    }
    '''

# connect to the robot 
mRobot = OpentronsClient(host="169.254.254.239", port=31950)

# turn on the lights 
mRobot.toggle_light(state=True)
mRobot.toggle_light(state=False)

# home the robot
mRobot.pipette_home("right")

# upload and start a protocol
protocol_id, run_id = mRobot.transfer(protocol_path="/uc2-workflow/Arkitektrons/OT2Driver/protocols/helloWorldStainstorm.py")
protocol_id_ = mRobot.execute(run_id=run_id)
status = mRobot.get_run_status(run_id)
mRobot.stop_run(run_id)
