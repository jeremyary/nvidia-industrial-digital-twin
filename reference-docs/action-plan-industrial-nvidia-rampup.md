# Industrial NVIDIA Ramp-Up -- Action Plan

**Created:** March 15, 2026
**Source:** March 13 meeting with Itamar Heim and Brett Thurber
**Context:** Read the learning material documents first, then use this as your execution guide.

---

## What Was Actually Asked of You

Pulling directly from the transcript (not just Rook's summary), here is everything Itamar
asked for, with the nuance preserved:

| # | Ask | Itamar's Exact Framing | Priority |
|---|-----|----------------------|----------|
| 1 | Ramp up on Cosmos and Omniverse | "ramp up and figure out how to deploy -- what does it mean to deploy them" | Immediate |
| 2 | Track Graphics Processing Unit (GPU) Technology Conference (GTC) announcements | "Track what Nvidia is announcing next week around that space of industrial models" | This week (Mar 16-19) |
| 3 | Watch Siemens at GTC | "Watch for what Siemens announcing next week with Nvidia as well" | This week |
| 4 | Catch the GTC keynote | "catch up on the keynote for GTC" | Mon Mar 16 |
| 5 | Figure out deployment architecture | "needs to work on Red Hat Enterprise Linux (RHEL) is the minimum requirement" | Near-term |
| 6 | Get it working as-is first | "I'm not asking to create a quick start just like take the Nvidia stuff as is" | Near-term |
| 7 | Then figure out the Red Hat improvement story | "what would we improve in the story if we could use OpenShift AI" | After #6 |
| 8 | Define demo flow | "work with Brett and Kelly Swit on what's the actual demo flow" | After ramp-up |
| 9 | Delegate to a human | "have someone else in the loop doing things... not an AI agent, rather a human" | Ongoing from start |
| 10 | Status updates | "needs to go into Amy's edge update and into Amy's NVIDIA update" | Weekly, starting now |
| 11 | Request GTC session content | "if there's a session that seems interesting, we could ask for its content" | During/after GTC |

### What was NOT asked

- Do NOT build a quickstart ("I'm not asking to create a quick start")
- Do NOT over-engineer the deployment story yet ("first step is just get it to work as is")
- Do NOT assume these are Large Language Model (LLM) workloads ("they're not about LLM at all because they're
  analyzing audio video" -- Itamar acknowledged uncertainty here)

### The constraint you must plan around

AMD fire drills are expected to resume. Brett literally said "I expect that call April 1st
at 7 a.m." That gives you roughly **2 weeks of focused time** before potential disruption.
Everything below is structured to maximize what gets done in that window and ensure someone
else can continue if you get pulled away.

---

## Phase 1: GTC Week (Mar 16-19) -- Watch and Learn

This phase is passive research. No hands-on deployment work yet. The goal is to absorb
what NVIDIA announces so your ramp-up is informed by the latest state of things, not stale
information.

### 1.1 Watch the Keynote (Monday Mar 16)

Jensen Huang keynote is Monday March 16 at 11 AM PT.

**What to watch for:**
- Cosmos updates (new models, new capabilities, industrial-specific features)
- Omniverse updates (new integrations, new APIs, containerization improvements)
- Siemens announcements (Digital Twin Composer General Availability (GA) timeline, new joint offerings)
- Any NEW industrial model announcements (beyond Cosmos and Omniverse)
- Data center GPU (DGX) Spark availability updates
- Isaac robotics updates (relevant to the Advanced GPU-accelerated computing for neXt-gen machines (AGX)/drone use case)
- Any mention of Red Hat, OpenShift, or RHEL in partner announcements

**Where to watch:**
- Free, no registration required
- NVIDIA will stream it on their site and likely YouTube
- Recording will be available on NVIDIA On-Demand afterwards

**Action:** Take notes on anything that changes the picture painted by the learning
material. If NVIDIA announces something new that's relevant, flag it to Itamar (he's
there in person and may already know, but confirmation is valuable).

### 1.2 Monitor GTC Sessions (Mar 16-19)

**Session catalog:** https://www.nvidia.com/gtc/session-catalog/

Filter by these topics to find relevant sessions:
- Industry: Manufacturing, Robotics, Industrial
- Technology: Omniverse, Cosmos, Digital Twin, Isaac
- Level: Any (attend introductory ones for ramp-up, technical ones for depth)

**Known relevant sessions:**
- Sessions on Omniverse Replicator + Cosmos for synthetic data generation
- Sessions on physical AI development with Isaac and Omniverse
- Session on accelerating grid modernization with Omniverse digital twins (S81683)

**Action:** Identify 3-5 sessions most relevant to your work. If they're not publicly
available, Itamar said to request slides/content: "we could ask for its content
regardless of being published or not, like at least for the slides." Use your NVIDIA
account team contact or the NVIDIA Developer Forums to request.

**Post-GTC:** Session recordings are expected to be uploaded free to NVIDIA On-Demand
(https://www.nvidia.com/en-us/on-demand/) based on past GTC precedent.

### 1.3 Track Siemens Announcements

**What to watch for:**
- Digital Twin Composer updates (currently early access, GA expected mid-2026)
- Any new Siemens + NVIDIA joint blueprints or reference architectures
- PepsiCo digital twin case study details (named as early adopter at CES 2026)
- Anything about the Erlangen AI-driven factory (first fully AI-driven manufacturing site)

**Key context from research:** The "$1-2B investment" Itamar mentioned is not an equity
stake. NVIDIA invested $500M in its own Germany-based industrial AI cloud, and Siemens
contributes AI specialists + software expertise. The partnership is a technology
collaboration, not an acquisition. See `siemens-nvidia-gtc-industrial-ai.md` section 1
for full details.

**Resources:**
- Siemens + NVIDIA partnership page: https://www.nvidia.com/en-us/industries/industrial-sector/siemens/
- Digital Twin Composer intro: https://www.siemens.com/global/en/company/digital-transformation/industrial-metaverse/introducing-digital-twin-composer.html

### 1.4 Deliverable: GTC Summary

By end of week (Friday Mar 20), produce a short summary of what changed:
- New announcements that affect your work
- Updated timelines for anything relevant
- Sessions you want to follow up on
- Any shifts in what Cosmos/Omniverse can do vs. what the learning material says

Share this with Itamar and Brett. This also becomes your first status update content.

---

## Phase 2: Hands-On Ramp-Up (Mar 20 - Mar 28) -- Understand the Models

This is the core ramp-up phase. The goal is to answer Itamar's question: "what does it
mean to deploy them?"

### 2.1 Set Up Access (Day 1)

Before touching any models, get your accounts and access ready:

| Step | Action | URL |
|------|--------|-----|
| 1 | Create NGC account (free) | https://ngc.nvidia.com/signin/email |
| 2 | Generate NGC Application Programming Interface (API) key | https://org.ngc.nvidia.com/setup/api-key (select "NGC Catalog") |
| 3 | Clone Cosmos repos | https://github.com/nvidia-cosmos |
| 4 | Clone Cosmos Cookbook | https://github.com/nvidia-cosmos/cosmos-cookbook |
| 5 | Bookmark Omniverse developer page | https://developer.nvidia.com/omniverse/get-started/ |
| 6 | Download Omniverse (individual, free) | https://www.nvidia.com/en-us/omniverse/download/ |

### 2.2 Cosmos Ramp-Up

#### What Cosmos actually is

Cosmos is a family of **world foundation models** -- AI that understands the physical world
(video, 3D space, physics), not text. This is fundamentally different from LLM work.

Three model families, each with a different purpose:

| Family | What It Does | Sizes | Edge-Capable? |
|--------|-------------|-------|---------------|
| **Cosmos-Predict** | Generates video/world scenarios from text, image, or video input | 2B, 7B, 14B | No (x86_64 only, 80GB+ VRAM) |
| **Cosmos-Transfer** | World-to-world transfer with conditioning (depth, segmentation, LiDAR) | 2B | No (x86_64 only) |
| **Cosmos-Reason** | Physical reasoning VLM -- understands video, answers questions about physical scenarios | 2B, 7B, 8B | Yes (runs on Jetson) |

**Critical insight:** Only Cosmos-Reason runs on Jetson edge devices. The Predict and
Transfer models are datacenter-only (they need x86_64 architecture and 80GB+ VRAM GPUs).
When Itamar said "Cosmos can run both on multi-GPU and Jetson," he was partially right --
but only for the Reason family.

#### What fits on Brett's Orin hardware

| Hardware | What Runs | How |
|----------|-----------|-----|
| Jetson AGX Orin 64GB | Cosmos-Reason2-2B (16-bit floating point (FP16) unquantized) | vLLM container for Jetson |
| Jetson AGX Orin 64GB | Cosmos-Reason2-8B (quantized) | vLLM container for Jetson |
| Jetson Orin Nano 8GB | Cosmos-Reason2-2B (W4A16 quantized only) | Barely -- must stop desktop, no headroom |

#### Hands-on steps: Run Cosmos-Reason on a workstation first

Before going to Jetson hardware, get familiar on your own machine. Your desktop has a 5090
(32GB VRAM) which can run the smaller models.

**Path A: Direct inference (recommended for learning)**
1. Clone: `git clone https://github.com/nvidia-cosmos/cosmos-reason2`
2. Follow the README for environment setup (Conda or Docker)
3. Download Cosmos-Reason2-2B weights from HuggingFace:
   https://huggingface.co/nvidia (search for cosmos-reason2)
4. Dependencies: PyTorch, Compute Unified Device Architecture (CUDA) 12.4+, vLLM >= 0.11.0, transformers >= 4.57.0
5. Run inference on sample video inputs
6. Understand what the model actually does: you feed it video, it reasons about the
   physical world depicted in it

**Path B: NVIDIA Inference Microservice (NIM) container (closer to production deployment)**
1. Authenticate: `echo "$NGC_API_KEY" | podman login nvcr.io --username '$oauthtoken' --password-stdin`
2. Pull a Cosmos NIM (note: these need 80GB+ VRAM, so your 5090 won't run the Predict
   NIMs, but try the Reason ones)
3. NIM containers expose a REST API at `/v1/infer` on port 8000
4. Test the API with sample requests

**NIM gotchas on RHEL/Podman:**
- Set `no-cgroups = true` in `/etc/nvidia-container-runtime/config.toml` for rootless
- Use `--pids-limit=-1` with podman run to avoid NIM startup failures
- GPU passthrough: `--gpus all` or use CDI

#### Hands-on steps: Run Cosmos-Reason on Brett's Orin

After understanding the model on your workstation, coordinate with Brett to test on
actual Jetson hardware.

1. Use the official tutorial: https://huggingface.co/blog/nvidia/cosmos-on-jetson
2. Use pre-built vLLM container for Jetson: `nvcr.io/nvidia/vlm:26.01-py3`
3. For 8GB Orin Nano: use quantized model from
   https://huggingface.co/embedl/Cosmos-Reason2-2B-W4A16-Edge2
4. For 64GB AGX Orin: can run unquantized FP16
5. Test with real-time webcam inference via the Live VLM WebUI

**Important:** NIM containers do NOT run on Jetson (x86_64 only). On Jetson, you use
vLLM containers built for aarch64 with model weights from HuggingFace directly. This is
a key architectural difference to understand for deployment planning.

#### What to learn and document

After running Cosmos, you should be able to answer:
- What does Cosmos-Reason actually do when you feed it video? What kind of output?
- How fast is inference on different hardware?
- What would this be useful for in an industrial setting?
- What's the deployment complexity? (container size, startup time, GPU memory usage)
- Could a factory use this for video-based inspection? Robot guidance? Something else?

### 2.3 Omniverse Ramp-Up

#### The key constraint

Omniverse does NOT run on Jetson. It requires multi-GPU datacenter infrastructure or at
minimum an NVIDIA RTX workstation GPU. Your desktop 5090 can run Omniverse for development
and learning.

**Also important:** Omniverse bare-metal development is Ubuntu-only. It does NOT run
natively on RHEL. For the Red Hat story, Omniverse runs containerized on OpenShift with GPU
nodes, using the NVIDIA GPU Operator.

#### Hands-on steps: Explore Omniverse

1. Download Omniverse (individual developer, free):
   https://www.nvidia.com/en-us/omniverse/download/
   - Note: Omniverse Launcher was deprecated Oct 2025. Use the current download method.
   - Requires NVIDIA RTX GPU (Turing or later -- your 5090 qualifies)
   - Requires driver >= 550.54.15 (Linux) or >= 551.78 (Windows)

2. Install Kit Software Development Kit (SDK) template:
   https://github.com/NVIDIA-Omniverse/kit-app-template
   - Templates: Kit Service (headless), Kit Base Editor (GUI), USD Composer, etc.
   - Languages: Python and C++
   - Docs: https://docs.omniverse.nvidia.com/kit/docs/kit-app-template/latest/docs/intro.html

3. Explore a sample digital twin scene:
   - Open one of the sample USD scenes included with Omniverse
   - Understand what a "digital twin" looks like in practice
   - Navigate, inspect, understand the OpenUSD scene graph

4. If you want structured learning, there's a DLI course: "Developing an Omniverse
   Kit-Based Application" (requires NVIDIA account, may have a cost)

#### What "deployment" means for Omniverse

This is different from Cosmos. Omniverse is not a single model you deploy -- it's a
platform with multiple components:

| Component | What It Does | Deployment Model |
|-----------|-------------|-----------------|
| Nucleus Server | Central asset storage/collaboration | Containerized (available on NGC) |
| Kit Applications | Custom 3D applications | Containerized or desktop |
| Kit App Streaming | Stream Kit apps to web browsers | Cloud/OpenShift deployment |
| Microservices | Rendering, physics, simulation | Containerized, GPU-required |

For OpenShift deployment, the relevant path is:
- NVIDIA GPU Operator supports OpenShift 4.14+ (RHEL 9.2/9.4/9.6 on x86)
- Kit Kernel Container available on NGC: `nvcr.io/nvidia/omniverse-kit`
- Supported GPUs on OpenShift: T4, V100, L4, L40s, A10, A100, H100, H200
- GPU Operator docs: https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/platform-support.html

#### What to learn and document

After exploring Omniverse, you should be able to answer:
- What does a digital twin look like in Omniverse?
- What kind of data do you need to build one? (3D models, sensor data, Internet of Things (IoT) feeds)
- What does "running Omniverse on OpenShift" actually mean? (Which components?)
- What GPU resources does it need?
- How would Omniverse connect to a factory's existing systems?

### 2.4 Understand the Relationship

After working with both independently, map how they connect:

```
OMNIVERSE (datacenter)              COSMOS (datacenter + edge)
  |                                    |
  |  Creates synthetic training        |  Understands/reasons about
  |  data from digital twin            |  the physical world from
  |  simulations                       |  video/sensor input
  |                                    |
  +--- Cosmos Predict generates ------>+  Trained on synthetic +
  |    synthetic video from            |  real-world data
  |    Omniverse scenes                |
  |                                    |
  +--- Cosmos Transfer converts ------>+  Converts simulation
       Omniverse renders to                output to realistic
       photorealistic video                training data
```

The Mega Blueprint is the concrete example of this: it uses Omniverse for warehouse/factory
digital twin simulation and Cosmos for synthetic data generation to train robot navigation.

### 2.5 Explore Relevant Blueprints

Blueprints are pre-packaged reference architectures. They show you how NVIDIA envisions
these models being deployed together.

**Available industrial blueprints:**

| Blueprint | Where | What It Shows |
|-----------|-------|---------------|
| **Mega** (multi-robot fleet testing) | Preview on build.nvidia.com | Warehouse/factory digital twins with robot fleet sim |
| **CAE Digital Twins (Fluid Simulation)** | https://github.com/NVIDIA-Omniverse-blueprints/digital-twins-for-fluid-simulation | Real-time CFD with Omniverse |
| **AV Simulation** | NGC | Replay driving data, closed-loop testing |
| **Earth-2 Weather Analytics** | https://github.com/NVIDIA-Omniverse-blueprints | Weather/climate digital twin |

**Action:** Look at the Mega Blueprint and the CAE Digital Twins blueprint. These are
the closest to the industrial use case Itamar described. Understand what's in a blueprint:
models, configs, pipelines, and deployment instructions.

**How to access:**
1. Install NGC Command-Line Interface (CLI) v4.10.0+
2. Authenticate with your NGC API key
3. Browse: https://catalog.ngc.nvidia.com/ (search for "blueprint")
4. GitHub repos: https://github.com/NVIDIA-Omniverse-blueprints and
   https://github.com/NVIDIA-AI-Blueprints

### 2.6 Deliverable: Technical Assessment

By end of this phase (around Mar 28), produce a document that covers:

1. **What Cosmos is and does** -- in your own words, not marketing material
2. **What Omniverse is and does** -- same
3. **What runs where** -- which models/components are datacenter, which are edge, which
   are both
4. **What runs on RHEL today** -- what works, what doesn't, what needs workarounds
5. **What "deployment" means** -- for each model/platform, what does deploying it look like?
6. **The audio/video question** -- Itamar said these models "analyze audio video, not text."
   Clarify: Cosmos-Reason is a VLM (vision-language model) that processes video + text
   prompts. It does NOT currently process audio. This is an important correction.
7. **Initial thoughts on demo scenarios** -- based on what you now know, what are 2-3
   plausible demo stories?

Share this with Itamar, Brett, and Kelly Swit. This becomes the foundation for the demo
flow discussion.

---

## Phase 3: Deployment Architecture (Mar 28 - Apr 7) -- Make It Work on RHEL

Itamar's ordering was explicit:
1. "First step is just get it to work as is"
2. "Then what would we improve in the story if we could use OpenShift AI"

### 3.1 Step 1: Get Cosmos Running on RHEL (Minimum Viable)

**Target:** Cosmos-Reason2-2B running on RHEL with Podman.

This is the simplest path -- RHEL + Podman + inference container. No Kubernetes.

| Component | Choice | Why |
|-----------|--------|-----|
| OS | RHEL 10 (or 9.6) | "needs to work on RHEL is the minimum requirement" |
| Container runtime | Podman | Red Hat standard; NIM officially supports it |
| GPU access | NVIDIA Container Toolkit + CDI | Standard GPU passthrough for Podman |
| Model serving | vLLM container | Works on both x86 and aarch64 (Jetson) |
| Model | Cosmos-Reason2-2B | Smallest, runs on widest hardware range |

**Steps:**
1. RHEL 10 installed with GPU drivers
2. Install Podman + NVIDIA Container Toolkit
3. Configure rootless containers: `no-cgroups = true` in nvidia-container-runtime config
4. Pull vLLM container from NGC
5. Download Cosmos-Reason2-2B weights from HuggingFace
6. Run inference, verify it works
7. Expose an API endpoint on the LAN

**This proves:** NVIDIA industrial AI models can run on RHEL without Kubernetes.

### 3.2 Step 2: Get Cosmos Running on Jetson with RHEL Image Mode

**Target:** Cosmos-Reason2-2B running on Jetson AGX Orin with a RHEL bootc image.

This is where Brett's work and your work converge:
- Brett has the path to build RHEL bootc images for Jetson
- You have the model and know how to deploy it
- Together: RHEL image mode on Jetson running Cosmos

**Steps:**
1. Coordinate with Brett for a bootc-built RHEL image for Jetson AGX Orin
2. Bake NVIDIA drivers into the bootc image (Brett's lane)
3. Include Podman + NVIDIA Container Toolkit in the image
4. Deploy Cosmos-Reason2-2B via vLLM container
5. Test inference on edge hardware

**This proves:** The full edge story -- Red Hat OS, NVIDIA hardware, NVIDIA AI models,
all working together at the edge.

### 3.3 Step 3: Evaluate the OpenShift AI Story (If Applicable)

Only do this after Steps 1 and 2 work. The question is: does adding OpenShift AI improve
anything?

**When Red Hat OpenShift AI (RHOAI) adds value:**
- Multiple models served with lifecycle management
- Model pipelines (preprocessing -> inference -> postprocessing)
- Multi-user model serving with authentication
- Integration with model training workflows
- Monitoring and observability

**When RHOAI is overkill:**
- Single model on a single edge device
- No Kubernetes needed for the workload
- The models don't use standard LLM serving patterns (Cosmos-Predict uses custom APIs)

**For the edge (Jetson):** RHOAI doesn't run on Jetson. MicroShift or Single Node OpenShift (SNO) might, but
the question is whether they add value beyond Podman. Brett says Thor has enough compute
for SNO -- but "I don't care right now. RHEL image mode, MicroShift, OpenShift -- that's
an after discussion" (Itamar, 00:06:35).

**For the datacenter (Omniverse):** RHOAI on OpenShift with GPU nodes could run Omniverse
Kit containers and Cosmos Predict NIMs. This is the datacenter half of the story.

### 3.4 Deliverable: Architecture Recommendation

A short document covering:
- What works today on RHEL (with evidence -- you ran it)
- What the minimal edge deployment looks like
- What the datacenter deployment looks like
- Whether RHOAI adds value and where
- A recommendation for the demo architecture

---

## Phase 4: Demo Story (Apr 1+) -- Define What We Show

This phase may overlap with or be interrupted by AMD fire drills (Brett expects "that call
April 1st at 7 a.m."). This is exactly why delegation matters -- Phase 4 should be
executable by your delegate even if you get pulled away.

### 4.1 The Open Question

Itamar explicitly does not know what the demo should be:

> "What's a demo world model? Is it a factory? Is it a Google map? Is it you know it's
> like what's we're actually the story we want to tell there."

And:

> "This one we just said we don't know how to validate because deploying is not enough.
> So need to figure out what to do with them."

### 4.2 Plausible Demo Scenarios

Based on the research, here are scenarios to evaluate with Brett and Kelly Swit:

**Scenario A: Factory Inspection with Cosmos-Reason**
- Camera feed from a factory floor (or simulated feed)
- Cosmos-Reason2 analyzes video in real-time on Jetson edge device
- Identifies safety violations, equipment anomalies, process deviations
- Running on RHEL image mode on Jetson
- **Pro:** Simple, self-contained, runs on edge hardware you have
- **Con:** Doesn't involve Omniverse or digital twins

**Scenario B: Digital Twin + Edge Intelligence**
- Omniverse digital twin of a factory (datacenter, OpenShift)
- Cosmos generates synthetic training data from the digital twin
- Trained model deploys to Jetson edge for real-time inference
- Shows the datacenter-to-edge pipeline
- **Pro:** Shows the full Red Hat stack (OpenShift AI + RHEL image mode)
- **Con:** Complex, needs real 3D assets or convincing sample scene

**Scenario C: Warehouse Robot Fleet (Mega Blueprint)**
- Use the existing Mega Blueprint as a starting point
- Digital twin of a warehouse with autonomous mobile robots
- Cosmos for synthetic sensor data generation
- **Pro:** Pre-built blueprint, aligns with Amazon/Lockheed use cases
- **Con:** Blueprint is still in preview; may need datacenter GPU access

**Scenario D: Siemens-Aligned Manufacturing Demo**
- Align with whatever Siemens announces at GTC
- Position Red Hat as the platform layer under Siemens + NVIDIA
- **Pro:** Business alignment with the Siemens partnership story
- **Con:** Dependent on Siemens announcements and collaboration

### 4.3 Demo Flow Discussion

Meet with Brett Thurber and Kelly Swit to:
1. Present the scenarios above (or updated versions based on GTC announcements)
2. Evaluate which is feasible with available hardware and timeline
3. Define: What does the audience see? What's the narrative? What Red Hat products are shown?
4. Define: What hardware do we need? What do we have? What do we need to acquire?
5. Agree on a target demo date (if there is one)

### 4.4 The Lockheed Martin / Military Drone Angle

Brett mentioned Lockheed Martin as a customer for military drone use cases on AGX hardware.
This is a real customer engagement. The demo could potentially align with this if
appropriate -- but this is Brett's customer relationship to lead. Ask Brett whether the
demo should be customer-aligned or generic.

---

## Delegation Strategy

Itamar was explicit: "have someone else in the loop doing things... not an AI agent,
rather a human." The reason is clear -- AMD fire drills could pull you back at any moment.

### What to Delegate

| Task | Delegatable? | Notes |
|------|-------------|-------|
| GTC keynote watching | Partially | You should watch, but have your delegate also watch and take notes |
| GTC session tracking | Yes | Delegate can monitor session catalog and flag relevant sessions |
| NGC account setup | Yes | Straightforward account creation |
| Cosmos hands-on (workstation) | Yes | Follow the steps in Phase 2.2 |
| Cosmos hands-on (Jetson) | Partially | Needs coordination with Brett for hardware |
| Omniverse exploration | Yes | Follow the steps in Phase 2.3 |
| Blueprint evaluation | Yes | Browse NGC catalog, read documentation |
| RHEL deployment testing | Yes | Follow the steps in Phase 3.1 |
| Demo flow definition | No | Requires your judgment and relationships with Brett/Kelly |
| Status updates | No | You own the communication |
| Architecture recommendation | No | Requires your judgment and understanding of the broader context |

### How to Brief Your Delegate

1. Give them access to this document and the learning material folder
2. Have them read documents 1-4 in the README's recommended order
3. Start them on NGC account setup and Cosmos-Reason2-2B local inference
4. Have them document their findings as they go
5. Daily 15-min sync to share learnings and unblock

### What Your Delegate Should Produce

- Running notes on what they tried, what worked, what didn't
- Screenshots/recordings of models running
- A list of questions that came up during hands-on work
- Hardware resource measurements (GPU memory, inference speed, disk usage)

---

## Status Reporting

### Where to Report

Your work goes into BOTH:
1. **Amy's edge update** -- because this is edge + industrial
2. **Amy's NVIDIA update** -- because this is NVIDIA-specific

Itamar said: "we don't mind sending it twice."

### Format

Itamar's complaint: industrial status is "hidden as three lines at the end" of the edge
updates. He wants status items as clear one-liners at the top, with details below.

**Template for your section:**

```
## Industrial NVIDIA -- Solution/Models Status

| Item | Status | Details |
|------|--------|---------|
| Cosmos ramp-up | [In Progress / Blocked / Done] | [one-line summary] |
| Omniverse ramp-up | [In Progress / Blocked / Done] | [one-line summary] |
| Deployment on RHEL | [Not Started / In Progress / Done] | [one-line summary] |
| Demo flow definition | [Not Started / In Progress / Done] | [one-line summary] |

### Details
[Expand on anything that needs more than one line]
```

### What to Track

Itamar listed these items to include in the status update:
- DGX Spark status (Brett's item, but include for completeness)
- Jetson image mode status (Brett's item)
- Jetson RPM Package Manager (RPM) mode status (Brett's item)
- Your industrial model work (your items above)

---

## Timeline Summary

```
Mar 15 (today)     Read learning material, set up NGC account
    |
Mar 16-19          GTC WEEK
    |               - Watch keynote (Mon Mar 16)
    |               - Monitor sessions
    |               - Track Siemens announcements
    |               - Identify relevant session content to request
    |
Mar 20             GTC summary deliverable
    |               Brief delegate, start them on Cosmos hands-on
    |
Mar 20-28          HANDS-ON RAMP-UP
    |               - Cosmos-Reason on workstation (you + delegate)
    |               - Omniverse exploration on workstation (you or delegate)
    |               - Blueprint evaluation (delegate)
    |               - Coordinate with Brett for Jetson access
    |
Mar 28             Technical assessment deliverable
    |               Share with Itamar, Brett, Kelly
    |
Mar 28 - Apr 7     DEPLOYMENT ARCHITECTURE
    |               - Cosmos on RHEL + Podman (prove it works)
    |               - Cosmos on Jetson with RHEL bootc (with Brett)
    |               - Evaluate RHOAI story
    |
~Apr 1             *** EXPECTED AMD FIRE DRILL ***
    |               Delegate continues if you get pulled
    |
Apr 7+             DEMO STORY
                    - Meet with Brett + Kelly
                    - Define scenario, narrative, hardware needs
                    - Architecture recommendation deliverable
```

---

## Key Resources

### Accounts Needed (all free)

| Account | URL | What For |
|---------|-----|----------|
| NGC (NVIDIA GPU Cloud) | https://ngc.nvidia.com/signin/email | Container images, NIMs, blueprints |
| HuggingFace | https://huggingface.co/join | Model weights download |
| NVIDIA Developer | https://developer.nvidia.com | Omniverse SDK, documentation |

### Key URLs

| Resource | URL |
|----------|-----|
| Cosmos GitHub org | https://github.com/nvidia-cosmos |
| Cosmos Cookbook | https://github.com/nvidia-cosmos/cosmos-cookbook |
| Cosmos on Jetson tutorial | https://huggingface.co/blog/nvidia/cosmos-on-jetson |
| Cosmos-Reason2 repo | https://github.com/nvidia-cosmos/cosmos-reason2 |
| Cosmos NIM quickstart | https://docs.nvidia.com/nim/cosmos/latest/quickstart-guide.html |
| NGC Catalog | https://catalog.ngc.nvidia.com/ |
| Omniverse download | https://www.nvidia.com/en-us/omniverse/download/ |
| Omniverse developer start | https://developer.nvidia.com/omniverse/get-started/ |
| Kit SDK template | https://github.com/NVIDIA-Omniverse/kit-app-template |
| Omniverse Blueprints | https://github.com/NVIDIA-Omniverse-blueprints |
| GPU Operator (OpenShift) | https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/platform-support.html |
| NIM on Podman/RHEL | https://docs.nvidia.com/ai-enterprise/deployment/rhel-with-kvm/latest/podman.html |
| GTC 2026 sessions | https://www.nvidia.com/gtc/session-catalog/ |
| NVIDIA On-Demand | https://www.nvidia.com/en-us/on-demand/ |
| Siemens + NVIDIA | https://www.nvidia.com/en-us/industries/industrial-sector/siemens/ |

### Key People

| Person | Role in This Work | When to Engage |
|--------|------------------|----------------|
| **Brett Thurber** | Hardware enablement, Jetson access, RHEL bootc images | Phase 2 (Jetson access), Phase 3 (deployment), Phase 4 (demo flow) |
| **Kelly Swit** | Demo flow definition | Phase 4 (demo story) |
| **Itamar Heim** | Strategy, priorities, GTC intel (he's there in person) | GTC week (real-time intel), Phase 2 deliverable, Phase 4 (demo approval) |
| **Ohad Anaf Levy** | Status update formatting/distribution | Status reporting setup |
| **Your delegate** | Hands-on execution, continuity | Briefed by Mar 20, active from Mar 20 onward |

### Cosmos Model Quick Reference

| Model | HuggingFace | Size | Runs On |
|-------|-------------|------|---------|
| Cosmos-Reason2-2B | nvidia/cosmos-reason2-2b | ~4GB (FP16) | Desktop GPU, Jetson AGX Orin 64GB, Orin Nano 8GB (quantized) |
| Cosmos-Reason2-2B (quantized) | embedl/Cosmos-Reason2-2B-W4A16-Edge2 | ~1.5GB | Jetson Orin Nano 8GB |
| Cosmos-Reason2-8B | nvidia/cosmos-reason2-8b | ~16GB (FP16) | Desktop GPU 24GB+, Jetson AGX Orin 64GB (quantized) |
| Cosmos-Predict2.5-2B | nvidia/cosmos-predict2.5-2b | ~4GB | Datacenter GPU 24GB+ (x86_64 only) |
| Cosmos-Predict2.5-14B | nvidia/cosmos-predict2.5-14b | ~28GB | Datacenter GPU 80GB+ (x86_64 only) |

### License Summary

| Component | License | Commercial Use |
|-----------|---------|---------------|
| Cosmos source code | Apache 2.0 | Yes |
| Cosmos model weights | NVIDIA Open Model License | Yes (commercially usable, derivative models allowed) |
| Omniverse (individual) | Free for personal/dev use | No (need Enterprise for commercial) |
| Omniverse Enterprise | $4,500/GPU/year | Yes |
| Omniverse Kit SDK | Free | Yes (for building apps) |
| NIM containers | Free (NGC account) | Yes |
