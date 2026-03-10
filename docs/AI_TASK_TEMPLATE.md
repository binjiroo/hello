# AI Task Template

This file defines the task format used for AI-assisted development.

Tasks are designed by ChatGPT and executed by Codex.

---

# Task Information

Task ID:
task_XXX

Task Name:
Short descriptive title

Phase:
Development phase (see AI_PHASE_PLAN.md)

---

# Objective

Describe the purpose of the task.

Explain what functionality should be implemented.

---

# Context

Relevant project context.

Framework:
Flask

Architecture:
Application Factory
Blueprint routing

Deployment:
Render

Python version:
3.12

---

# Requirements

List the functional requirements.

Example:

- Use Flask Application Factory pattern
- Use Blueprint for routing
- Configuration must be handled in config.py
- Code must follow project rules

Reference:

docs/PROJECT_RULES.md

---

# Files to Create

List new files.

Example:

app/
├ __init__.py
├ routes.py
└ config.py

---

# Files to Modify

List existing files that must be modified.

Example:

run.py

---

# Implementation Details

Explain the implementation logic.

Example:

create_app() function should initialize Flask app.

Blueprint must be registered inside create_app().

Routes should be defined inside routes.py.

---

# Expected Behavior

Describe the final behavior.

Example:

Accessing "/" should display:

Hello App

---

# Output Format

Codex must output:

1. File structure
2. Full code for each file
3. Explanation (optional)

---

# Constraints

Important constraints for Codex.

Example:

- Do not modify unrelated files
- Keep code minimal
- Follow Flask best practices
- Avoid unnecessary dependencies

---

# Acceptance Criteria

Task is complete when:

- Flask app runs successfully
- "/" route works
- Code structure matches specification