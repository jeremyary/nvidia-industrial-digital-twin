# Warehouse Safety Digital Twin

A warehouse safety monitoring system built with NVIDIA Isaac Sim and Cosmos-Reason2. Simulated security cameras feed an edge AI model that detects safety hazards (workers in forklift paths, blocked exits, fallen pallets). Detections flow over MQTT back into the digital twin, which highlights danger zones in real-time. The annotated scene streams to a viewer via WebRTC.

This is the same architectural pattern used by BMW (FactoryExplorer), PepsiCo (Digital Twin Composer), and KION/GXO (autonomous forklift fleet twins) on NVIDIA Omniverse.

## Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌─────────────┐
│  Isaac Sim   │───▶│ Camera Frames │───▶│ Cosmos-R2   │───▶│    MQTT     │
│  (Digital    │    │  (PNG files)  │    │ (vLLM edge  │    │  Broker     │
│   Twin)      │◀──┐└──────────────┘    │  inference)  │    │ (Mosquitto) │
│              │   │                    └──────────────┘    └──────┬──────┘
│  WebRTC      │   │                                              │
│  Streaming ──┼──▶│ Viewer (AppImage)          ┌─────────────────┘
│              │   │                            │
│  MQTT-to-USD │◀──┼────────────────────────────┘
│  Bridge      │   │  (updates alert prims)
└──────────────┘   │
```

## Components

| Component | Container | Purpose |
|-----------|-----------|---------|
| Isaac Sim 5.1 | `isaac-sim` | 3D warehouse scene, camera rendering, streaming |
| Cosmos-Reason2-2B | `cosmos-edge` | Vision-language model for safety analysis |
| Mosquitto | `mqtt-broker` | MQTT message broker (ports 1883, 9001) |
| Edge Inference | host process | Watches camera frames, calls Cosmos, publishes to MQTT |
| MQTT Bridge | Isaac Sim Script Editor | Subscribes to MQTT, updates USD alert prims |

## Prerequisites

- NVIDIA GPU with 32+ GB VRAM
- [Podman](https://podman.io/) with [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) (CDI mode)
- NGC API key for pulling Isaac Sim container
- ~30 GB disk for containers and assets

### One-time setup

1. **SimReady Warehouse dataset** — download from [HuggingFace](https://huggingface.co/datasets/nvidia/PhysicalAI-SimReady-Warehouse-01) into `simready-warehouse/`
2. **Cosmos-Reason2-2B model** — download the W4A16 quantized weights into `models/cosmos-reason2-2b-w4a16/`
3. **Isaac Sim streaming client** — download the [AppImage](https://download.isaacsim.omniverse.nvidia.com/isaacsim-webrtc-streaming-client-1.0.6-linux-x64.AppImage) to the project root
4. **Cache directories** — create and set permissions:
   ```bash
   mkdir -p isaac-sim/{cache/main,cache/computecache,logs,data}
   chmod -R 777 isaac-sim/
   ```

## Quick Start

```bash
# Start all containers
./scripts/launch.sh start

# Wait for Isaac Sim to load (watch for streaming ready message)
podman logs -f isaac-sim

# Connect the streaming client to 127.0.0.1

# In Isaac Sim Script Editor, load the warehouse scene, then run:
exec(open("/workspace/create_alerts.py").read())
exec(open("/workspace/mqtt_bridge.py").read())

# In a host terminal, run the inference loop:
CAMERA_DIR=$(pwd)/workspace/camera_feeds python3 scripts/edge_inference.py

# Check status
./scripts/launch.sh status

# Stop everything
./scripts/launch.sh stop
```

## Project Structure

```
scripts/
  add_cameras.py        # Creates security camera prims in the scene
  edge_inference.py     # Watches camera frames, sends to Cosmos, publishes MQTT
  launch.sh             # Start/stop/status for all containers

workspace/                # Mounted into Isaac Sim container at /workspace
  add_cameras.py          # Copy of scripts/add_cameras.py for Script Editor access
  capture_frames.py       # Captures camera renders via Omniverse Replicator
  create_alerts.py        # Creates alert spheres and zone planes
  fix_cameras.py          # Repositions cameras to match actual scene bounds
  inspect_scene.py        # Utility to inspect scene bounds and prim locations
  mqtt_bridge.py          # MQTT-to-USD bridge (runs in Script Editor)
  warehouse_safety_scene.usd  # Saved scene with warehouse + cameras

mqtt-config/
  mosquitto.conf          # MQTT broker config (anonymous dev access)
```

## How It Works

1. **Camera capture** — `capture_frames.py` uses Omniverse Replicator to render each security camera at 1280x720 and save PNGs to `workspace/camera_feeds/`

2. **Edge inference** — `edge_inference.py` polls for new `*_latest.png` files, sends them to Cosmos-Reason2-2B via vLLM's OpenAI-compatible API, and publishes structured JSON results to MQTT topics (`warehouse/safety/{camera_id}`)

3. **MQTT bridge** — `mqtt_bridge.py` runs inside Isaac Sim's Script Editor, subscribes to `warehouse/safety/#`, and updates USD prims:
   - Alert spheres change color (green/yellow/red) based on `overall_status`
   - Zone planes become visible on CAUTION/DANGER, hidden on SAFE

4. **Streaming** — Isaac Sim streams the annotated scene via WebRTC to the AppImage client on port 49100

## VRAM Budget

Both Isaac Sim and Cosmos-Reason2 run on a single GPU:

| Component | VRAM |
|-----------|------|
| Isaac Sim (DLSS Balanced, 0.375 texture budget) | ~14 GB |
| Cosmos-Reason2-2B W4A16 (vLLM, 25% util) | ~8 GB |
| **Total** | **~22 GB** |
