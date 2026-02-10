# QLR Generator: FastAPI Service for QGIS Layer Files

This project provides a FastAPI web service that generates QLR (QGIS Layer) files from STAC items with pre-constructed XYZ tile service URLs. QLR files allow you to easily load and visualize geospatial data in QGIS with proper styling and metadata.

## Features

- **Generate QLR files:** Create QGIS layer files from STAC items with XYZ tile URLs
- **Simplified architecture:** Single generic template for all data types
- **Frontend-controlled rendering:** All render parameters handled by the frontend
- **RESTful API:** Simple HTTP endpoints for integration with other applications
- **Template-based approach:** Uses a single XML template for consistent QLR generation

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
uv run uvicorn app.main:app --reload
```

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
  "xyzUrl": "https://titiler.example.com/tiles/{z}/{x}/{y}?url=...&title=...&assets=cog&bidx=3&bidx=2&bidx=1",
  "renderId": "Natural Color"
}
```

- The `item` field contains the complete STAC item object
- The `xyzUrl` field contains the fully constructed XYZ tile service URL with all render parameters
- The `renderId` field identifies the render configuration being used
- This will return a QLR file that you can download and open in QGIS

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
- `app/api/` — API routes (health, QLR generation)
- `app/core/` — Core config and middleware
- `app/create_qlr/` — QLR generation module
  - `create_qlr.py` — Main QLR generation logic
  - `models.py` — Pydantic models for request validation
  - `constants.py` — Configuration constants
  - `templates/` — QLR XML templates
- `app/services/` — Business logic services
- `lambda_handler.py` — AWS Lambda handler (Mangum wrapper)
- `template.yaml` — SAM template for Lambda deployment

## API Endpoints

- `GET /health` — Health check endpoint
- `POST /qlr` — Generate QLR file from STAC item and XYZ URL

## Deployment

### Docker (ECS/ECR)

The Docker image is built and pushed via the `publish` job in GitHub Actions on push to main.

### AWS Lambda

The Lambda deployment uses AWS SAM and is triggered via the `publish-to-lambda` workflow on push to `main` or `develop` branches.

---
