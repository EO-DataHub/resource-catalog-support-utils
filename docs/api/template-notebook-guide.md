# Template Notebook Guide

This guide explains how to create a Jupyter notebook template that works with the Earth Observation Data Hub (EODH) notebook launch service. The service fetches templates via HTTP, injects runtime variables, and launches them in JupyterHub for workspace users.

Documentation for the workflow catalogue and hosting requirements is available at [the workflow catalogue guide](https://github.com/EO-DataHub/workflow-catalogue/blob/main/docs/guides/adding-records.md).

## How the Template System Works

When a launch request is sent:

1. The backend downloads your `.ipynb` file from `template_url`.
2. It replaces placeholders in notebook cell source text.
3. The parameterized notebook is uploaded to S3 at:
   - `<workspace_name>/jupyter/<action_name>_<uuid>.ipynb`

Placeholder format:

- `{{KEY}}`
- If request `variables` contains `"KEY": "value"`, the notebook text `{{KEY}}` becomes `value`.
- Missing variables are left unchanged.

## How Variable Keys Are Unique

The `variables` object is a key/value map, so each key can only appear once per request payload.

For this integration, the frontend resolves these keys from unique sources:

- `STAC_COLLECTION_NAME`
  - Source: selected STAC item's `collection` field.
  - Meaning: collection identifier for the selected item.
- `STAC_ITEM_LINK`
  - Source: selected STAC item's `rel="self"` link.
  - Meaning: canonical link to the specific STAC item.
- `AOI`
  - Source: current map AOI (only when AOI exists and the user has enabled include AOI).
  - Meaning: stringified GeoJSON Feature (`JSON.stringify(aoi)`).

Important matching rules:

- Key names are case-sensitive and must match exactly between notebook placeholder and request `variables`.
- Only keys that exist in notebook `inputParameters` are auto-resolved and sent by the current frontend flow.
- `AOI` is optional; if omitted, `{{AOI}}` remains in the notebook unchanged.

## Step 1: Create the Notebook

Create a notebook in JupyterLab with your analysis flow (imports, setup, processing, plots, exports).

Use placeholders anywhere in markdown or code cell source where runtime values should be injected.

Example placeholders used by this project:

- `{{STAC_COLLECTION_NAME}}`
- `{{STAC_ITEM_LINK}}`
- `{{AOI}}`

## Step 2: Add a Parameters Cell

Add a top cell that collects and validates injected values.

```python
import json

STAC_COLLECTION_NAME = "{{STAC_COLLECTION_NAME}}"
STAC_ITEM_LINK = "{{STAC_ITEM_LINK}}"
AOI_RAW = "{{AOI}}"

print("Collection:", STAC_COLLECTION_NAME)
print("Item URL:", STAC_ITEM_LINK)

aoi_geometry = None
if AOI_RAW and AOI_RAW != "{{AOI}}":
    try:
        aoi_geometry = json.loads(AOI_RAW)
        print("AOI loaded")
    except json.JSONDecodeError:
        print("AOI is not JSON; using raw string")
        aoi_geometry = AOI_RAW
```

Why this pattern matters:

- It works when `AOI` is omitted (placeholder remains `{{AOI}}`).
- It avoids crashes if `AOI` is plain text instead of JSON.

## Step 3: Keep the Notebook Launch-Friendly

- Do not hardcode environment-specific local paths.
- Prefer relative/output-safe paths inside notebook workspace folders.
- Keep long-running cells optional or clearly labeled.
- Add short markdown sections so users know what to run first.

## Step 4: Save and Host the Template

Your template must be reachable by the API over HTTP(S). See the EODH API documentation (linked above) for hosting requirements and supported options for `template_url`.

## Step 5: Test with the Launch Endpoint

Example request:

```json
{
  "workspace_name": "sparkgeotest",
  "username": "geodowd",
  "action_name": "ndvi",
  "template_url": "https://raw.githubusercontent.com/<org>/<repo>/main/ndvi.ipynb",
  "variables": {
    "STAC_COLLECTION_NAME": "sentinel2_ard",
    "STAC_ITEM_LINK": "https://example.com/stac/item/123",
    "AOI": "{\"type\":\"Polygon\",\"coordinates\":[...]}"
  }
}
```

Expected response fields:

- `servername`
- `notebook_path`
- `spawn_url`

Open `spawn_url` to launch directly in JupyterHub.

## Troubleshooting

- `TEMPLATE_FETCH_FAILED`: `template_url` is unreachable or non-200.
- `TEMPLATE_PARSE_FAILED`: file is not valid `.ipynb` JSON.
- `NOTEBOOK_UPLOAD_FAILED`: S3 permissions or bucket policy issue.

If placeholders are not replaced:

- Confirm exact placeholder syntax (`{{KEY}}`).
- Confirm key names in `variables` exactly match placeholder names.
- Confirm the placeholder is in cell source text (not metadata/output).
