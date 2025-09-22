# QLR Generator: FastAPI Service for QGIS Layer Files

This project provides a FastAPI web service that generates QLR (QGIS Layer) files from Cloud Optimized GeoTIFF (COG) URLs. QLR files allow you to easily load and visualize geospatial data in QGIS with proper styling and metadata.

## Features

- **Generate QLR files:** Create QGIS layer files from COG URLs using template-based generation
- **Multiple collection support:** Support for different satellite data collections (Sentinel-1, Sentinel-2)
- **Automatic styling:** Apply appropriate styling templates based on the data collection
- **RESTful API:** Simple HTTP endpoints for integration with other applications
- **Template-based approach:** Uses XML templates for consistent QLR generation

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

Make a GET request to the `/qlr` endpoint:

```http
http://127.0.0.1:8000/qlr?url=YOUR_COG_URL&collection=COLLECTION_NAME
```

- Replace `YOUR_COG_URL` with the URL to your Cloud Optimized GeoTIFF file.
- Replace `COLLECTION_NAME` with one of the supported collections: `sentinel2_ard` or `sentinel1_ard`.
- Example:

```http
http://127.0.0.1:8000/qlr?url=https://example.com/sentinel2.tif&collection=sentinel2_ard
```

- This will return a QLR file that you can download and open in QGIS.
- The QLR file will include proper styling and metadata based on the collection type.

### 3. Health Check

Check if the service is running:

```http
http://127.0.0.1:8000/health
```

This will return a JSON response with the service status.

## File Structure

- `main.py` — FastAPI app for QLR generation
- `create_qlr/` — QLR generation module
  - `create_qlr.py` — Main QLR generation logic with template-based approach
  - `get_template.py` — Template selection logic
  - `template_config.json` — Collection to template mapping
  - `templates/` — QLR XML templates
    - `sentinel1_template.xml` — Sentinel-1 styling template
    - `sentinel2_template.xml` — Sentinel-2 styling template
- `requirements.txt` — Project dependencies

## Notes

- The service generates QLR files using XML templates for consistent styling and metadata.
- QLR files are generated with appropriate styling based on the collection type (Sentinel-1 vs Sentinel-2).
- The service supports CORS for web-based applications.
- All requests are logged with timing information for monitoring and debugging.
- Layer IDs are automatically extracted from URLs, with support for both `/items/` URL patterns and fallback extraction.

## API Endpoints

- `GET /health` — Health check endpoint
- `GET /qlr?url=<cog_url>&collection=<collection_name>` — Generate QLR file

## Supported Collections

- `sentinel2_ard` — Sentinel-2 Analysis Ready Data
- `sentinel1_ard` — Sentinel-1 Analysis Ready Data

## Troubleshooting

- If you get a 400 error, check that the COG URL is accessible and the collection name is valid.
- If you see errors about missing dependencies, double-check your Python environment and install all required packages.
- Check the logs for detailed error messages about template generation or URL processing.
- Ensure the template files exist in the `create_qlr/templates/` directory for your collection type.

---
