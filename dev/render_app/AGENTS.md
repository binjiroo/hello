# AGENTS.md

## Review scope

This project is in the Render public test preparation phase.

Always review these together when applicable:

- render.yaml
- wsgi.py
- requirements.txt
- app/__init__.py
- app/blueprint or app/blueprints route packages

---

## Critical priority

Always prioritize in this order:

1. Deployment-breaking issues
2. Runtime errors
3. Phase2 structure mismatches
4. Improvements

---

## Phase2 structure rules

- App entrypoint must remain `wsgi:app`
- `wsgi.py` must expose `app = create_app()`
- Blueprint integration must be centralized in `create_app()`
- Screen Blueprint names use `unique_name`
- API Blueprint names use `unique_name_api`
- Screen Blueprint URL prefixes use `/cad/unique_name`
- API Blueprint URL prefixes use `/api/unique_name`
- Each Blueprint folder must contain `__init__.py`
- Static JS paths should follow `/static/js/cad/sections/unique_name/main.js`
- Health check endpoint must be `/health`

---

## Render configuration checks

- `buildCommand` installs runtime dependencies
- `startCommand` matches the WSGI entrypoint
- Python version is compatible with dependencies
- `PORT` binding uses `0.0.0.0:$PORT`
- Health check path is configured when needed
- No local-only path assumptions exist

---

## Flask architecture checks

- `create_app()` exists and owns Blueprint registration
- No direct `Flask(__name__)` app instance is created outside the factory
- Blueprint auto-discovery and manual registration are not mixed incorrectly
- Logging is initialized with `logging.getLogger(__name__)`
- `404` handler exists
- Route endpoints follow `unique_name.index` style

---

## Common failure patterns

- Module not found from Blueprint package path drift
- Wrong gunicorn target
- Missing `__init__.py` in Blueprint folders
- URL prefixes not aligned with `/cad/...` or `/api/...`
- Health check missing
- Debug-only behavior left in Render config

---

## Response style

- Keep explanations short
- List findings before improvements
- Focus on actionable issues only

---

## Output format

1. Critical issues
2. Important improvements
3. Minor notes
4. Conclusion
