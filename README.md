# Autonomous Desktop Automation Agent with Resilient Spatial Grounding

[![Python Version](https://img.shields.io/badge/python-3.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Package Manager](https://img.shields.io/badge/managed%20by-uv-purple.svg)](https://github.com/astral-sh/uv)
[![Platform](https://img.shields.io/badge/OS-Windows%2010%20%7C%2011-microsoft.svg)](https://www.microsoft.com/)

An enterprise-grade, zero-shot autonomous desktop automation framework designed to navigate non-deterministic GUI environments without relying on rigid coordinate maps or brittle template images. The system ingests content dynamically via remote data feeds, routes around network pipeline friction, leverages Large Multimodal Models (LMM) for spatial partitioning grounding, and drives desktop native processes with native Win32 kernel safeguards.

---

## 🚀 Key Architectural Strengths

* **Spatial Quad-Partitioning Engine**: Combats image token compression and downsampling degradation by automatically splitting the primary screen into discrete geographic quadrants, preserving high-fidelity visual context and text labels for the vision parser.
* **Resolution-Independent Pipeline**: Translates vision coordinates to relative float percentages (`0.0 - 1.0`), mapping interactions dynamically to the current monitor layout at execution time.
* **Kernel-Level Input Lockout**: Temporarily silences physical hardware inputs via the Windows Win32 API (`BlockInput`) to isolate the environment from human mouse jitter or text stream corruption.
* **Asynchronous Safety Escape Hatch**: Isolates automation runtimes to a background worker thread while keeping a foreground thread hooked (`pynput`) to intercept emergency `Esc` keystrokes, instantly dropping locks and safely purging process clusters.
* **Active Data Failover Cache**: Shields live operations from remote network drops and rate-limiting thresholds by automatically falling back to an integrated high-fidelity local mock data repository.

---

## 📂 Project Architecture

```text
tjm-vision-automation/
├── src/
│   ├── config.py               # Absolute path mapping and environment setups
│   ├── data_controller.py      # Resilient API network management and caching data
│   ├── main.py                 # Multi-threaded pipeline execution loop and hooks
│   ├── os_agent.py             # Focus controls, input blocks, and process tree prunes
│   └── vision_engine.py        # Spatial quadrant segmentation and visual grounding
├── debug_output/               # Target workspace for telemetry and visual audits
├── Design Document.md          # Comprehensive architectural analysis document
├── pyproject.toml              # Modern Python standard project packaging metadata
└── README.md                   # Repository configuration documentation