# Notebook Launch API Documentation

**Version**: 1.0.0  
**Base Path**: `/api/v1`  
**Last Updated**: 2026-02-10

## Overview

The Notebook Launch API endpoint allows you to create parameterized Jupyter notebooks from templates, upload them to S3, and receive a JupyterHub spawn URL that users can open directly in their browser.

### What it does

1. Fetches a notebook template from a provided URL
2. Replaces placeholders (e.g., `{{KEY}}`) with values from the optional `variables` map
3. Uploads the parameterized notebook to S3
4. Returns a JupyterHub spawn URL that opens the notebook automatically

---

## Endpoint

### Launch Notebook

**POST** `/api/v1/notebooks/launch`

Creates a parameterized notebook and returns spawn details.

---

## Request

### Headers

```
Content-Type: application/json
```

### Request Body

All fields except `variables` are **required**.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `workspace_name` | `string` | Workspace identifier where the notebook will be created | `"sparkgeotest"` |
| `username` | `string` | JupyterHub username (must match authenticated user) | `"geodowd"` |
| `action_name` | `string` | Logical name of the analysis action/template (used in servername) | `"ndvi"` |
| `template_url` | `string` (URL) | HTTP(S) URL to the notebook template file | `"https://example.com/templates/ndvi_template.ipynb"` |
| `variables` | `object` (optional) | Key-value map for template placeholder substitution. Each key `K` is replaced as `{{K}}` in the notebook. | `{"STAC_COLLECTION_NAME": "sentinel-s2-l2a", "STAC_ITEM_LINK": "https://..."}` |

### Example Request

**Basic request (no variables):**
```json
{
  "workspace_name": "sparkgeotest",
  "username": "geodowd",
  "action_name": "ndvi",
  "template_url": "https://example.com/templates/ndvi_template.ipynb"
}
```

**Request with variables:**
```json
{
  "workspace_name": "sparkgeotest",
  "username": "geodowd",
  "action_name": "ndvi",
  "template_url": "https://example.com/templates/ndvi_template.ipynb",
  "variables": {
    "STAC_COLLECTION_NAME": "sentinel-s2-l2a",
    "STAC_ITEM_LINK": "https://example.com/stac/collections/sentinel-s2-l2a/items/123",
    "AOI": "{\"type\":\"Polygon\",\"coordinates\":[[[-122.5,37.7],[-122.4,37.7],[-122.4,37.8],[-122.5,37.8],[-122.5,37.7]]]}"
  }
}
```

---

## Response

### Success Response (200 OK)

```json
{
  "servername": "ndvi_a1b2c3d4e5f6",
  "notebook_path": "jupyter/ndvi_a1b2c3d4e5f6.ipynb",
  "spawn_url": "https://eodatahub-workspaces.org.uk/notebooks/hub/spawn/geodowd/ndvi_a1b2c3d4e5f6?workspace=sparkgeotest&next=https://eodatahub-workspaces.org.uk/notebooks/user/geodowd/ndvi_a1b2c3d4e5f6/lab/tree/s3/jupyter/ndvi_a1b2c3d4e5f6.ipynb"
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `servername` | `string` | Unique server name generated as `<action_name>_<uuid>`. Used by JupyterHub to identify the notebook server. |
| `notebook_path` | `string` | Relative S3 path where the notebook is stored (e.g., `jupyter/ndvi_abc123.ipynb`) |
| `spawn_url` | `string` (URL) | Complete JupyterHub URL that spawns the server and opens the notebook. **Use this URL to redirect users.** |

### Error Response (400 Bad Request / 500 Internal Server Error)

```json
{
  "error": "Template notebook could not be fetched",
  "code": "TEMPLATE_FETCH_FAILED"
}
```

#### Error Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `error` | `string` | Human-readable error message |
| `code` | `string` | Machine-readable error code (see Error Codes below) |

---

## Error Codes

| HTTP Status | Error Code | Description | When it occurs |
|-------------|------------|-------------|----------------|
| `400` | `TEMPLATE_FETCH_FAILED` | Template URL is unreachable or returns non-200 status | Template URL is invalid, network error, or server returns error |
| `400` | `TEMPLATE_PARSE_FAILED` | Template is not valid notebook JSON | Template file exists but is malformed |
| `400` | `VALIDATION_ERROR` | Request validation failed | Missing required fields, invalid URL format, or invalid data types |
| `500` | `NOTEBOOK_UPLOAD_FAILED` | Failed to upload notebook to S3 | S3 permissions issue, bucket misconfiguration, or network error |
| `500` | `INTERNAL_ERROR` | Unexpected server error | Unhandled exception (should be rare) |

---

## Usage Flow

### 1. User initiates notebook launch

User selects a STAC item and chooses an analysis action (e.g., "NDVI analysis").

### 2. Frontend calls the API

```typescript
const response = await launchNotebook(apiBaseUrl, {
  workspace_name: currentWorkspace,
  username: currentUser.username,
  action_name: selectedAction,
  template_url: actionTemplateUrl,
  variables: {
    STAC_COLLECTION_NAME: selectedCollection,
    STAC_ITEM_LINK: selectedItemLink,
    ...(selectedAOI && { AOI: JSON.stringify(selectedAOI) }),
  },
});
```

### 3. Handle response

**On Success:**

```typescript
// Option 1: Redirect user to JupyterHub
window.location.href = response.spawn_url;

// Option 2: Open in new tab/window
window.open(response.spawn_url, '_blank');

// Option 3: Store for later use
localStorage.setItem('notebook_spawn_url', response.spawn_url);
// Show success message with option to open
showNotification(`Notebook created: ${response.servername}`, {
  action: () => window.open(response.spawn_url),
});
```

**On Error:**

```typescript
try {
  const result = await launchNotebook(...);
  // Handle success
} catch (error) {
  // Display user-friendly error message
  const errorMessage = getErrorMessage(error.code);
  showErrorNotification(errorMessage);
  
  // Log for debugging
  console.error('Notebook launch failed:', error);
}
```

## Testing

### cURL Example

**Without variables:**
```bash
curl -X POST "https://api.example.com/api/v1/notebooks/launch" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "workspace_name": "sparkgeotest",
    "username": "geodowd",
    "action_name": "ndvi",
    "template_url": "https://example.com/templates/ndvi_template.ipynb"
  }'
```

**With variables:**
```bash
curl -X POST "https://api.example.com/api/v1/notebooks/launch" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "workspace_name": "sparkgeotest",
    "username": "geodowd",
    "action_name": "ndvi",
    "template_url": "https://example.com/templates/ndvi_template.ipynb",
    "variables": {
      "STAC_COLLECTION_NAME": "sentinel-s2-l2a",
      "STAC_ITEM_LINK": "https://example.com/stac/collections/sentinel-s2-l2a/items/123"
    }
  }'
```

### Expected Success Response

```json
{
  "servername": "ndvi_a1b2c3d4e5f6",
  "notebook_path": "jupyter/ndvi_a1b2c3d4e5f6.ipynb",
  "spawn_url": "https://eodatahub-workspaces.org.uk/notebooks/hub/spawn/geodowd/ndvi_a1b2c3d4e5f6?workspace=sparkgeotest&next=https://eodatahub-workspaces.org.uk/notebooks/user/geodowd/ndvi_a1b2c3d4e5f6/lab/tree/s3/jupyter/ndvi_a1b2c3d4e5f6.ipynb"
}
```