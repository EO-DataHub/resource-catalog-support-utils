# QLR Generation API Documentation

**Version**: 1.0.0  
**Base Path**: `/api/v1` (or `/qlr` for backward compatibility)  
**Last Updated**: 2026-02-16

## Overview

The QLR Generation API endpoint allows you to create QGIS Layer (QLR) files from STAC items with pre-constructed XYZ tile service URLs. QLR files can be opened directly in QGIS to load and visualize geospatial data layers with proper styling and metadata.

### What it does

1. Accepts a complete STAC item object with metadata
2. Takes a fully constructed XYZ tile service URL with render parameters
3. Generates a QLR XML file using a template-based approach
4. Returns the QLR file as a downloadable attachment

---

## Endpoint

### Generate QLR File

**POST** `/api/v1/qlr` or **POST** `/qlr`

Generates a QLR file from a STAC item and XYZ tile service URL.

---

## Request

### Headers

```
Content-Type: application/json
```

### Request Body

All fields are **required**.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `item` | `object` (STAC Item) | Complete STAC item object containing metadata, geometry, assets, and links. Must conform to STAC specification. | See example below |
| `xyzUrl` | `string` (URL) | Fully constructed XYZ tile service URL with all render parameters. Must include `{z}`, `{x}`, and `{y}` placeholders for tile coordinates. | `"https://titiler.example.com/tiles/{z}/{x}/{y}?url=https://example.com/data.tif&bidx=1&bidx=2&bidx=3&resampling=bilinear"` |

### STAC Item Structure

The `item` field must be a valid STAC Item object with the following required fields:

| Field | Type | Description |
|-------|------|-------------|
| `type` | `string` | Must be `"Feature"` |
| `stac_version` | `string` | STAC specification version (e.g., `"1.0.0"`) |
| `id` | `string` | Unique identifier for the item within the collection |
| `collection` | `string` | Collection this item belongs to |
| `bbox` | `array[number]` | Bounding box `[minLon, minLat, maxLon, maxLat]` in WGS84 |
| `geometry` | `object` | GeoJSON geometry object (Point, Polygon, etc.) |
| `properties` | `object` | Item properties/metadata (must include `datetime`) |
| `links` | `array[object]` | Array of related links |
| `assets` | `object` | Dictionary of assets (data files, thumbnails, etc.) |

### Example Request

**Basic request:**
```json
{
  "item": {
    "type": "Feature",
    "stac_version": "1.0.0",
    "id": "sentinel2-item-001",
    "collection": "sentinel2_ard",
    "bbox": [-122.5, 37.7, -122.4, 37.8],
    "geometry": {
      "type": "Polygon",
      "coordinates": [[
        [-122.5, 37.7],
        [-122.4, 37.7],
        [-122.4, 37.8],
        [-122.5, 37.8],
        [-122.5, 37.7]
      ]]
    },
    "properties": {
      "datetime": "2023-01-01T00:00:00Z",
      "title": "Sentinel-2 Scene",
      "description": "Sentinel-2 L2A product"
    },
    "links": [
      {
        "rel": "self",
        "href": "https://example.com/stac/collections/sentinel2_ard/items/sentinel2-item-001",
        "type": "application/geo+json"
      }
    ],
    "assets": {
      "visual": {
        "href": "https://example.com/data/sentinel2-item-001.tif",
        "type": "image/tiff",
        "roles": ["data"]
      }
    }
  },
  "xyzUrl": "https://titiler.example.com/tiles/{z}/{x}/{y}?url=https://example.com/data/sentinel2-item-001.tif&bidx=1&bidx=2&bidx=3&resampling=bilinear"
}
```

