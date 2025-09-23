#!/usr/bin/env python3
"""
Test script for the updated STAC-based QLR API
"""

import requests
from typing import Dict, Any


def create_sample_stac_item() -> Dict[str, Any]:
    """Create a sample STAC item for testing"""
    return {
        "type": "Feature",
        "stac_version": "1.0.0",
        "stac_extensions": ["proj"],
        "id": "test-item-001",
        "collection": "sentinel2_ard",
        "bbox": [-122.5, 37.7, -122.3, 37.9],
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [-122.5, 37.7],
                    [-122.3, 37.7],
                    [-122.3, 37.9],
                    [-122.5, 37.9],
                    [-122.5, 37.7],
                ]
            ],
        },
        "properties": {"datetime": "2023-01-01T00:00:00Z", "proj:epsg": 32610},
        "links": [
            {
                "rel": "self",
                "type": "application/geo+json",
                "href": "https://api.example.com/collections/sentinel2_ard/items/test-item-001",
            }
        ],
        "assets": {
            "cog": {
                "href": "https://storage.example.com/data/test-item-001.tif",
                "roles": ["data"],
                "size": 12345678,
                "location": "s3://bucket/path/test-item-001.tif",
            },
            "thumbnail": {
                "href": "https://storage.example.com/thumb/test-item-001.jpg",
                "roles": ["thumbnail"],
                "size": 12345,
                "location": "s3://bucket/path/test-item-001.jpg",
            },
        },
        "tilesUrl": "https://tiles.example.com/test-item-001",
        "render": {
            "title": "Natural Color",
            "assets": ["cog"],
            "bidx": [3, 2, 1],
            "nodata": 0,
            "color_formula": "Gamma RGB 6 Saturation 0.8 Sigmoidal RGB 25 0.35",
        },
    }


def test_api():
    """Test the updated API endpoint"""
    base_url = "http://localhost:8000"

    # Test health endpoint first
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running.")
        return

    # Test the new STAC-based QLR endpoint
    print("\nTesting STAC-based QLR endpoint...")

    sample_item = create_sample_stac_item()

    try:
        response = requests.post(
            f"{base_url}/qlr",
            json=sample_item,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 200:
            print("✅ QLR generation successful")
            print(f"Content-Type: {response.headers.get('Content-Type')}")
            print(f"Content-Disposition: {response.headers.get('Content-Disposition')}")

            # Save the QLR content to a file for inspection
            with open("test_output.qlr", "w") as f:
                f.write(response.text)
            print("QLR content saved to test_output.qlr")

            # Show first few lines of the QLR
            lines = response.text.split("\n")[:10]
            print("\nFirst 10 lines of QLR:")
            for i, line in enumerate(lines, 1):
                print(f"{i:2d}: {line}")

        else:
            print(f"❌ QLR generation failed: {response.status_code}")
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"❌ Error testing QLR endpoint: {e}")


if __name__ == "__main__":
    test_api()
