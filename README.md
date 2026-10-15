# Resource Catalog Support Utils: FastAPI Service

This project provides a FastAPI web service that supports resource catalog operations, including generating QLR (QGIS Layer) and LYRX (ArcGIS Layer) files from STAC items and launching parameterized Jupyter notebooks for analysis workflows.

## Features

- **Generate QLR files:** Create QGIS layer files from STAC items with XYZ tile URLs
- **Generate LYRX files:** Create ArcGIS Pro layer files from STAC items with XYZ tile URLs
- **Launch notebooks:** Create and launch parameterized Jupyter notebooks from templates for STAC-based analysis
- **Simplified architecture:** Single generic template for QLR/LYRX generation across all data types
- **Frontend-controlled rendering:** All render parameters handled by the frontend
- **RESTful API:** Simple HTTP endpoints for integration with other applications
- **Template-based approach:** Uses templates for consistent QLR, LYRX, and notebook generation

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (for dependency management)

## Development Setup

1. **Clone the repository** and navigate to the project directory.

2. **Install dependencies:**

   ```bash
   make setup
   ```

3. **Run checks:**

   ```bash
   make check
   ```

4. **Format code:**

   ```bash
   make format
   ```

## Usage

### Start the FastAPI App

```bash
KEYCLOAK_BASE_URL=https://test.eodatahub.org.uk uv run uvicorn app.main:app --reload
```

- `KEYCLOAK_BASE_URL` is required (see [Configuration](#configuration)).

- By default, this will start the API at `http://127.0.0.1:8000`.
- The `app.main:app` syntax tells uvicorn to import the `app` object from the `app.main` module.

### Generate a QLR File

Make a POST request to the `/qlr` endpoint with a JSON payload:

```http
POST http://127.0.0.1:8000/qlr
Content-Type: application/json

{
  "item": {
    "type": "Feature",
    "stac_version": "1.0.0",
    "id": "example-item-id",
    "collection": "sentinel2_ard",
    "bbox": [-180, -90, 180, 90],
    "geometry": {...},
    "properties": {...},
    "links": [...],
    "assets": {...}
  },
  "xyzUrl": "https://titiler.example.com/tiles/{z}/{x}/{y}?url=...&title=...&assets=cog&bidx=3&bidx=2&bidx=1"
}
```

- The `item` field contains the complete STAC item object
- The `xyzUrl` field contains the fully constructed XYZ tile service URL with all render parameters
- This will return a QLR file that you can download and open in QGIS

### Generate a LYRX File

Make a POST request to the `/lyrx` endpoint with the same `item` and `xyzUrl` fields as the `/qlr` payload (see above):

```http
POST http://127.0.0.1:8000/lyrx
Content-Type: application/json

{
  "item": {...},
  "xyzUrl": "https://titiler.example.com/tiles/{z}/{x}/{y}?url=...&title=...&assets=cog&bidx=3&bidx=2&bidx=1"
}
```

- This will return a LYRX file that you can download and open in ArcGIS Pro
- See [`docs/api/lyrx-generation.md`](docs/api/lyrx-generation.md) for full details

### Health Check

```http
GET http://127.0.0.1:8000/health
```

This will return a JSON response with the service status.

## Make Targets

| Target | Description |
|---|---|
| `make setup` | Install dependencies and set up pre-commit hooks |
| `make check` | Run all linting and type checks (ruff, pyright, validate-pyproject) |
| `make format` | Auto-format code with ruff |
| `make test` | Run tests in watch mode |
| `make testonce` | Run tests once |
| `make dockerbuild` | Build Docker image |
| `make dockerpush` | Build and push Docker image to ECR |

## File Structure

- `app/main.py` — FastAPI app entry point
- `app/app_factory.py` — Application factory
- `app/api/` — API routes (health, QLR generation, LYRX generation, notebook launch)
- `app/core/` — Core config and middleware
- `app/create_qlr/` — QLR generation module
  - `create_qlr.py` — Main QLR generation logic
  - `models.py` — Pydantic models for request validation
  - `constants.py` — Configuration constants
  - `templates/` — QLR XML templates
    - `generic_template.xml` — Single template for all data types
- `app/create_lyrx/` — LYRX generation module
  - `create_lyrx.py` — Main LYRX generation logic
  - `models.py` — Pydantic models for request validation
  - `constants.py` — Configuration constants
  - `templates/` — LYRX (CIM JSON) templates
    - `generic_template.lyrx` — Single template for all data types
- `app/api/v1/` — API endpoint modules
  - `qlr.py` — QLR generation endpoints
  - `lyrx.py` — LYRX generation endpoints
  - `notebooks.py` — Notebook launch endpoints
  - `health.py` — Health check endpoints
- `app/services/` — Business logic services

## Notes

- The service generates QLR and LYRX files using a single generic template each, for all data types.
- All render parameters (styling, bands, color formulas, etc.) are handled by the frontend and provided in the `xyzUrl`.
- The service supports CORS for web-based applications.
- All requests are logged with timing information for monitoring and debugging.
- Layer names are extracted from STAC item properties (title, name, or fallback to item ID).
- The backend uses proper URL encoding to ensure QLR files render correctly in QGIS.
- LYRX generation points at the same pre-rendered tile endpoint (rather than the raw raster), reusing the `xyzUrl`'s `{z}`/`{x}`/`{y}` placeholders as-is, so ArcGIS Pro displays titiler's styling instead of computing its own.

## API Endpoints

- `GET /health` — Health check endpoint
- `POST /qlr` — Generate QLR file from STAC item and XYZ URL
- `POST /lyrx` — Generate LYRX file from STAC item and XYZ URL
- `POST /api/v1/notebooks/launch` — Launch a parameterized Jupyter notebook from a template. Needs a platform JWT (`Authorization: Bearer <token>`); `username` must match the token's `preferred_username`, and `workspace_name` must be in its `workspaces`, `workspaces-admin` or `workspaces-owned` claim. Returns 401 for a missing or invalid token, 403 when the user or workspace doesn't match, and 503 if Keycloak's signing keys can't be fetched. `action_name` may contain only letters, digits, `.`, `_` and `-` (at most 64 characters).

## Configuration

| Variable | Purpose |
| --- | --- |
| `KEYCLOAK_BASE_URL` | Platform base URL that serves Keycloak (e.g. `https://eodatahub.org.uk`). Required: the service will not start without it. Tokens must be issued by `<base>/keycloak/realms/<realm>` and are verified against that realm's `/protocol/openid-connect/certs` keys |
| `KEYCLOAK_REALM` | Keycloak realm. Default `eodhp` |
| `NOTEBOOK_S3_BUCKET` | Workspace bucket that notebooks are written to |
| `JUPYTERHUB_BASE_URL` | JupyterHub URL used to build spawn links |

## Deployment

### Docker (ECS/ECR)

The Docker image is built and pushed via the `publish` job in GitHub Actions on push to main.

---