**Request with custom render parameters:**
```json
{
  "item": {
    "type": "Feature",
    "stac_version": "1.0.0",
    "id": "landsat-item-002",
    "collection": "landsat-c2-l2",
    "bbox": [-122.5, 37.7, -122.4, 37.8],
    "geometry": {
      "type": "Polygon",
      "coordinates": [[
        [-122.5, 37.7],
        [-122.4, 37.7],
        [-122.4, 37.8],
        [-122.5, 37.8],
        [-122.5, 37.7]
      ]]
    },
    "properties": {
      "datetime": "2023-06-15T10:30:00Z",
      "title": "Landsat 8 Scene"
    },
    "links": [],
    "assets": {}
  },
  "xyzUrl": "https://titiler.example.com/tiles/{z}/{x}/{y}?url=https://example.com/data/landsat.tif&bidx=4&bidx=3&bidx=2&colormap_name=viridis&rescale=0,10000"
}
```

---

## Response

### Success Response (200 OK)

Returns an XML file with `Content-Type: application/xml` and `Content-Disposition` header for file download.

**Response Headers:**
```
Content-Type: application/xml
Content-Disposition: attachment; filename="sentinel2-item-001.qlr"
```

**Response Body:**
The response body is a QLR XML file that can be saved and opened directly in QGIS.

**Example QLR XML structure:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE qgis-layer-definition>
<qlr>
  <layer-tree-group expanded="1" groupLayer="" name="" checked="Qt::Checked">
    <layer-tree-layer expanded="1" legend_split_behavior="0" 
                      source="http-header:referer=&amp;type=xyz&amp;url=https://titiler.example.com/tiles/{z}/{x}/{y}?url=..." 
                      id="sentinel2-item-001" name="Sentinel-2 Scene" providerKey="wms" 
                      checked="Qt::Checked">
    </layer-tree-layer>
  </layer-tree-group>
</qlr>
```

#### Response Details

- **Filename**: Generated from the STAC item `id` field (e.g., `{item.id}.qlr`)
- **Content**: Valid QLR XML that can be opened in QGIS
- **Layer Name**: Extracted from STAC item properties (`title`, `name`, or falls back to `id`)

### Error Response (400 Bad Request)

```json
{
  "detail": "xyzUrl must contain {z}, {x}, and {y} placeholders for tile coordinates"
}
```

**Common validation errors:**

| Error Message | Cause |
|--------------|-------|
| `"xyzUrl cannot be empty"` | `xyzUrl` field is missing or empty |
| `"xyzUrl must be a valid HTTP/HTTPS URL"` | URL doesn't start with `http://` or `https://` |
| `"xyzUrl must contain {z}, {x}, and {y} placeholders for tile coordinates"` | URL missing required tile coordinate placeholders |
| `"STAC item is required"` | `item` field is missing |
| `"STAC item validation failed: ..."` | STAC item doesn't conform to specification |

### Error Response (500 Internal Server Error)

```json
{
  "detail": "Internal server error"
}
```

Occurs when there's an unexpected server error during QLR generation (e.g., template loading failure, XML generation error).

---

## Usage Flow

### 1. User selects STAC item and render configuration

User selects a STAC item from a catalog and chooses a render configuration (e.g., "Natural Color", "NDVI").

### 2. Frontend constructs XYZ tile URL

The frontend constructs a fully parameterized XYZ tile URL with all render parameters:

```typescript
const xyzUrl = buildTileUrl(stacItem, renderConfig);
// Example: "https://titiler.example.com/tiles/{z}/{x}/{y}?url=...&bidx=1&bidx=2&bidx=3"
```

### 3. Frontend calls the API

```typescript
const response = await fetch(`${apiBaseUrl}/api/v1/qlr`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    item: stacItem,
    xyzUrl: xyzUrl,
  }),
});

if (!response.ok) {
  const error = await response.json();
  throw new Error(error.detail);
}
```

### 4. Handle response

**On Success:**

```typescript
// Get the QLR file as a blob
const blob = await response.blob();

// Create download link
const url = window.URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;

// Extract filename from Content-Disposition header
const contentDisposition = response.headers.get('Content-Disposition');
const filenameMatch = contentDisposition?.match(/filename="(.+)"/);
const filename = filenameMatch ? filenameMatch[1] : 'layer.qlr';
a.download = filename;

// Trigger download
document.body.appendChild(a);
a.click();
document.body.removeChild(a);
window.URL.revokeObjectURL(url);

// Show success message
showNotification(`QLR file downloaded: ${filename}`);
```

