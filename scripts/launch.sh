#!/usr/bin/env bash
# Launch all containers for the warehouse safety digital twin.
# Usage: ./scripts/launch.sh [start|stop|status]

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Container images
ISAAC_IMAGE="nvcr.io/nvidia/isaac-sim:5.1.0"
VLLM_IMAGE="docker.io/vllm/vllm-openai:latest"
MQTT_IMAGE="docker.io/eclipse-mosquitto:2"

start_mqtt() {
    if podman ps --format '{{.Names}}' | grep -q '^mqtt-broker$'; then
        echo "mqtt-broker already running"
        return
    fi
    echo "Starting MQTT broker..."
    podman run --name mqtt-broker -d --rm \
        -p 1883:1883 \
        -p 9001:9001 \
        -v "${PROJECT_DIR}/mqtt-config/mosquitto.conf:/mosquitto/config/mosquitto.conf:ro" \
        "${MQTT_IMAGE}"
}

start_isaac() {
    if podman ps --format '{{.Names}}' | grep -q '^isaac-sim$'; then
        echo "isaac-sim already running"
        return
    fi
    echo "Starting Isaac Sim (streaming mode)..."
    podman run --name isaac-sim -d --rm \
        --device nvidia.com/gpu=all \
        --network=host \
        -e "ACCEPT_EULA=Y" \
        -e "PRIVACY_CONSENT=Y" \
        -v "${PROJECT_DIR}/isaac-sim/cache/main:/isaac-sim/.cache:rw" \
        -v "${PROJECT_DIR}/isaac-sim/cache/computecache:/isaac-sim/.nv/ComputeCache:rw" \
        -v "${PROJECT_DIR}/isaac-sim/logs:/isaac-sim/.nvidia-omniverse/logs:rw" \
        -v "${PROJECT_DIR}/isaac-sim/data:/isaac-sim/.local/share/ov/data:rw" \
        -v "${HOME}/.nvidia-omniverse/config:/isaac-sim/.nvidia-omniverse/config:rw" \
        -v "${PROJECT_DIR}/workspace:/workspace:rw" \
        -v "${PROJECT_DIR}/simready-warehouse:/simready-warehouse:ro" \
        "${ISAAC_IMAGE}" \
        isaacsim isaacsim.exp.full.streaming --no-window \
        --/rtx-transient/resourcemanager/texturestreaming/memoryBudget=0.375 \
        --/rtx/post/dlss/execMode=1
    echo "Waiting for Isaac Sim to load (watch logs with: podman logs -f isaac-sim)"
}

start_cosmos() {
    if podman ps --format '{{.Names}}' | grep -q '^cosmos-edge$'; then
        echo "cosmos-edge already running"
        return
    fi
    echo "Starting Cosmos-Reason2 inference server..."
    podman run --name cosmos-edge -d --rm \
        --device nvidia.com/gpu=all \
        --network=host \
        -v "${PROJECT_DIR}/models:/models:ro" \
        -v "${PROJECT_DIR}/workspace/camera_feeds:/camera_feeds:ro" \
        "${VLLM_IMAGE}" \
        --model /models/cosmos-reason2-2b-w4a16 \
        --max-model-len 8192 \
        --gpu-memory-utilization 0.25 \
        --max-num-seqs 2 \
        --port 8000 \
        --reasoning-parser qwen3 \
        --allowed-local-media-path /camera_feeds
    echo "Waiting for vLLM to load model (watch logs with: podman logs -f cosmos-edge)"
}

stop_all() {
    echo "Stopping containers..."
    for name in cosmos-edge mqtt-broker isaac-sim; do
        if podman ps --format '{{.Names}}' | grep -q "^${name}$"; then
            echo "  Stopping ${name}..."
            podman stop "${name}" 2>/dev/null || true
        fi
    done
    echo "All stopped."
}

show_status() {
    echo "=== Container Status ==="
    for name in mqtt-broker isaac-sim cosmos-edge; do
        status=$(podman ps --format '{{.Status}}' --filter "name=^${name}$" 2>/dev/null || echo "not running")
        if [ -z "$status" ]; then
            status="not running"
        fi
        printf "  %-15s %s\n" "${name}" "${status}"
    done
    echo ""
    echo "=== GPU Memory ==="
    nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader 2>/dev/null || echo "  nvidia-smi not available"
}

case "${1:-status}" in
    start)
        start_mqtt
        start_isaac
        start_cosmos
        echo ""
        echo "All containers launched."
        echo "Next steps:"
        echo "  1. Wait for Isaac Sim to load: podman logs -f isaac-sim"
        echo "  2. Connect streaming client to 127.0.0.1"
        echo "  3. Open scene and run workspace scripts in Script Editor:"
        echo "     exec(open('/workspace/create_alerts.py').read())"
        echo "     exec(open('/workspace/mqtt_bridge.py').read())"
        echo "  4. Run edge inference: python3 scripts/edge_inference.py"
        ;;
    stop)
        stop_all
        ;;
    status)
        show_status
        ;;
    *)
        echo "Usage: $0 [start|stop|status]"
        exit 1
        ;;
esac
