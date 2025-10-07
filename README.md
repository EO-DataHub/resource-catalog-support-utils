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
- [Uvicorn](https://www.uvicorn.org/) (for running FastAPI)
- All dependencies in `requirements.txt` (install with your preferred tool, e.g. `pip`, `uv`, or `poetry`)

## Installation

1. **Clone the repository** and navigate to the project directory.

2. **Install dependencies** (using pip as an example):

   ```bash
   pip install -r requirements.txt
   ```

   Or, to use the exact versions in `requirements.txt`:

   ```bash
   pip install fastapi>=0.115.14 uvicorn>=0.35.0 pydantic>=2.0.0 requests>=2.31.0
   ```

## Usage

### 1. Start the FastAPI App

Run the FastAPI app using Uvicorn:

```bash
uvicorn main:app --reload
```

- By default, this will start the API at `http://127.0.0.1:8000`.

### 2. Generate a QLR File

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

### 3. Health Check

Check if the service is running:

```http
http://127.0.0.1:8000/health
```

This will return a JSON response with the service status.

## File Structure

- `main.py` — FastAPI app for QLR generation
- `create_qlr/` — QLR generation module
  - `create_qlr.py` — Main QLR generation logic with simplified approach
  - `models.py` — Pydantic models for request validation
  - `constants.py` — Error messages and configuration constants
  - `templates/` — QLR XML templates
    - `generic_template.xml` — Single template for all data types
- `requirements.txt` — Project dependencies

## Notes

- The service generates QLR files using a single generic XML template for all data types.
- All render parameters (styling, bands, color formulas, etc.) are handled by the frontend and provided in the `xyzUrl`.
- The service supports CORS for web-based applications.
- All requests are logged with timing information for monitoring and debugging.
- Layer names are extracted from STAC item properties (title, name, or fallback to item ID).
- The backend uses proper URL encoding to ensure QLR files render correctly in QGIS.

## API Endpoints

- `GET /health` — Health check endpoint
- `POST /qlr` — Generate QLR file from STAC item and XYZ URL

## Request Format

The `/qlr` endpoint expects a JSON payload with:

- `item`: Complete STAC item object
- `xyzUrl`: Fully constructed XYZ tile service URL with render parameters
- `renderId`: Identifier for the render configuration

## Troubleshooting

- If you get a 400 error, check that the STAC item is valid and the `xyzUrl` contains proper `{z}`, `{x}`, `{y}` placeholders.
- If you see errors about missing dependencies, double-check your Python environment and install all required packages.
- Check the logs for detailed error messages about template generation or URL processing.
- Ensure the `generic_template.xml` file exists in the `create_qlr/templates/` directory.
- If QLR files don't render in QGIS, verify that the `xyzUrl` is properly URL-encoded and accessible.

---
