# Opentrons Driver for Arkitekt

This repository provides an Opentrons driver that integrates with the Arkitekt framework. The driver enables control of an Opentrons OT-2 robot via HTTP request interface. Users can upload, compile, transfer, and execute protocols as well as pause, resume, or cancel runs through Arkitekt.

---

## Features

- **Protocol Management**: Compile and convert YAML configurations to Python protocols.
- **HTTP Interface**: Upload protocols, start, stop, pause, and resume runs using HTTP requests.
- **Run Monitoring**: Check status, fetch logs, and retrieve details of active or past runs.
- **Robot Control**: Toggle robot lights to verify connectivity and manage run states.
- **Arkitekt Integration**: Register driver functions for remote access via Arkitekt.

---

## Installation

### Docker Deployment

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/arkitekt-opentrons-driver.git
   cd arkitekt-opentrons-driver
   ```

2. **Build the Docker Image**
   ```bash
   docker build -t arkitekt_opentrons .
   ```

3. **Run the Container**
   ```bash
   docker run -p 8000:8000 arkitekt_opentrons
   ```

### Local Development

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/arkitekt-opentrons-driver.git
   cd arkitekt-opentrons-driver
   ```

2. **Create and Activate Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   python ot2_driver.py
   ```

---

## Usage

### HTTP Request Endpoints

- **Compile Protocol**
  - Function: `driver_compile_protocol`
  - Converts a YAML configuration to a Python protocol.
  
- **Transfer Protocol**
  - Function: `driver_transfer`
  - Uploads a protocol file to the Opentrons OT-2 and initiates a run.
  
- **Execute Protocol**
  - Function: `driver_execute`
  - Starts the protocol run and monitors its execution.
  
- **Pause/Resume/Cancel Run**
  - Functions: `driver_pause`, `driver_resume`, `driver_cancel`
  - Manage run state operations.
  
- **Status and Logs**
  - Functions: `driver_check_run_status`, `driver_get_run`, `driver_get_run_log`, `driver_get_runs`
  - Retrieve detailed information and logs for runs.
  
- **Robot Status and Maintenance**
  - Functions: `driver_get_robot_status`, `driver_reset_robot_data`, `driver_change_lights_status`
  - Monitor robot status and reset or change robot settings.
  
- **Custom Requests and Streaming**
  - Functions: `driver_send_request`, `driver_stream`
  - Allows custom HTTP requests and command streaming.

### Arkitekt Registration

Each driver function is registered with Arkitekt using the `@register` decorator. This allows remote invocation through an Arkitekt server. Update the `easy` context manager with your Arkitekt server URL.

---

## File Structure

```
arkitekt-opentrons-driver/
├── Dockerfile          # Docker configuration to build the container
├── ot2_driver.py       # Main driver script with HTTP and Arkitekt integration
├── requirements.txt    # Python dependencies
├── README.md           # Documentation
```

---

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes and push to your fork.
4. Open a pull request.

---

## License

Licensed under the MIT License. See [LICENSE](LICENSE) for details.