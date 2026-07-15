# LYRX Generation API Documentation

**Version**: 1.0.0
**Base Path**: `/api/v1` (or `/lyrx` for backward compatibility)
**Last Updated**: 2026-07-14

## Overview

The LYRX Generation API endpoint allows you to create ArcGIS layer (LYRX) files from STAC items with pre-constructed XYZ tile service URLs. LYRX files can be opened directly in ArcGIS Pro to load the same pre-rendered raster tile layer that QGIS users get from the [QLR endpoint](./qlr-generation.md).

### What it does

1. Accepts a complete STAC item object with metadata
2. Takes a fully constructed XYZ tile service URL with render parameters
3. Generates a LYRX (CIM JSON) file using a template-based approach
4. Returns the LYRX file as a downloadable attachment

---

## Endpoint

### Generate LYRX File

**POST** `/api/v1/lyrx` or **POST** `/lyrx`

Generates a LYRX file from a STAC item and XYZ tile service URL.

---

## Request

### Headers

```
Content-Type: application/json
```

### Request Body

Identical shape to the [`/qlr` request body](./qlr-generation.md#request-body) — `item` (STAC item) and `xyzUrl` are both required.

---

## Response

### Success Response (200 OK)

Returns a JSON file with `Content-Type: application/json` and `Content-Disposition` header for file download.

**Response Headers:**
```
Content-Type: application/json
Content-Disposition: attachment; filename="sentinel2-item-001.lyrx"
```

**Response Body:**
The response body is a LYRX (CIM `CIMLayerDocument`) JSON file that can be saved and opened directly in ArcGIS Pro.

**Example LYRX structure:**
```json
{
  "type": "CIMLayerDocument",
  "version": "3.1.0",
  "build": 41833,
  "layers": ["CIMPATH=Map/sentinel2-item-001.json"],
  "layerDefinitions": [
    {
      "type": "CIMTiledServiceLayer",
      "name": "Sentinel-2 Scene",
      "uRI": "CIMPATH=Map/sentinel2-item-001.json",
      "serviceConnection": {
        "type": "CIMStandardServiceConnection",
        "serviceType": "1",
        "url": "https://titiler.example.com/tiles/{z}/{x}/{y}?url=...&bidx=1&bidx=2&bidx=3"
      }
    }
  ]
}
```

#### Response Details

- **Filename**: Generated from the STAC item `id` field (e.g., `{item.id}.lyrx`)
- **Content**: Valid LYRX (CIM) JSON that can be opened in ArcGIS Pro
- **Layer Name**: Extracted from STAC item properties (`title`, `name`, or falls back to `id`)
- **Tile coordinate placeholders**: `xyzUrl`'s `{z}`/`{x}`/`{y}` tokens are embedded as-is — ArcGIS Pro's tiled service layer accepts them verbatim

### Error Responses

Same validation and error behavior as [`/qlr`](./qlr-generation.md#error-response-400-bad-request) for the shared `xyzUrl`/`item` fields.

---

## Notes

### Why a tiled service layer, not a raster dataset

The layer points at the same pre-rendered `xyzUrl` tile endpoint used by `/qlr` (`CIMTiledServiceLayer` / `CIMStandardServiceConnection`), rather than opening the raw COG asset as an ArcGIS raster dataset. This means ArcGIS Pro displays the tiles exactly as titiler renders them (bands, color formula, rescale, etc. all baked in) instead of re-deriving its own default stretch from raw pixel values — matching the QGIS experience rather than ArcGIS's own auto-styling.

### Schema basis

The CIM JSON template is based on ArcGIS Pro's real, verified output for a URL-based tiled layer (`CIMTiledServiceLayer` with a `CIMStandardServiceConnection`), cross-checked against [Esri's public CIM specification](https://github.com/Esri/cim-spec) and multiple real-world `.lyrx` examples. It intentionally omits per-band statistics/histograms and elevation-surface boilerplate that ArcGIS Pro sometimes includes when exporting from a full project/scene — those are computed from actual pixel data or scene state and aren't meaningful for a generated, stateless layer file.

### Template-Based Generation

The API uses a single generic CIM JSON template for all data types, mirroring the QLR service's approach. All render parameters (styling, bands, color formulas, etc.) are handled by the frontend and provided in the `xyzUrl`.
