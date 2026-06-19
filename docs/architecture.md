## Subsystem

Astro
│
├── Parser Engine
├── File Dependency Graph Engine
├── Symbol Dependency Graph Engine
├── Unified Dependency Graph Engine
├── Compatibility Analysis Graph Engine
├── Integrity Analysis Engine
└── Report Generator

## Version Scope

This document describes the architecture of Astro V1.

Supported Analysis Layers:

- Syntax & Grammar Errors
- Codebase Integrity Issues
- Environment & Compatibility Issues

Future layers such as Runtime Contract Analysis and Business Logic Analysis are outside the scope of V1.

### Astro Architecture

## Overview

Astro is defined as a multi-layer software intelligence engine that analyzes source code from multiple perspectives, including syntax, structural integrity, runtime contracts, business logic risks and deployment readiness

# High-Level Architecture

Project Source Code 
        |
        ▼
Project Scanner  ───► Filters paths & finds valid files
           │
           ▼
    Parser Engine    ───► Validates Layer 1 Syntax & extracts raw strings
           │
           ▼
    Graph Engine     ───► Resolves strings to absolute paths & links modules
           │
           ▼
 Configuration Analyzer ──► Cross-references Graph keys with requirements.txt
           │
           ▼
  Integrity Analyzer ───► Runs Cycle (DFS) & Dead Code algorithms on the Graph
           │
           ▼
   Report Generator  ───► Flattens all findings into a clean CLI output terminal



## Core Components

# Project Scanner

Responsibilities -

- Discover project files
- filtering unwanted files and directories

Inputs -

- Source Code directory

Output -

- List of files and directories

# Parser Engine

Responsibilities - 

- parse source code
- Generate syntax trees
- extract meaningful symbols and metadata

Input -

- source files

Output -

- AST structures
- Symbol metadata
- Import metadata

# Configuration Analyzer

Responsibilities -

- validate project environment
- check dependency consistency
- detect deployment risks

Inputs -

- requirements.txt
- lockfiles
- project metadata

Outputs - 

- environment warnings

# Graph Engine

Responsibilities -

- Build dependency network
- Track imports and refs
- construct project relationship graph

Inputs -

- AST graph

Outputs ->

- Dependency Graph

# Integrity Analyzer

Responsibilities - 

- Detect circular dependencies
- Detect broken import
- Detect broken codebase integrity

Inputs -

- Dependency Graph

Outputs -

- Integrity findings

# Report Generator 

Responsibilities -

- Aggregate findings
- prioritize risks
- Generate final analysis reports

Outputs -

- Integrity reports
- Compatibility report
- Risk summary

## Design Principle

- Modular Architecture
- Layered verification
- Extensible plugin system
- Environment-aware analysis

## Current Status

This architecture represents the intended design and may evolve as research and implementation progress.


### Graph Engine Architecture


## Layer 1 — File Dependency Graph

### Purpose

Represents relationships between files/modules in the codebase.

### Nodes

* Files
* Modules

### Edges

* `IMPORTS`
* `DEPENDS_ON`

### Example

```
auth_service.py ──imports──► manager.py
```

### Responsibilities

* Dependency tracking
* Impact analysis at file level
* Incremental graph updates
* Circular dependency detection
* Project structure visualization

### Questions Answered

* Which files depend on this file?
* What files will be affected if this file changes?
* Which files import this module?
* Are there circular dependencies?

### Value

Acts as a coarse-grained filtering layer, reducing the search space before deeper semantic analysis.

---

## Layer 2 — Symbol Dependency Graph

### Purpose

Represents relationships between code symbols inside files.

### Nodes

* Functions
* Classes
* Methods
* Global variables
* Constants

### Edges

* `CALLS`
* `INHERITS`
* `USES`
* `RETURNS`
* `ACCESSES`
* `DEFINES`

### Example

```
verify_token ──calls──► find_workspace_root
```

### Responsibilities

* Symbol usage tracking
* Call graph generation
* API breakage analysis
* Dead code detection
* Cross-reference generation

### Questions Answered

* Who calls this function?
* Where is this class used?
* What breaks if this API changes?
* Which functions depend on this symbol?

### Value

Provides semantic understanding of how code components interact.

---

## Layer 3 — Unified Semantic Graph

### Purpose

Combines file-level and symbol-level relationships into a single traversable graph.

### Nodes

* Files
* Modules
* Functions
* Classes
* Methods
* Variables

### Edges

* All Layer 1 edges
* All Layer 2 edges
* Cross-layer ownership edges

### Example

```
auth_service.py
     │
     ▼
verify_token
     │
     ▼
find_workspace_root
     │
     ▼
manager.py
```

### Responsibilities

* End-to-end impact analysis
* Semantic code navigation
* Dependency tracing
* Architectural reasoning
* Intelligent code understanding

### Questions Answered

* If this function changes, what files are affected?
* Why does this file depend on another file?
* What is the complete dependency chain?
* What is the shortest path between two symbols?

### Value

Transforms Astro from a dependency tracker into a semantic code intelligence engine capable of reasoning across the entire codebase.


### Compatibility Analysis Engine (CAE)

Astro CAE is responsible for determining whether a project can run correctly in a environment.

This Engine analyzes project requirements, runtime dependencies, operating system constraints, hardware requirements and external services to identify potential compatibility issues before deployment or execution

## High-Level Architecture

parser Engine json file
          ↓
compatibility Analysis Engine
          ↓
compatibility report

## Core Components

# 1. Requirement Discovery Engine

Extract all project requirements from config files and source metadata.

Inputs:
- requirements.txt
- pyproject.toml
- package.json
- Dockerfile
- docker-compose.yml
- files_metadata.json

Outputs:
- Project Requirements object

Example:

Project Requirements:

Python >= 3.11
FastAPI >= 0.115
PostgreSQL >= 15
Redis >= 7
Linux supported

# 2. Environment Discovery Engine

Collect information about the host machine or target environment

Collected Data:

- Operating System
- OS Version
- CPU Architecture
- Python Version
- Installed Packages
- Available RAM
- GPU Information
- Docker Availability
- Compiler Versions

Outputs:

- Environment Project Object

# 3. Compatibility Rule Engine

Compare Project Requirements against Environment Profile

Responsibilities:

- Version validation
- OS validation
- Architecture validation
- Runtime validation
- Package validation
- Service validation

Outputs:

Compatibility Findings

Example:

Severity: HIGH
Issue:
Project requires Python >= 3.11
Detected Python 3.9

# 4. Report Generator

Purpose:
Generate structured compatibility reports.

Outputs:

Human-readable report
JSON report
Future VS Code diagnostics

Example:

Compatibility Score: 78%

Issues:

Python Version Mismatch
PostgreSQL Version Mismatch

Warnings:

Docker Not Installed

## Compatibility Categories

# Runtime Compatibility

Checks:

Python version
Node version
Java version
Compiler versions

Examples:

Python 3.11 feature used on Python 3.9
C23 project compiled using GCC 8

# Package Compatibility

Checks:

Package version constraints
Framework compatibility

Examples:

FastAPI requiring Pydantic v2
NumPy version conflicts

# Operating System Compatibility

Checks:

OS-specific modules
OS-specific binaries
Path assumptions

Examples:

fcntl on Windows
winreg on Linux

# Hardware Compatibility

Checks:

CPU architecture
GPU requirements
RAM requirements

Examples:

CUDA required but unavailable
ARM system running x86-only binaries

# Service Compatibility

Checks:

Database versions
Redis versions

# External dependencies

Examples:

PostgreSQL 15 required
MySQL version mismatch