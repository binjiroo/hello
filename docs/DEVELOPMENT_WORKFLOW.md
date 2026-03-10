# AI Development Workflow

This project uses an AI-driven development workflow.

AI roles are separated into design and implementation.

ChatGPT is responsible for architecture and task design.

Codex is responsible for code generation and optimization.

---

# Development Flow

ChatGPT
↓
Architecture / Task Design

Codex
↓
Code Implementation

Git
↓
Version Control

Project Memory
↓
Development History

---

# Step 1: Understand Project Context

Before starting any task, the AI must read:

ai/context/AI_CONTEXT.md

This file explains:

- project purpose
- framework
- deployment
- current phase

---

# Step 2: Check Project Memory

AI must read:

ai/context/PROJECT_MEMORY.md

This file contains:

- development history
- previous decisions
- past tasks

---

# Step 3: Identify Current Task

Check:

ai/prompts/codex_tasks/

Tasks are numbered:

task_001
task_002
task_003

Each task describes:

- purpose
- requirements
- files to create
- expected behavior

---

# Step 4: Generate Code

Codex reads the task file and generates code.

Generated code must follow:

docs/PROJECT_RULES.md

---

# Step 5: Update Project Memory

After completing a task, update:

ai/context/PROJECT_MEMORY.md

Record:

- task completed
- files created
- architecture decisions

---

# Step 6: Prepare Next Task

ChatGPT designs the next task.

Create new task file:

ai/prompts/codex_tasks/task_XXX.md

---

# Development Phases

Phase 0
AI Development Infrastructure

Phase 1
Flask Application Core

Phase 2
Template System

Phase 3
Static Assets

Phase 4
Database Integration

Phase 5
Authentication

Phase 6
API

Phase 7
SaaS Architecture

---

# AI Development Principles

1. Separate design and implementation.

2. Store AI context and memory.

3. Use structured task files.

4. Maintain project history.

5. Keep architecture consistent.