**On Error:**

```typescript
try {
  const response = await generateQLR(...);
  // Handle success
} catch (error) {
  // Display user-friendly error message
  const errorMessage = getErrorMessage(error.detail);
  showErrorNotification(errorMessage);
  
  // Log for debugging
  console.error('QLR generation failed:', error);
}
```

---

## Testing

### cURL Example

```bash
curl -X POST "https://api.example.com/api/v1/qlr" \
  -H "Content-Type: application/json" \
  -o "output.qlr" \
  -d '{
    "item": {
      "type": "Feature",
      "stac_version": "1.0.0",
      "id": "sentinel2-item-001",
      "collection": "sentinel2_ard",
      "bbox": [-122.5, 37.7, -122.4, 37.8],
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-122.5, 37.7],
          [-122.4, 37.7],
          [-122.4, 37.8],
          [-122.5, 37.8],
          [-122.5, 37.7]
        ]]
      },
      "properties": {
        "datetime": "2023-01-01T00:00:00Z"
      },
      "links": [],
      "assets": {}
    },
    "xyzUrl": "https://titiler.example.com/tiles/{z}/{x}/{y}?url=https://example.com/data.tif&bidx=1&bidx=2&bidx=3"
  }'
```

### Expected Success Response

The response will be an XML file that can be saved and opened in QGIS:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE qgis-layer-definition>
<qlr>
  <layer-tree-group expanded="1" groupLayer="" name="" checked="Qt::Checked">
    <layer-tree-layer expanded="1" legend_split_behavior="0" 
                      source="http-header:referer=&amp;type=xyz&amp;url=https://titiler.example.com/tiles/{z}/{x}/{y}?url=..." 
                      id="sentinel2-item-001" name="sentinel2-item-001" providerKey="wms" 
                      checked="Qt::Checked">
    </layer-tree-layer>
  </layer-tree-group>
</qlr>
```

---

## Notes

### XYZ URL Requirements

- Must include `{z}`, `{x}`, and `{y}` placeholders for tile coordinates
- Must be a valid HTTP/HTTPS URL
- Should include all render parameters (band indices, color formulas, etc.) as query parameters
- The frontend is responsible for constructing the complete URL with all render parameters

### STAC Item Requirements

- Must conform to STAC specification (version 1.0.0 or later)
- Must include all required fields (`type`, `stac_version`, `id`, `collection`, `bbox`, `geometry`, `properties`, `links`, `assets`)
- The `properties.datetime` field is required
- Layer name in QLR file is extracted from `properties.title`, `properties.name`, or falls back to `item.id`

### QLR File Usage

1. Download the QLR file from the API response
2. Open QGIS
3. Drag and drop the QLR file into QGIS, or use `Layer > Add Layer > Add from Layer Definition File`
4. The layer will load with the XYZ tile service and render according to the parameters in the URL

### Template-Based Generation

The API uses a single generic XML template for all data types. All render parameters (styling, bands, color formulas, etc.) are handled by the frontend and provided in the `xyzUrl`. This approach ensures consistency and simplifies maintenance.

---

## Error Codes

| HTTP Status | Error Detail | Description | When it occurs |
|-------------|--------------|-------------|----------------|
| `400` | `"xyzUrl cannot be empty"` | `xyzUrl` field is missing or empty | Request body missing `xyzUrl` or empty string |
| `400` | `"xyzUrl must be a valid HTTP/HTTPS URL"` | URL doesn't start with `http://` or `https://` | Invalid URL format |
| `400` | `"xyzUrl must contain {z}, {x}, and {y} placeholders for tile coordinates"` | URL missing required tile coordinate placeholders | URL doesn't include `{z}`, `{x}`, `{y}` |
| `400` | `"STAC item is required"` | `item` field is missing | Request body missing `item` |
| `400` | `"STAC item validation failed: ..."` | STAC item doesn't conform to specification | Missing required STAC fields or invalid structure |
| `500` | `"Internal server error"` | Unexpected server error | Template loading failure, XML generation error, or unhandled exception |
