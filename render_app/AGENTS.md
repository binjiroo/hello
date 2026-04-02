# AGENTS.md

## Review scope

This project uses Flask with Render deployment.

Always review the following files together when applicable:

- render.yaml
- wsgi.py
- requirements.txt
- Flask app structure (create_app, Blueprints, routes)

---

## Critical priority

Always prioritize in this order:

1. Deployment-breaking issues
2. Runtime errors
3. Structural inconsistencies
4. Improvements

---

## Render configuration checks (render.yaml)

- buildCommand is valid and installs all dependencies
- startCommand correctly points to wsgi entrypoint
- Python version is compatible with dependencies
- Environment variables (envVars) are correctly defined
- PORT binding is correct (0.0.0.0:$PORT)
- No missing or conflicting settings

---

## WSGI checks (wsgi.py)

- Correct import of Flask app
- Entry point matches render.yaml startCommand
- No circular imports
- Application instance name is correct (app)

Example expected pattern:

- app = create_app()

---

## requirements.txt checks

- All required runtime packages are listed
- Flask and gunicorn are included
- Versions are compatible (no obvious conflicts)
- No unnecessary or duplicate packages
- python-dotenv included if used

---

## Flask architecture checks

### Application Factory

- create_app() exists and is used
- No global app misuse
- Config is properly loaded

### Blueprint structure

- Each feature is modularized properly
- Blueprint naming is consistent (xxx_bp)
- No route conflicts
- No duplicated registrations
- Blueprints are properly registered

### Routes

- URL structure is consistent
- No hardcoded paths that break deployment
- No missing return responses

### Project structure consistency

- Directory structure matches intended phase (Phase1 / Phase2)
- No mixed patterns (standalone + blueprint auto-discovery conflict)
- Templates and static paths are correct

---

## Cross-file consistency checks

- render.yaml startCommand matches wsgi.py
- wsgi.py imports match actual app structure
- requirements.txt supports all used modules
- Flask config matches deployment environment

---

## Common failure patterns (detect aggressively)

- Module not found (missing in requirements.txt)
- Incorrect gunicorn target (e.g. wrong module:app)
- Missing create_app usage
- Blueprint not registered
- Wrong working directory assumptions
- Hardcoded local paths
- PORT not bound properly
- Debug mode left enabled in production

---

## Response style

- Keep explanations as short as possible
- Prioritize conclusions and issues first
- Avoid unnecessary background or theory
- Focus only on actionable points
- Do not explain obvious concepts

---

## Output format

1. Critical issues
2. Important improvements
3. Minor notes (optional)
4. Conclusion

Each section must be concise.
If no issues exist, clearly state:
"No critical issues found."