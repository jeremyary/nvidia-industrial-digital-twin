# Claude Code Prompt -- Warehouse Safety Digital Twin Project

Copy this into your first Claude Code prompt in the new project workspace.

---

## Prompt

I'm building a warehouse safety monitoring system that uses NVIDIA Isaac Sim for a digital twin and Cosmos-Reason2-2B for edge AI inference. The full project plan is in `project-plan-warehouse-safety-digital-twin.md` -- read it thoroughly before we start.

Here's a summary of the architecture:

1. **Isaac Sim 5.1** renders a warehouse scene with simulated security cameras (using SimReady Warehouse assets from HuggingFace)
2. Camera frames are extracted and sent to **Cosmos-Reason2-2B** (W4A16 quantized variant, served via vLLM)
3. Cosmos analyzes each frame for safety hazards (workers in forklift paths, fallen objects, blocked exits) and outputs structured JSON
4. A lightweight Python service publishes detections to an **MQTT broker** (Mosquitto)
5. An **MQTT-to-USD bridge** receives detections and updates USD prim attributes in the Isaac Sim scene (alert markers, zone highlights)
6. **Kit App Streaming** (WebRTC) streams the annotated digital twin to a web browser

Everything starts on a single machine, then optionally splits edge inference to a separate device later.

### My hardware

- **Primary workstation:** ORIGIN PC, Ubuntu Desktop, RTX 5090 (32GB VRAM), 128GB RAM, i9-13900K
- **Optional edge device (later):** GMKTec Evo-X2, AMD Ryzen AI Max+ 395, 128GB unified RAM, 2TB SSD
- **NAS:** QNAP TS-464, on Tailscale as "nastorious"
- **OpenShift Dedicated** available if needed (possible GPU nodes)

### VRAM budget (both on desktop)

| Component | VRAM | Key flags |
|-----------|------|-----------|
| Isaac Sim (moderate scene, 720p cams) | 10-14 GB | `--/renderer/textureStreaming/budget=0.3` |
| Cosmos-Reason2-2B W4A16 (vLLM) | 6-8 GB | `--gpu-memory-utilization 0.25` |
| CUDA contexts (2 processes) | 1-2 GB | |
| **Total** | **17-24 GB** | Fits in 32 GB |

### Container images needed

- `nvcr.io/nvidia/isaac-sim:5.1.0` (~20GB)
- `docker.io/vllm/vllm-openai:latest` (~8GB)
- `docker.io/eclipse-mosquitto:2` (~10MB)

### Key accounts (I have these set up)

- NGC (nvcr.io authenticated via podman)
- HuggingFace (authenticated via huggingface-cli)
- NVIDIA Developer

### What I want to accomplish in our first session

Let's start with **Phase 1** from the plan: getting Isaac Sim running in a container with a warehouse scene loaded. Specifically:

1. Pull the Isaac Sim 5.1 container
2. Set up the persistent cache/config directories
3. Launch Isaac Sim (try GUI mode first, fall back to streaming mode if display forwarding is an issue)
4. Download the SimReady Warehouse dataset from HuggingFace
5. Load the pre-built warehouse scene or build a simpler custom scene (50-100 assets to keep VRAM reasonable)
6. Add 2-3 cameras at security camera positions
7. Verify the scene renders and cameras produce frames

### Constraints

- Use **Podman** (not Docker) for all containers
- GPU passthrough via **CDI** (`--device nvidia.com/gpu=all`), not `--gpus all`
- I'm on **Ubuntu Desktop** -- this is my primary workstation, not a server
- I'm a Red Hat employee learning this stack for an industrial AI initiative. The project plan has full context on why I'm doing this.
- I have no prior experience with Isaac Sim, Omniverse, or OpenUSD. I've used Cosmos-Reason2 via vLLM and NIM before.

### Reference files

I've copied several research documents into this workspace. Key ones:
- `project-plan-warehouse-safety-digital-twin.md` -- the master plan (read this first)
- `nvidia-cosmos-blueprints-research.md` -- Cosmos model details, families, capabilities
- `research-omniverse-digital-twins.md` -- digital twin concepts, Omniverse architecture
- `nvidia-hardware-platforms-research.md` -- Jetson/IGX/DGX hardware details
- `action-plan-industrial-nvidia-rampup.md` -- broader ramp-up context and tasking from management

Let's get started with Phase 1.
