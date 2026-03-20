# Project Plan: Warehouse Safety Monitor -- Edge Vision Feeding a Live Digital Twin

**Created:** March 20, 2026
**Author:** Jeremy Ary (with AI assistance)
**Status:** Planning
**Hardware:** ORIGIN PC (RTX 5090, 128GB RAM, Ubuntu) + optional GMKTec (Ryzen AI Max+ 395, 128GB unified RAM)

---

## Table of Contents

1. [What You Are Building](#1-what-you-are-building)
2. [Architecture Overview](#2-architecture-overview)
3. [Hardware Strategy: Desktop-First, Then Edge](#3-hardware-strategy-desktop-first-then-edge)
4. [RHEL and Fedora: Where They Fit](#4-rhel-and-fedora-where-they-fit)
5. [Prerequisites and Account Setup](#5-prerequisites-and-account-setup)
6. [Phase 1: Isaac Sim Warehouse Scene](#6-phase-1-isaac-sim-warehouse-scene)
7. [Phase 2: Simulated Camera Feeds](#7-phase-2-simulated-camera-feeds)
8. [Phase 3: Cosmos-Reason2 Edge Inference](#8-phase-3-cosmos-reason2-edge-inference)
9. [Phase 4: MQTT Bridge and Digital Twin Updates](#9-phase-4-mqtt-bridge-and-digital-twin-updates)
10. [Phase 5: Kit App Streaming to Browser](#10-phase-5-kit-app-streaming-to-browser)
11. [Phase 6: End-to-End Integration](#11-phase-6-end-to-end-integration)
12. [Phase 7 (Optional): GMKTec as Physical Edge Device](#12-phase-7-optional-gmktec-as-physical-edge-device)
13. [Phase 8 (Optional): RHEL / OpenShift Integration](#13-phase-8-optional-rhel--openshift-integration)
14. [VRAM Budget and Performance Tuning](#14-vram-budget-and-performance-tuning)
15. [Troubleshooting Guide](#15-troubleshooting-guide)
16. [Key Resources](#16-key-resources)
17. [What You Will Learn](#17-what-you-will-learn)
18. [Deliverables](#18-deliverables)

---

## 1. What You Are Building

A warehouse digital twin in NVIDIA Isaac Sim with simulated security/safety cameras.
Camera feeds are analyzed by Cosmos-Reason2-2B (acting as an "edge" inference engine)
that detects safety events -- worker in a forklift path, fallen pallet, blocked exit,
unauthorized zone entry. Detections flow over MQTT back into the digital twin, which
highlights hazards in real-time. The annotated digital twin streams to a web browser
via Kit App Streaming.

This is the same architectural pattern used by:
- **PepsiCo** (Siemens Digital Twin Composer + Omniverse, announced CES 2026)
- **BMW** (FactoryExplorer on Omniverse, 30+ global factories)
- **KION/GXO** (autonomous forklift fleet digital twins, announced GTC 2026)
- **Pegatron** (Metropolis VSS for defect detection, 67% defect rate reduction)

The project teaches you the full edge-to-datacenter loop that Itamar is asking about,
using the exact tools NVIDIA is positioning for industrial AI in 2026.

---

## 2. Architecture Overview

```
+------------------------------------------------------------------+
|  DESKTOP WORKSTATION (RTX 5090, Ubuntu)                          |
|                                                                  |
|  +-------------------+     Camera frames      +--------------+  |
|  |                   |  (ZMQ or shared dir)    |              |  |
|  |  Isaac Sim 5.1    | ---------------------->| Cosmos       |  |
|  |  (Warehouse Scene |                        | Reason2-2B   |  |
|  |   + Cameras)      |                        | (vLLM)       |  |
|  |                   |     USD prim updates   |              |  |
|  |  [Kit App Stream] | <----+                 +--------------+  |
|  |     (WebRTC)      |      |                       |           |
|  +-------------------+      |                       |           |
|         |                   |   JSON detections     |           |
|         |              +----+----+                   |           |
|         |              |  MQTT   | <----------------+           |
|         |              | Broker  |                               |
|         |              | + Bridge|                               |
|  +------v------+      +---------+                               |
|  |   Browser   |                                                |
|  | (any device)|                                                |
+------------------------------------------------------------------+

                    --- OPTIONAL PHASE 7 ---

+------------------------------------------------------------------+
|  DESKTOP WORKSTATION                                             |
|  +-------------------+                        +---------+       |
|  |  Isaac Sim 5.1    |     USD prim updates   |  MQTT   |       |
|  |  (Digital Twin)   | <---------------------| Broker  |       |
|  |  [Kit App Stream] |                        |         |       |
|  +-------------------+                        +----^----+       |
+------------------------------------------------------------------+
                                                     |
                              Network (Tailscale)    |
                                                     |
+------------------------------------------------------------------+
|  GMKTEC (Ryzen AI Max+ 395)                                     |
|  +-----------------+          JSON detections  +---------+      |
|  | Cosmos-Reason2  | -----------------------> |  MQTT   |      |
|  | 2B (ROCm/vLLM   |                          | Client  |      |
|  |  or llama.cpp)  |                          +---------+      |
|  +-----------------+                                            |
|         ^                                                       |
|         | Camera frames (network stream or file share)          |
+------------------------------------------------------------------+
```

### Data Flow

1. **Isaac Sim** renders a warehouse scene with simulated cameras
2. Camera frames are extracted (ZMQ extension, Python API, or written to a shared directory)
3. **Cosmos-Reason2-2B** receives frames and analyzes them for safety events
4. Cosmos outputs structured JSON: detected objects, bounding boxes, safety assessments
5. A lightweight Python service publishes detections to an **MQTT broker**
6. An **MQTT-to-USD bridge** (based on NVIDIA iot-samples) reads MQTT messages and
   updates USD prim attributes in the Isaac Sim scene (alert markers, zone highlights)
7. **Kit App Streaming** renders the annotated scene and streams it to a web browser

### Component Inventory

| Component | Technology | Container? | GPU Required? |
|-----------|-----------|------------|---------------|
| Warehouse scene + cameras | Isaac Sim 5.1 | Yes (NGC) | Yes (RTX) |
| Edge inference | Cosmos-Reason2-2B via vLLM | Yes | Yes (CUDA or ROCm) |
| Message broker | Mosquitto (MQTT) | Yes | No |
| MQTT-to-USD bridge | Python (based on iot-samples) | Optional | No |
| Frame transport | IsaacSimZMQ or shared directory | Part of Isaac Sim | No |
| Browser streaming | Kit App Streaming (WebRTC) | Built into Isaac Sim | Yes (NVENC) |
| Dashboard | Web browser (Firefox recommended) | N/A | No |

---

## 3. Hardware Strategy: Desktop-First, Then Edge

**Start everything on the desktop.** The RTX 5090 (32GB VRAM) can run Isaac Sim and
Cosmos-Reason2-2B simultaneously with careful memory budgeting. This lets you build
and debug the full pipeline without fighting ROCm driver issues on the GMKTec.

### Why Desktop-First Works

| Component | VRAM Estimate | Notes |
|-----------|--------------|-------|
| Isaac Sim (moderate scene, reduced textures) | 10-14 GB | Use DLSS Performance + 30% texture budget |
| Cosmos-Reason2-2B (W4A16 quantized, vLLM) | 6-8 GB | Constrain gpu-memory-utilization to 0.25 |
| CUDA contexts overhead (x2 processes) | 1-2 GB | Unavoidable per-process cost |
| **Total** | **17-24 GB** | Fits in 32 GB with headroom |

The W4A16 quantized model (`embedl/Cosmos-Reason2-2B-W4A16-Edge2`) loses only 0.02
percentage points of accuracy vs full precision and cuts memory roughly in half. Use it.

### When to Bring in the GMKTec (Phase 7)

Move Cosmos-Reason2 to the GMKTec after the pipeline works end-to-end on the desktop.
Benefits of the split:
- Frees ~8GB VRAM on the desktop for a richer Isaac Sim scene
- Demonstrates real network-separated edge-to-datacenter architecture
- The GMKTec's 128GB unified RAM is overkill for the 2B model -- it will run comfortably
- Proves the architecture works across physical machines (relevant for demo credibility)

The GMKTec path uses ROCm + vLLM (or llama.cpp with HIP backend). ROCm 7.0 supports
the Strix Halo GPU (gfx1151), but this is newer hardware with potential rough edges.
By proving the pipeline works on the desktop first, you isolate ROCm issues as a
separate concern rather than debugging the pipeline and the driver stack simultaneously.

---

## 4. RHEL and Fedora: Where They Fit

### Recommendation: Stay on Ubuntu, Use RHEL/UBI Containers

Your Ubuntu host has first-class NVIDIA support (Isaac Sim is officially supported,
drivers are stable, vLLM ships pre-built wheels). Switching the host OS to RHEL or
Fedora would introduce friction with no immediate benefit for this project.

The Red Hat story is better served by **running RHEL/UBI-based containers** on your
Ubuntu host. The container runtime does not care about the host OS for GPU workloads --
GPU passthrough via CDI is host-agnostic:

```bash
# Proof: UBI container with GPU on Ubuntu host
sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml
podman run --rm --device nvidia.com/gpu=all \
  registry.access.redhat.com/ubi9 nvidia-smi -L
```

### Where to Inject Red Hat

| Component | Default | Red Hat Option | Effort |
|-----------|---------|---------------|--------|
| MQTT broker | Eclipse Mosquitto (Alpine) | Mosquitto on UBI9 | Low -- rebuild on UBI base |
| MQTT-to-USD bridge | Python on Ubuntu | Python on UBI9 | Low -- change FROM line |
| Cosmos vLLM server | vLLM official image | vLLM on UBI9 | Medium -- CUDA deps |
| Isaac Sim | NVIDIA official image | Cannot change (NVIDIA proprietary) | N/A |
| Edge device OS | Ubuntu / GMKTec stock | RHEL bootc or Fedora bootc | Medium-High |

For the best Red Hat story with minimal effort, build the **MQTT broker** and
**MQTT-to-USD bridge** as UBI9-based containers. These are the custom components you
control, and they demonstrate that the glue layer runs on Red Hat's stack.

### Fedora as RHEL Substitute

Fedora is a reasonable substitute for development and prototyping:

| Concern | RHEL | Fedora |
|---------|------|--------|
| NVIDIA drivers | Supported (official RPMs) | Works via RPM Fusion `akmod-nvidia`, but kernel updates can break driver builds until RPM Fusion catches up |
| Container Toolkit | Official support | Works (available in Fedora repos since F41) |
| bootc / image mode | GA, production-supported | Experimental (available since F41 via `fedora-bootc` images) |
| Subscription | Free Developer Subscription (16 systems) | No subscription needed |
| Demo credibility | High ("runs on RHEL") | Medium ("runs on Fedora / Red Hat ecosystem") |
| Isaac Sim support | Not officially supported | Not officially supported |

**Fedora's main weakness for this project** is NVIDIA driver stability. Fedora tracks
newer kernels aggressively, and NVIDIA's akmod drivers sometimes lag behind, causing
build failures after kernel updates. For a demo workstation where uptime matters, this
is a real friction source.

**If you want to try Fedora:** Use it on the GMKTec (Phase 7) rather than the desktop.
The GMKTec uses an AMD GPU (no NVIDIA driver issues), and Fedora's ROCm support is
reasonable. Fedora bootc on the GMKTec would demonstrate the "Red Hat ecosystem at the
edge" story without risking your primary workstation.

### RHEL Licensing for Red Hat Employees

As a Red Hat associate, you have multiple paths to a free RHEL subscription:

1. **No-cost Developer Subscription for Individuals** -- Free, self-supported, up to
   16 systems. Usable on employer-owned hardware. Register at
   https://developers.redhat.com/register
2. **Internal employee access** -- Check The Source / Mojo / internal IT portal for
   associate-specific entitlements (not documented publicly)
3. **RHEL for Business Developers** (new July 2025) -- No-cost, up to 25 instances,
   for development/test in business environments

Any of these give you access to RHEL image mode base images in the Red Hat container
catalog, which is all you need for building bootc images.

---

## 5. Prerequisites and Account Setup

Complete these before starting any hands-on work. Most are free registrations.

### Accounts

| Account | URL | What For |
|---------|-----|----------|
| NGC (NVIDIA GPU Cloud) | https://ngc.nvidia.com/signin/email | Isaac Sim container, Cosmos NIM, SimReady assets |
| HuggingFace | https://huggingface.co/join | Cosmos model weights, SimReady Warehouse dataset |
| NVIDIA Developer | https://developer.nvidia.com | Documentation, SDK access |

### NGC API Key

Required for pulling container images from NGC:

1. Go to https://org.ngc.nvidia.com/setup/api-key
2. Select "NGC Catalog" scope
3. Generate and save the key securely
4. Authenticate Podman:
   ```bash
   echo "$NGC_API_KEY" | podman login nvcr.io --username '$oauthtoken' --password-stdin
   ```

### HuggingFace Token

Required for downloading the SimReady Warehouse dataset and Cosmos model weights:

1. Go to https://huggingface.co/settings/tokens
2. Create a token with "Read" access
3. Authenticate:
   ```bash
   pip install huggingface_hub
   huggingface-cli login
   ```

### Host Software

Verify these are installed on your Ubuntu workstation:

```bash
# NVIDIA driver (should already be installed for your 5090)
nvidia-smi
# Expect: Driver 570.xx+ for Blackwell

# NVIDIA Container Toolkit
nvidia-ctk --version
# If not installed:
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html

# Generate CDI specs (enables --device nvidia.com/gpu=all)
sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml

# Podman
podman --version
# Expect: 4.x+

# Python 3.11+
python3 --version
```

### Disk Space Budget

| Item | Size | Location |
|------|------|----------|
| Isaac Sim 5.1 container image | ~20 GB (compressed pull) | Podman image store |
| Isaac Sim runtime cache (shaders, etc.) | ~10-15 GB (grows on first run) | `~/isaac-sim/cache/` |
| SimReady Warehouse dataset | ~15 GB | `~/simready-warehouse/` |
| Cosmos-Reason2-2B W4A16 model weights | ~1.5 GB | `~/.cache/huggingface/` |
| vLLM container image | ~8 GB | Podman image store |
| Mosquitto + bridge containers | <500 MB | Podman image store |
| **Total** | **~55-60 GB** | |

Ensure you have at least 80 GB free on your NVMe to be comfortable.

---

## 6. Phase 1: Isaac Sim Warehouse Scene

**Goal:** A warehouse environment in Isaac Sim with shelving, pallets, forklifts,
and human characters. This is your digital twin's physical space.

**Time estimate:** Half day to full day (first run has significant shader compilation).

### Step 1.1: Pull and Start Isaac Sim

```bash
# Pull the Isaac Sim 5.1 container
podman pull nvcr.io/nvidia/isaac-sim:5.1.0

# Create persistent directories for cache and config
mkdir -p ~/isaac-sim/{cache/main,cache/computecache,logs,config,data}

# Launch Isaac Sim (GUI mode for scene building)
podman run --name isaac-sim -it --rm \
  --device nvidia.com/gpu=all \
  --network=host \
  -e "ACCEPT_EULA=Y" \
  -e "PRIVACY_CONSENT=Y" \
  -v ~/isaac-sim/cache/main:/isaac-sim/.cache:rw \
  -v ~/isaac-sim/cache/computecache:/isaac-sim/.nv/ComputeCache:rw \
  -v ~/isaac-sim/logs:/isaac-sim/.nvidia-omniverse/logs:rw \
  -v ~/isaac-sim/config:/isaac-sim/.nvidia-omniverse/config:rw \
  -v ~/isaac-sim/data:/isaac-sim/.local/share/ov/data:rw \
  -v ~/workspace:/workspace:rw \
  nvcr.io/nvidia/isaac-sim:5.1.0 \
  isaacsim isaacsim.exp.full
```

**First launch will take 5-15 minutes** for shader compilation. Subsequent launches
are much faster because shaders are cached in `~/isaac-sim/cache/`.

If you cannot get GUI mode working in the container (display forwarding issues), you
have two alternatives:
- Install Isaac Sim natively via pip: `pip install isaacsim==5.1.0`
- Use streaming mode and build the scene via browser (see Phase 5)

### Step 1.2: Download SimReady Warehouse Assets

```bash
huggingface-cli download nvidia/PhysicalAI-SimReady-Warehouse-01 \
  --repo-type dataset \
  --local-dir ~/simready-warehouse
```

This gives you 753 OpenUSD assets: shelving units, pallets, bins, crates, forklifts,
safety cones, barrels, conveyors, ramps, ladders, and a pre-built complete warehouse
scene.

### Step 1.3: Build the Scene

**Option A: Use the pre-built warehouse scene (fastest)**

The dataset includes `physical_ai_simready_warehouse_01.usd` -- a complete warehouse
already composed from the individual assets. Open this in Isaac Sim:

```
File > Open > navigate to ~/simready-warehouse/physical_ai_simready_warehouse_01.usd
```

First load takes several minutes (material compilation, collider generation). This is
normal.

**Option B: Build a custom scene (more learning)**

If you want to understand scene composition and have a simpler scene (better for VRAM):

1. Create a new stage: `File > New`
2. Add a ground plane: `Create > Physics > Ground Plane`
3. Add lighting: `Create > Light > Dome Light` (or Distant Light for outdoor feel)
4. Add warehouse elements by referencing SimReady assets:
   - `Create > Reference` then navigate to individual USD files in `~/simready-warehouse/Props/`
   - Start with: a few shelving units, some pallets, a forklift, safety cones
   - Arrange them to create a warehouse aisle layout
5. Add physics: Select objects that should interact physically, then
   `Add > Physics > Rigid Body` and `Add > Physics > Collider`

**Recommendation for VRAM management:** Start with Option B and build a focused scene
with 50-100 assets rather than the full 753-asset warehouse. This keeps VRAM usage in
the 10-12 GB range, leaving room for Cosmos. You can scale up the scene complexity
later after validating the full pipeline.

### Step 1.4: Add Human Characters and Forklifts (Optional)

Isaac Sim 5.0+ supports human characters executing common warehouse behaviors:
- Stacking items
- Pushing carts
- Walking routes

Access via: `Create > Characters` or the People extension. This adds realism to safety
monitoring -- Cosmos can reason about human-machine interactions.

### Step 1.5: Save the Scene

Save to your workspace mount so it persists outside the container:
```
File > Save As > /workspace/warehouse_safety_scene.usd
```

### Verification

- The scene loads without errors
- You can navigate the 3D viewport (orbit, pan, zoom)
- Physics simulation runs when you press Play (objects fall, collide)
- `nvidia-smi` shows Isaac Sim using 10-14 GB VRAM (if more, reduce scene complexity)

---

## 7. Phase 2: Simulated Camera Feeds

**Goal:** Add cameras to the warehouse scene that simulate security/safety cameras.
Extract their rendered frames so an external process (Cosmos) can analyze them.

**Time estimate:** Half day.

### Step 2.1: Add Cameras to the Scene

Place 2-3 cameras at positions a real warehouse would have security cameras:

1. Overhead view of main aisle (wide angle)
2. View of forklift operating zone (medium angle)
3. View of loading dock or restricted area (medium angle)

In Isaac Sim:
```
Create > Camera
```
Then position and orient each camera using the transform gizmo. Set resolution:
- **720p (1280x720)** is a good balance of detail vs. VRAM for this project
- Lower resolution means faster rendering and less data to send to Cosmos

Camera properties to configure:
- **Focal length:** 18-24mm for wide angle (overhead), 35-50mm for medium shots
- **Clipping range:** Near=0.1, Far=100 (meters)
- **Resolution:** 1280x720

### Step 2.2: Choose a Frame Transport Method

You need to get rendered camera frames out of Isaac Sim and into Cosmos-Reason2.
Three options, ordered by complexity:

**Option A: Shared directory (simplest, recommended to start)**

Isaac Sim writes camera frames to a directory on disk. Cosmos reads them from the
same directory. Works perfectly when both run on the same machine.

```python
# In Isaac Sim (Python script or extension):
import omni.replicator.core as rep

# Create render products for each camera
cam1_rp = rep.create.render_product("/World/Camera_Overhead", (1280, 720))
cam2_rp = rep.create.render_product("/World/Camera_Forklift", (1280, 720))

# Write frames to disk
writer = rep.WriterRegistry.get("BasicWriter")
writer.initialize(
    output_dir="/workspace/camera_feeds",
    rgb=True,
    frame_padding=6,
)
writer.attach([cam1_rp, cam2_rp])

# Trigger frame capture (call this each simulation step or on interval)
rep.orchestrator.step()
```

Frames appear as PNG files in `/workspace/camera_feeds/`. Your Cosmos inference
script watches this directory for new files.

**Option B: IsaacSimZMQ (higher performance, recommended for Phase 6)**

The ZMQ extension streams camera frames via ZeroMQ sockets with Protobuf
serialization. This is the production-grade approach.

```bash
# Clone and build the extension
git clone https://github.com/isaac-sim/IsaacSimZMQ.git
cd IsaacSimZMQ
./build.sh
```

On the Isaac Sim side:
- Enable the IsaacSimZMQ extension: `Window > Extensions > search "ZMQ" > enable`
- Configure camera prims as ZMQ stream sources
- Frames stream as CUDA pointers (C++ mode) or numpy arrays (Python mode)

On the Cosmos side:
- Build a ZMQ server that receives frames and passes them to vLLM
- The included example server is a good starting point

**Option C: Python Camera API (most flexible)**

Direct programmatic access within an Isaac Sim Python script:

```python
from isaacsim.sensors.camera import Camera
import numpy as np
from PIL import Image

camera = Camera(prim_path="/World/Camera_Overhead", resolution=(1280, 720))
camera.initialize()

# After each simulation step:
rgba = camera.get_rgba()  # np.ndarray, shape (720, 1280, 4), uint8
rgb = rgba[:, :, :3]

# Save to shared directory
img = Image.fromarray(rgb)
img.save("/workspace/camera_feeds/overhead_latest.png")
```

### Step 2.3: Configure Frame Rate

For Cosmos-Reason2, you do not need 30 fps. The model was trained at 4 fps for video
input. For still-image analysis (which is what you are doing with individual frames),
even 1 frame per second is sufficient for safety monitoring.

Configure your frame capture to run at 1-2 fps to start:

```python
import time

CAPTURE_INTERVAL = 1.0  # seconds between captures

# In your simulation loop:
last_capture = 0
while simulation_running:
    sim.step()
    now = time.time()
    if now - last_capture >= CAPTURE_INTERVAL:
        capture_frames()
        last_capture = now
```

This dramatically reduces VRAM pressure from rendering and gives Cosmos time to
process each frame before the next arrives.

### Verification

- Camera feeds appear as PNG files in `/workspace/camera_feeds/`
- Images show reasonable views of the warehouse from each camera angle
- Files update at approximately your configured interval
- VRAM usage does not spike significantly from the camera rendering
  (at 720p, 1 fps, the rendering overhead is minimal)

---

## 8. Phase 3: Cosmos-Reason2 Edge Inference

**Goal:** Run Cosmos-Reason2-2B as an inference service that analyzes camera frames
and outputs structured JSON describing safety-relevant observations.

**Time estimate:** Half day to full day (model download + vLLM setup + prompt engineering).

### Step 3.1: Download the Model

Use the W4A16 quantized variant to minimize VRAM usage:

```bash
huggingface-cli download embedl/Cosmos-Reason2-2B-W4A16-Edge2 \
  --local-dir ~/models/cosmos-reason2-2b-w4a16
```

Size: ~1.5 GB. If you have VRAM headroom and want better quality, use the full
FP16 model instead:

```bash
huggingface-cli download nvidia/Cosmos-Reason2-2B \
  --local-dir ~/models/cosmos-reason2-2b
```

Size: ~4 GB.

### Step 3.2: Launch vLLM Inference Server

**Option A: vLLM in a container (recommended)**

```bash
podman run --name cosmos-edge -d --rm \
  --device nvidia.com/gpu=all \
  --network=host \
  -v ~/models:/models:ro \
  -v ~/workspace/camera_feeds:/camera_feeds:ro \
  -e VLLM_WORKER_MULTIPROC_METHOD=spawn \
  docker.io/vllm/vllm-openai:latest \
  --model /models/cosmos-reason2-2b-w4a16 \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.25 \
  --max-num-seqs 2 \
  --port 8000 \
  --reasoning-parser qwen3 \
  --allowed-local-media-path /camera_feeds
```

Key flags for co-location with Isaac Sim:
- `--gpu-memory-utilization 0.25` -- Limits vLLM to ~8 GB of VRAM (25% of 32 GB).
  Adjust up if Isaac Sim is using less than expected, or down if you see OOM.
- `--max-model-len 8192` -- Shorter context = less KV cache memory.
- `--max-num-seqs 2` -- Process max 2 concurrent requests (you only have 2-3 cameras).

**Option B: vLLM native (if container GPU sharing causes issues)**

```bash
pip install vllm>=0.11.0

vllm serve ~/models/cosmos-reason2-2b-w4a16 \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.25 \
  --max-num-seqs 2 \
  --port 8000 \
  --reasoning-parser qwen3 \
  --allowed-local-media-path ~/workspace/camera_feeds
```

### Step 3.3: Test Basic Inference

Verify Cosmos is running and can analyze an image:

```bash
curl -s http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "cosmos-reason2-2b-w4a16",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "image_url",
            "image_url": {"url": "file:///camera_feeds/overhead_latest.png"}
          },
          {
            "type": "text",
            "text": "Describe what you see in this warehouse camera image. Identify any safety concerns."
          }
        ]
      }
    ],
    "max_tokens": 512
  }'
```

You should get a response with physical reasoning about the warehouse scene.

### Step 3.4: Design the Safety Analysis Prompt

The prompt is critical -- it determines what Cosmos looks for and how it structures
its output. Here is a starting point:

```
You are a warehouse safety monitoring AI analyzing security camera footage.

Analyze this image and report:
1. All people visible and their locations (near machinery, in aisles, in restricted zones)
2. All vehicles/forklifts and whether they are moving or stationary
3. Any safety hazards:
   - Workers in forklift operating paths
   - Fallen or unstable pallets/objects
   - Blocked emergency exits or aisles
   - Missing safety equipment (hard hats, vests)
   - Unauthorized zone entry
4. Overall safety status: SAFE, CAUTION, or DANGER

Respond in JSON format:
{
  "timestamp": "<current_time>",
  "camera_id": "<camera_name>",
  "people": [{"location": [x, y], "description": "...", "in_danger": true/false}],
  "vehicles": [{"type": "forklift", "location": [x, y], "status": "moving/stationary"}],
  "hazards": [{"type": "...", "severity": "low/medium/high", "description": "...", "location": [x, y]}],
  "overall_status": "SAFE|CAUTION|DANGER",
  "summary": "One-sentence summary of the scene"
}
```

**Note on coordinates:** Cosmos-Reason2 normalizes all coordinates to a 0-1000 range
on each axis (origin: top-left). Your MQTT bridge will need to map these to the USD
scene's coordinate system.

### Step 3.5: Build the Inference Loop

Create a Python script that watches for new camera frames, sends them to Cosmos,
and publishes the results. This is the "edge inference application":

```python
#!/usr/bin/env python3
"""Edge inference service: watches camera frames, analyzes with Cosmos, publishes to MQTT."""

import json
import time
import glob
import os
import requests
import paho.mqtt.client as mqtt

VLLM_URL = "http://localhost:8000/v1/chat/completions"
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_PREFIX = "warehouse/safety"
CAMERA_DIR = "/workspace/camera_feeds"  # or ~/workspace/camera_feeds
POLL_INTERVAL = 2.0  # seconds

SAFETY_PROMPT = """You are a warehouse safety monitoring AI analyzing security camera footage.
Analyze this image and report all people, vehicles, and safety hazards.
Respond in JSON format with fields: people, vehicles, hazards, overall_status, summary."""


def analyze_frame(image_path: str, camera_id: str) -> dict | None:
    """Send a frame to Cosmos-Reason2 for analysis."""
    try:
        response = requests.post(
            VLLM_URL,
            json={
                "model": "cosmos-reason2-2b-w4a16",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"file://{image_path}"},
                            },
                            {"type": "text", "text": SAFETY_PROMPT},
                        ],
                    }
                ],
                "max_tokens": 512,
            },
            timeout=30,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]

        # Try to extract JSON from the response
        # Cosmos wraps output in <think>...</think><answer>...</answer>
        if "<answer>" in content:
            content = content.split("<answer>")[1].split("</answer>")[0].strip()

        return json.loads(content)
    except (requests.RequestException, json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"Analysis failed for {camera_id}: {e}")
        return None


def main():
    # Connect to MQTT broker
    mqtt_client = mqtt.Client(client_id="edge-inference")
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
    mqtt_client.loop_start()

    print(f"Watching {CAMERA_DIR} for new frames...")
    last_processed = {}

    while True:
        for frame_path in glob.glob(os.path.join(CAMERA_DIR, "*.png")):
            mtime = os.path.getmtime(frame_path)
            if last_processed.get(frame_path) == mtime:
                continue  # Already processed this version

            camera_id = os.path.splitext(os.path.basename(frame_path))[0]
            print(f"Analyzing {camera_id}...")

            result = analyze_frame(frame_path, camera_id)
            if result:
                result["camera_id"] = camera_id
                result["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

                topic = f"{MQTT_TOPIC_PREFIX}/{camera_id}"
                mqtt_client.publish(topic, json.dumps(result), qos=1)
                print(f"  Status: {result.get('overall_status', 'UNKNOWN')}")

            last_processed[frame_path] = mtime

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
```

### Verification

- vLLM is running: `curl http://localhost:8000/v1/models` returns the model name
- Analysis works: the curl test from Step 3.3 returns a structured response
- The inference loop picks up new frames and publishes MQTT messages
- `nvidia-smi` shows both Isaac Sim and vLLM using GPU memory within budget

---

## 9. Phase 4: MQTT Bridge and Digital Twin Updates

**Goal:** Connect the inference output to the digital twin. When Cosmos detects a
hazard, the warehouse scene updates visually -- highlighting zones, moving alert
markers, changing object colors.

**Time estimate:** Half day to full day.

### Step 4.1: Run an MQTT Broker

```bash
podman run --name mqtt-broker -d --rm \
  -p 1883:1883 \
  -p 9001:9001 \
  docker.io/eclipse-mosquitto:2 \
  mosquitto -c /mosquitto-no-auth.conf
```

Note: The default Mosquitto 2.x config requires authentication. For development,
create a permissive config:

```bash
mkdir -p ~/mqtt-config
cat > ~/mqtt-config/mosquitto.conf << 'EOF'
listener 1883
allow_anonymous true
listener 9001
protocol websockets
EOF

podman run --name mqtt-broker -d --rm \
  -p 1883:1883 \
  -p 9001:9001 \
  -v ~/mqtt-config/mosquitto.conf:/mosquitto/config/mosquitto.conf:ro \
  docker.io/eclipse-mosquitto:2
```

### Step 4.2: Verify MQTT Flow

In one terminal, subscribe to all warehouse topics:
```bash
# Install mosquitto-clients if needed: sudo apt install mosquitto-clients
mosquitto_sub -h localhost -t "warehouse/safety/#" -v
```

In another terminal, publish a test message:
```bash
mosquitto_pub -h localhost -t "warehouse/safety/overhead" \
  -m '{"overall_status": "DANGER", "hazards": [{"type": "worker_in_path", "severity": "high"}]}'
```

You should see the message appear in the subscriber terminal.

### Step 4.3: Build the MQTT-to-USD Bridge

This is the key integration piece. It subscribes to MQTT topics and updates USD
prim attributes in the Isaac Sim scene to reflect safety events.

The approach depends on how you are running Isaac Sim:

**Option A: Isaac Sim Python extension (recommended)**

Write an Isaac Sim extension or standalone script that runs inside the Isaac Sim
process, subscribes to MQTT, and updates prims directly:

```python
"""MQTT-to-USD bridge running inside Isaac Sim."""

import json
import threading
import omni.usd
import paho.mqtt.client as mqtt
from pxr import UsdGeom, Gf, Sdf

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "warehouse/safety/#"

# Pre-create alert marker prims in your scene at these paths
ALERT_MARKERS = {
    "overhead": "/World/Alerts/Overhead_Alert",
    "forklift_zone": "/World/Alerts/Forklift_Alert",
    "loading_dock": "/World/Alerts/Dock_Alert",
}

# Color mapping for safety status
STATUS_COLORS = {
    "SAFE": Gf.Vec3f(0.0, 0.8, 0.0),      # Green
    "CAUTION": Gf.Vec3f(1.0, 0.8, 0.0),    # Yellow
    "DANGER": Gf.Vec3f(1.0, 0.0, 0.0),     # Red
}


def on_message(client, userdata, msg):
    """Handle incoming MQTT messages and update USD prims."""
    try:
        data = json.loads(msg.payload.decode())
        camera_id = data.get("camera_id", "unknown")
        status = data.get("overall_status", "SAFE")

        stage = omni.usd.get_context().get_stage()
        if stage is None:
            return

        # Update alert marker visibility and color
        marker_path = ALERT_MARKERS.get(camera_id)
        if marker_path:
            prim = stage.GetPrimAtPath(marker_path)
            if prim.IsValid():
                # Make visible if CAUTION or DANGER
                imageable = UsdGeom.Imageable(prim)
                if status in ("CAUTION", "DANGER"):
                    imageable.MakeVisible()
                else:
                    imageable.MakeInvisible()

        # Update zone highlighting (if you have zone prims)
        for hazard in data.get("hazards", []):
            severity = hazard.get("severity", "low")
            hazard_type = hazard.get("type", "unknown")
            print(f"  HAZARD [{severity}]: {hazard_type} - {hazard.get('description', '')}")

    except (json.JSONDecodeError, KeyError) as e:
        print(f"MQTT message parse error: {e}")


def start_mqtt_bridge():
    """Start MQTT subscriber in a background thread."""
    client = mqtt.Client(client_id="usd-bridge")
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT)
    client.subscribe(MQTT_TOPIC)
    client.loop_start()
    print(f"MQTT-to-USD bridge connected, subscribed to {MQTT_TOPIC}")


# Call this from your Isaac Sim script or extension setup
start_mqtt_bridge()
```

**Option B: Use the NVIDIA iot-samples pattern**

Clone and adapt the official IoT samples:

```bash
git clone https://github.com/NVIDIA-Omniverse/iot-samples.git
cd iot-samples
```

The `source/ingest_app_mqtt/` directory contains a ready-made MQTT-to-USD connector
that updates prim attributes via the Omniverse Connect SDK. Study its architecture
and adapt the MQTT topic mapping to your safety events.

### Step 4.4: Create Alert Prims in the Scene

Before the bridge can update anything, you need visual elements in the scene that
represent alerts. Add these to your warehouse scene in Isaac Sim:

1. **Zone highlight planes** -- Flat, semi-transparent colored planes that overlay
   dangerous zones. Start invisible; the bridge makes them visible on DANGER status.
   - Create: `Create > Mesh > Plane`, scale to zone size, add a translucent red material
   - Path: `/World/Alerts/Zone_ForkLift_Danger`

2. **Alert marker spheres** -- Small spheres at camera positions that change color
   based on status (green/yellow/red).
   - Create: `Create > Mesh > Sphere`, scale to 0.3m, position at each camera location
   - Path: `/World/Alerts/Overhead_Alert`, etc.

3. **Text labels** (optional) -- USD text prims that display the current status.

### Verification

- MQTT broker is running: `mosquitto_sub` shows messages
- The inference loop (Phase 3) publishes detections to MQTT
- The bridge receives messages and updates prims in the scene
- Alert markers change color / visibility based on safety status
- The visual state of the scene reflects the current safety assessment

---

## 10. Phase 5: Kit App Streaming to Browser

**Goal:** Stream the annotated digital twin to a web browser so anyone on your
network can view the warehouse safety dashboard.

**Time estimate:** 1-2 hours (mostly configuration).

### Step 5.1: Launch Isaac Sim in Streaming Mode

Stop the GUI instance of Isaac Sim and relaunch in streaming mode:

```bash
podman run --name isaac-sim-stream -it --rm \
  --device nvidia.com/gpu=all \
  --network=host \
  -e "ACCEPT_EULA=Y" \
  -e "PRIVACY_CONSENT=Y" \
  -v ~/isaac-sim/cache/main:/isaac-sim/.cache:rw \
  -v ~/isaac-sim/cache/computecache:/isaac-sim/.nv/ComputeCache:rw \
  -v ~/isaac-sim/logs:/isaac-sim/.nvidia-omniverse/logs:rw \
  -v ~/isaac-sim/config:/isaac-sim/.nvidia-omniverse/config:rw \
  -v ~/isaac-sim/data:/isaac-sim/.local/share/ov/data:rw \
  -v ~/workspace:/workspace:rw \
  nvcr.io/nvidia/isaac-sim:5.1.0 \
  isaacsim isaacsim.exp.full.streaming --no-window
```

Wait for: `Isaac Sim Full Streaming App is loaded.`

### Step 5.2: Connect via Browser

Open Firefox (recommended over Chrome for containerized Isaac Sim) and navigate to:

```
http://localhost:8211/streaming/webrtc-client?server=localhost
```

You should see the Isaac Sim viewport rendered in your browser. You can orbit, pan,
and zoom the 3D scene interactively.

**For access from other devices on your network** (e.g., your Mac laptop, a tablet):

```
http://<workstation_ip>:8211/streaming/webrtc-client?server=<workstation_ip>
```

### Step 5.3: Alternative -- Dedicated Streaming Client

NVIDIA provides a desktop streaming client that may perform better than the browser:

```bash
wget https://download.isaacsim.omniverse.nvidia.com/isaacsim-webrtc-streaming-client-1.0.6-linux-x64.AppImage
chmod +x isaacsim-webrtc-streaming-client-1.0.6-linux-x64.AppImage
./isaacsim-webrtc-streaming-client-1.0.6-linux-x64.AppImage
# Enter workstation IP, click Connect
```

### Ports

Ensure these ports are accessible (they are, with `--network=host`):

| Port | Purpose |
|------|---------|
| 49100 | WebRTC signaling |
| 47998 | WebRTC media stream |
| 8211 | HTTP for browser client |

### Limitation

Kit App Streaming supports **one concurrent viewer** per Isaac Sim instance. If you
need multiple viewers, you would need multiple Isaac Sim instances (one per viewer),
which is a datacenter/cloud deployment pattern.

### Verification

- Browser shows the 3D warehouse scene
- You can navigate (orbit, pan, zoom) interactively
- When the MQTT bridge updates alert prims, the changes are visible in the browser
- Latency is acceptable (expect 50-200ms on localhost)

---

## 11. Phase 6: End-to-End Integration

**Goal:** Run all components simultaneously and verify the full pipeline works.

**Time estimate:** Half day (mostly debugging timing and resource contention).

### Step 6.1: Startup Order

Launch components in this order (each in its own terminal or as a background container):

```bash
# 1. MQTT Broker
podman run --name mqtt-broker -d --rm \
  -p 1883:1883 -p 9001:9001 \
  -v ~/mqtt-config/mosquitto.conf:/mosquitto/config/mosquitto.conf:ro \
  docker.io/eclipse-mosquitto:2

# 2. Isaac Sim (streaming mode, with your saved scene)
podman run --name isaac-sim -d --rm \
  --device nvidia.com/gpu=all \
  --network=host \
  -e "ACCEPT_EULA=Y" -e "PRIVACY_CONSENT=Y" \
  -v ~/isaac-sim/cache/main:/isaac-sim/.cache:rw \
  -v ~/isaac-sim/cache/computecache:/isaac-sim/.nv/ComputeCache:rw \
  -v ~/isaac-sim/logs:/isaac-sim/.nvidia-omniverse/logs:rw \
  -v ~/isaac-sim/config:/isaac-sim/.nvidia-omniverse/config:rw \
  -v ~/isaac-sim/data:/isaac-sim/.local/share/ov/data:rw \
  -v ~/workspace:/workspace:rw \
  nvcr.io/nvidia/isaac-sim:5.1.0 \
  isaacsim isaacsim.exp.full.streaming --no-window

# 3. Wait for Isaac Sim to fully load (watch logs)
podman logs -f isaac-sim  # wait for "loaded" message, then Ctrl+C

# 4. Cosmos-Reason2 inference server
podman run --name cosmos-edge -d --rm \
  --device nvidia.com/gpu=all \
  --network=host \
  -v ~/models:/models:ro \
  -v ~/workspace/camera_feeds:/camera_feeds:ro \
  docker.io/vllm/vllm-openai:latest \
  --model /models/cosmos-reason2-2b-w4a16 \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.25 \
  --max-num-seqs 2 \
  --port 8000 \
  --reasoning-parser qwen3 \
  --allowed-local-media-path /camera_feeds

# 5. Wait for vLLM to load the model
podman logs -f cosmos-edge  # wait for "Uvicorn running" message

# 6. Start the inference loop (from Phase 3 script)
python3 edge_inference.py

# 7. Start the MQTT-to-USD bridge
#    (this runs inside Isaac Sim or as a separate script connecting to the stage)
```

### Step 6.2: Monitor Resource Usage

Keep `nvidia-smi` running in a terminal to watch VRAM:

```bash
watch -n 2 nvidia-smi
```

Expected output:
```
| GPU  Name         | Memory-Usage     |  GPU-Util |
| RTX 5090          | ~20000MiB/32768MiB |   30-60% |
```

If VRAM exceeds 28 GB, reduce one of:
- Isaac Sim texture budget: `--/renderer/textureStreaming/budget=0.2`
- vLLM memory: `--gpu-memory-utilization 0.2`
- Scene complexity (remove assets)
- Camera resolution (drop to 640x480)

### Step 6.3: Verify the Full Loop

1. Open the browser stream: `http://localhost:8211/streaming/webrtc-client?server=localhost`
2. In Isaac Sim, press Play to start the physics simulation (objects move, forklifts drive)
3. Watch the camera feed directory for new frames
4. Watch the MQTT topic for analysis results:
   ```bash
   mosquitto_sub -h localhost -t "warehouse/safety/#" -v
   ```
5. Observe the digital twin in the browser -- alert markers should update based on
   what Cosmos detects in the camera feeds

### Step 6.4: Demo Scenario

Create a scripted scenario to demonstrate the system:

1. **Baseline:** Warehouse is quiet. Cosmos reports SAFE. Alert markers are green.
2. **Event:** A simulated worker walks into the forklift operating zone.
   (Move a character prim into the zone via Isaac Sim script or manual manipulation.)
3. **Detection:** Cosmos detects "person in forklift path" and reports CAUTION.
4. **Alert:** The forklift zone highlight turns yellow in the digital twin.
5. **Escalation:** The forklift begins moving toward the worker. Cosmos reports DANGER.
6. **Alert:** The zone turns red, alert marker pulses.
7. **Resolution:** Worker leaves the zone. Cosmos reports SAFE. Alerts clear.

This can be scripted in Python using Isaac Sim's API to move prims on a timeline.

### Verification

- The full pipeline runs for 10+ minutes without crashes or OOM
- Cosmos produces meaningful analysis (not garbage or hallucinations)
- MQTT messages flow from Cosmos to the bridge to USD prim updates
- The browser view reflects safety status changes in near-real-time
- `nvidia-smi` shows stable VRAM usage (no slow leak)

---

## 12. Phase 7 (Optional): GMKTec as Physical Edge Device

**Goal:** Move Cosmos-Reason2 to the GMKTec, creating a real two-machine
edge-to-datacenter architecture.

**Time estimate:** 1-2 days (ROCm setup is the wildcard).

### Prerequisites

- GMKTec is on the same network as the desktop (Tailscale or LAN)
- You have verified the full pipeline works on the desktop (Phase 6)

### Step 7.1: ROCm Setup on GMKTec

The GMKTec's Ryzen AI Max+ 395 uses the gfx1151 (Strix Halo) GPU. ROCm 7.0+ is
required.

```bash
# Install ROCm 7.0 on the GMKTec (Ubuntu or Fedora)
# Follow https://rocm.docs.amd.com/projects/install-on-linux/en/latest/
# Verify:
rocminfo | grep gfx
# Should show: gfx1151
```

### Step 7.2: vLLM with ROCm

```bash
# vLLM ROCm container
podman run --name cosmos-edge -d --rm \
  --device /dev/kfd --device /dev/dri \
  --network=host \
  -v ~/models:/models:ro \
  -v ~/camera_feeds:/camera_feeds:ro \
  docker.io/vllm/vllm-openai:latest-rocm \
  --model /models/cosmos-reason2-2b-w4a16 \
  --max-model-len 8192 \
  --max-num-seqs 2 \
  --port 8000 \
  --reasoning-parser qwen3 \
  --allowed-local-media-path /camera_feeds
```

**If ROCm + vLLM is problematic**, fall back to llama.cpp with the HIP backend:

```bash
# Build llama.cpp with ROCm/HIP support
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
cmake -B build -DGGML_HIP=ON
cmake --build build --config Release -j$(nproc)

# Convert model to GGUF format (if needed)
# Serve with llama.cpp's OpenAI-compatible server
./build/bin/llama-server \
  --model ~/models/cosmos-reason2-2b-w4a16/model.gguf \
  --port 8000 \
  --host 0.0.0.0
```

Note: llama.cpp may require converting the model to GGUF format first. Check
https://github.com/ggerganov/llama.cpp for current Cosmos-Reason2 support.

### Step 7.3: Frame Transport Over Network

The camera frames need to get from the desktop (where Isaac Sim renders them) to the
GMKTec (where Cosmos analyzes them). Options:

**Option A: NFS/SMB share (simplest)**

Mount the camera_feeds directory from the desktop on the GMKTec:

```bash
# On desktop: share ~/workspace/camera_feeds via NFS or SMB
# On GMKTec: mount it
sudo mount -t nfs <desktop_ip>:/home/jary/workspace/camera_feeds ~/camera_feeds
```

The inference loop script on the GMKTec watches the same directory.

**Option B: MQTT with image payload (self-contained)**

Modify the frame capture to publish images as base64-encoded MQTT messages.
The GMKTec subscribes to the image topic, decodes, and analyzes.

**Option C: HTTP endpoint (cleanest API)**

Add a simple HTTP server on the desktop that serves the latest camera frames.
The GMKTec's inference script fetches frames via HTTP.

### Step 7.4: Network Architecture

```
Desktop (192.168.x.10)                GMKTec (192.168.x.20)
  Isaac Sim :49100/47998/8211           Cosmos vLLM :8000
  MQTT Broker :1883                     MQTT Client -> :1883 on desktop
  Camera Feeds (NFS export)             Camera Feeds (NFS mount)
```

Or via Tailscale:
```
Desktop (100.x.x.10)                  GMKTec "gmktec" (100.x.x.20)
  Same ports                            Same setup, use Tailscale IPs
```

### Step 7.5: Update Inference Script for Remote Operation

The only change to the inference script from Phase 3 is the MQTT broker address:

```python
MQTT_BROKER = "192.168.x.10"  # or Tailscale IP of desktop
# Everything else stays the same
```

### Step 7.6: Fedora on GMKTec (Optional RHEL-Adjacent Story)

If you want to add a Red Hat angle to the edge device:

1. Install Fedora 43 on the GMKTec (or in a VM on it)
2. Install ROCm via Fedora's packaging (better integrated than on Ubuntu)
3. The "edge device runs Fedora" story is weaker than RHEL but still Red Hat ecosystem
4. Fedora bootc could be used to build an immutable edge OS image with ROCm baked in

This is only worth doing if the demo needs to show Red Hat at the edge AND you cannot
get RHEL (which you can -- see Section 4).

### Verification

- Cosmos-Reason2 runs on the GMKTec and responds to API requests
- The inference loop on the GMKTec reads frames from the shared directory
- MQTT messages from the GMKTec reach the broker on the desktop
- The digital twin updates in the browser based on GMKTec's detections
- End-to-end latency is acceptable (expect 3-8 seconds per frame analysis)

---

## 13. Phase 8 (Optional): RHEL / OpenShift Integration

**Goal:** Add Red Hat products to the architecture to demonstrate the
"Red Hat platform layer" story.

### Option A: UBI Containers (Low Effort, Good Story)

Rebuild the custom components (MQTT broker, MQTT-to-USD bridge, inference loop)
on UBI9 base images:

```dockerfile
# Dockerfile.mqtt-bridge
FROM registry.access.redhat.com/ubi9/python-311:latest

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mqtt_to_usd_bridge.py .
CMD ["python", "mqtt_to_usd_bridge.py"]
```

```dockerfile
# Dockerfile.edge-inference
FROM registry.access.redhat.com/ubi9/python-311:latest

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY edge_inference.py .
CMD ["python", "edge_inference.py"]
```

This lets you say: "The integration layer runs on Red Hat's Universal Base Image."

### Option B: OpenShift Dedicated with NIM Operator (High Effort, Strong Story)

Deploy the datacenter tier on OpenShift:

1. **Provision GPU nodes** on your OpenShift Dedicated cluster
   (A100 80GB, H100, or L40S required for NIM Operator)

2. **Install NVIDIA GPU Operator** via OperatorHub

3. **Install NIM Operator:**
   ```bash
   # Create NGC API key secret
   oc create secret generic ngc-api-key \
     --from-literal=NGC_API_KEY=$NGC_API_KEY \
     -n nvidia-nim

   # Install NIM Operator from OperatorHub
   ```

4. **Deploy Cosmos-Reason2 as a NIM:**
   ```yaml
   apiVersion: nim.nvidia.com/v1
   kind: NIMService
   metadata:
     name: cosmos-reason2
   spec:
     model: nvidia/cosmos-reason2-2b
     replicas: 1
     resources:
       gpu: 1
   ```

5. **Route edge inference through OpenShift:**
   The GMKTec (or desktop inference script) sends frames to the OpenShift-hosted
   NIM endpoint instead of localhost.

This gives you: "Edge devices send data to Cosmos running on OpenShift with NVIDIA
GPU nodes. The digital twin runs on OpenShift workloads." This is the strongest
possible Red Hat story.

### Option C: RHEL Image Mode for Edge (Medium Effort, Edge Story)

Build a RHEL bootc image for the GMKTec that includes ROCm, Cosmos model weights,
and the inference script baked in:

```dockerfile
FROM registry.redhat.io/rhel9/rhel-bootc:9.6

# Install ROCm (this is complex -- AMD provides RPMs for RHEL 9)
RUN dnf install -y rocm-hip-runtime rocm-hip-sdk

# Install Python and inference dependencies
RUN dnf install -y python3.11 python3.11-pip
RUN pip3.11 install vllm paho-mqtt requests

# Bake in the model weights
COPY models/cosmos-reason2-2b-w4a16 /opt/models/cosmos-reason2-2b-w4a16

# Bake in the inference script
COPY edge_inference.py /opt/edge/edge_inference.py

# Systemd service to start inference on boot
COPY edge-inference.service /etc/systemd/system/
RUN systemctl enable edge-inference.service
```

This produces an immutable, bootable OS image that:
- Boots directly to RHEL on the GMKTec
- Starts the Cosmos inference service automatically
- Updates atomically by pulling new images from a registry
- Can roll back to a previous version on failure

This is the **RHEL image mode at the edge** story that Brett's team is building for
Jetson. You would be doing it for AMD edge hardware with an AI workload baked in.

**Note:** This requires a RHEL subscription (free Developer Subscription works) and
ROCm RPMs for RHEL 9 from AMD.

---

## 14. VRAM Budget and Performance Tuning

### Desktop-Only Configuration (Phases 1-6)

| Component | VRAM | Tuning Lever |
|-----------|------|-------------|
| Isaac Sim (moderate scene, 720p cameras) | 10-14 GB | `--/renderer/textureStreaming/budget=0.3` |
| Cosmos-Reason2-2B W4A16 (vLLM) | 6-8 GB | `--gpu-memory-utilization 0.25` |
| CUDA contexts (2 processes) | 1-2 GB | Unavoidable |
| **Total** | **17-24 GB** | Fits in 32 GB |

### If You Hit VRAM Limits

Escalation path (try in order):

1. **Reduce texture budget** to 20%: `--/renderer/textureStreaming/budget=0.2`
2. **Enable DLSS Performance mode**: `--/rtx/post/dlss/execMode=0`
3. **Reduce camera resolution** to 640x480
4. **Reduce scene complexity** -- fewer assets, simpler materials
5. **Reduce vLLM memory** further: `--gpu-memory-utilization 0.2`
6. **Reduce max model length**: `--max-model-len 4096`
7. **Move Cosmos to CPU** (very slow, but frees all inference VRAM):
   `--device cpu` in vLLM (not practical for interactive use)
8. **Move Cosmos to GMKTec** (Phase 7) -- frees 6-8 GB on desktop

### Performance Expectations

| Metric | Desktop-Only | With GMKTec Edge |
|--------|-------------|-----------------|
| Frame analysis latency | 2-5 sec/frame | 3-8 sec/frame (network + ROCm) |
| Pipeline throughput | ~1 frame every 5 sec | ~1 frame every 5-10 sec |
| Isaac Sim FPS (viewport) | 30-60 fps | 30-60 fps (more VRAM freed) |
| Browser stream quality | Good (WebRTC adaptive) | Same |
| End-to-end event detection | 5-10 sec from event to visual alert | 10-15 sec |

These latencies are acceptable for a safety monitoring demo. Real production systems
would use lighter models (YOLO, DeepStream) for sub-second detection, with
Cosmos-Reason providing deeper analysis on flagged events.

---

## 15. Troubleshooting Guide

### Isaac Sim won't start in container

```
Error: Failed to create display
```
- Use `--network=host` and ensure `DISPLAY` is set, or use streaming mode (`--no-window`)
- For headless with cameras: use `isaacsim.exp.full.headless.rendering`

### vLLM fails to allocate memory

```
ValueError: No available memory for the cache blocks
```
- Isaac Sim is consuming too much VRAM. Reduce texture budget or scene complexity.
- Lower `--gpu-memory-utilization` (try 0.2 or 0.15)
- Ensure Isaac Sim started first and stabilized before launching vLLM

### Cosmos produces garbage output

- Check that the image file is actually a valid PNG (not 0 bytes or corrupted)
- Verify the `--allowed-local-media-path` matches the actual frame directory
- Try the curl test from Phase 3.3 with a known-good image
- If the model consistently fails, try the full FP16 model instead of W4A16

### MQTT messages not reaching the bridge

- Verify broker is running: `mosquitto_sub -h localhost -t "#"` (subscribe to all)
- Check firewall: port 1883 must be open
- Ensure the inference script and bridge use the same broker address

### Kit App Streaming shows black screen

- Wait longer -- first-run shader compilation can take 10+ minutes
- Try Firefox instead of Chrome (known Chrome issues with containerized Isaac Sim)
- Check that ports 49100, 47998, 8211 are accessible
- Verify NVENC is available: `nvidia-smi -q | grep Encoder` (RTX 5090 has it)

### ROCm issues on GMKTec (Phase 7)

- Verify ROCm detects the GPU: `rocminfo | grep gfx`
- If gfx1151 is not listed, you need ROCm 7.0+
- If vLLM crashes, try llama.cpp with HIP backend as fallback
- Check https://github.com/ROCm/ROCm/issues for Strix Halo issues

### Isaac Sim runs out of disk space

- Shader cache can grow to 10+ GB. Clear with:
  ```bash
  rm -rf ~/isaac-sim/cache/main/*
  rm -rf ~/isaac-sim/cache/computecache/*
  ```
- First run after clearing will be slow again (recompilation)

---

## 16. Key Resources

### Container Images

| Image | Purpose | Size |
|-------|---------|------|
| `nvcr.io/nvidia/isaac-sim:5.1.0` | Isaac Sim | ~20 GB |
| `docker.io/vllm/vllm-openai:latest` | Cosmos inference (CUDA) | ~8 GB |
| `docker.io/vllm/vllm-openai:latest-rocm` | Cosmos inference (ROCm) | ~10 GB |
| `docker.io/eclipse-mosquitto:2` | MQTT broker | ~10 MB |

### GitHub Repositories

| Repo | What For |
|------|----------|
| [isaac-sim/IsaacSim](https://github.com/isaac-sim/IsaacSim) | Isaac Sim source (for building from source if needed) |
| [isaac-sim/IsaacSimZMQ](https://github.com/isaac-sim/IsaacSimZMQ) | ZMQ extension for streaming camera frames |
| [NVIDIA-Omniverse/iot-samples](https://github.com/NVIDIA-Omniverse/iot-samples) | MQTT-to-USD connector reference |
| [NVIDIA-Omniverse/web-viewer-sample](https://github.com/NVIDIA-Omniverse/web-viewer-sample) | Kit App Streaming web client |
| [nvidia-cosmos/cosmos-reason2](https://github.com/nvidia-cosmos/cosmos-reason2) | Cosmos-Reason2 model code |

### Models

| Model | HuggingFace | Size | Use |
|-------|-------------|------|-----|
| Cosmos-Reason2-2B W4A16 | [embedl/Cosmos-Reason2-2B-W4A16-Edge2](https://huggingface.co/embedl/Cosmos-Reason2-2B-W4A16-Edge2) | ~1.5 GB | Primary (quantized, low VRAM) |
| Cosmos-Reason2-2B FP16 | [nvidia/Cosmos-Reason2-2B](https://huggingface.co/nvidia/Cosmos-Reason2-2B) | ~4 GB | Higher quality alternative |

### Assets

| Asset | Source | Size |
|-------|--------|------|
| SimReady Warehouse | [nvidia/PhysicalAI-SimReady-Warehouse-01](https://huggingface.co/datasets/nvidia/PhysicalAI-SimReady-Warehouse-01) | ~15 GB |
| Additional industrial packs | [Omniverse Downloadable Packs](https://docs.omniverse.nvidia.com/usd/latest/usd_content_samples/downloadable_packs.html) | Varies |

### Documentation

| Topic | URL |
|-------|-----|
| Isaac Sim 5.1 docs | https://docs.isaacsim.omniverse.nvidia.com/5.1.0/ |
| Isaac Sim container install | https://docs.isaacsim.omniverse.nvidia.com/5.0.0/installation/install_container.html |
| Isaac Sim camera sensors | https://docs.isaacsim.omniverse.nvidia.com/5.1.0/sensors/isaacsim_sensors_camera.html |
| Kit App Streaming | https://docs.omniverse.nvidia.com/ovas/latest/index.html |
| Cosmos-Reason2 API | https://docs.nvidia.com/nim/vision-language-models/1.6.0/examples/cosmos-reason2/api.html |
| NVIDIA CDI support | https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/cdi-support.html |
| Omniverse IoT integration | https://developer.nvidia.com/blog/connect-real-time-iot-data-to-digital-twins-for-3d-remote-monitoring/ |

---

## 17. What You Will Learn

By completing this project through Phase 6, you will be able to answer every question
Itamar, Brett, and Kelly will ask:

| Question | You Will Know |
|----------|--------------|
| "What does it mean to deploy Cosmos?" | Exactly what containers, models, and GPU resources are needed |
| "What does Cosmos actually do with video?" | You will have seen it analyze warehouse scenes and produce structured safety assessments |
| "What does a digital twin look like?" | You will have built one in Isaac Sim with SimReady industrial assets |
| "How does edge inference feed a digital twin?" | You will have built the MQTT pipeline connecting them |
| "Does this work on RHEL?" | You will know that the container layer is host-agnostic, and that UBI containers work |
| "What hardware does this need?" | You will have VRAM budgets, latency numbers, and disk requirements |
| "What's a plausible demo scenario?" | You will have a scripted safety monitoring scenario with visual alerts |
| "Can this run on OpenShift?" | You will understand which components can (NIM, MQTT) and which need RTX GPUs (Isaac Sim) |
| "What about Siemens?" | You will understand how Digital Twin Composer relates to what you built (it is the Siemens-branded version of the same Omniverse-based pattern) |

### Skills Acquired

- Isaac Sim scene building and camera simulation
- OpenUSD scene graph manipulation (prim creation, attribute updates)
- Cosmos-Reason2 inference (prompt engineering, structured output, vLLM serving)
- MQTT-based IoT data integration with Omniverse
- Kit App Streaming (WebRTC) for remote visualization
- VRAM budgeting for multi-workload GPU sharing
- Container-based deployment with Podman and CDI

---

## 18. Deliverables

At the end of this project, you should have:

1. **A working warehouse digital twin** in Isaac Sim with simulated cameras
2. **An edge inference pipeline** that analyzes camera feeds with Cosmos-Reason2
3. **An MQTT-based integration** connecting edge inference to the digital twin
4. **A browser-accessible dashboard** showing the annotated digital twin
5. **A scripted demo scenario** (safety event detection and alerting)
6. **Technical notes** documenting:
   - Hardware requirements and VRAM budgets
   - What works, what doesn't, and what needs workarounds
   - Architecture diagram suitable for sharing with Itamar/Brett/Kelly
   - Assessment of where RHEL/OpenShift/MicroShift add value
7. **(Optional) GMKTec edge device** running Cosmos as a physically separate node
8. **(Optional) UBI-based containers** for the Red Hat platform story
