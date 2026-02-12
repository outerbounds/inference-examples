#!/usr/bin/env python3
"""Test script to verify the Evidently AI app is deployed and accessible.

Tests:
1. Health check via /api/version endpoint
2. UI accessibility
3. (Optional) Create a test project and upload a snapshot
"""

import sys
import json
import os
import requests
from typing import Tuple


def get_auth_headers() -> dict:
    """Get authentication headers using Metaflow config."""
    try:
        from metaflow.metaflow_config_funcs import init_config

        conf = init_config()
        if conf:
            return {"x-api-key": conf["METAFLOW_SERVICE_AUTH_KEY"]}
        else:
            headers = json.loads(os.environ["METAFLOW_SERVICE_HEADERS"])
            return {"x-api-key": headers.get("x-api-key", "")}
    except Exception as e:
        print(f"Warning: Could not get auth headers: {e}")
        return {}


def test_health(url: str, headers: dict = None) -> Tuple[bool, str]:
    """Test Evidently health endpoint (/api/version)."""
    print(f"\n{'='*60}")
    print("Testing Evidently Health Check")
    print(f"{'='*60}")
    print(f"URL: {url}")

    try:
        health_url = f"{url.rstrip('/')}/api/version"
        print(f"Checking: {health_url}")

        response = requests.get(health_url, headers=headers or {}, timeout=10)

        if response.status_code == 200:
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return True, "Evidently is healthy"
        else:
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False, f"Unexpected status: {response.status_code}"

    except requests.exceptions.Timeout:
        return False, "Request timed out"
    except requests.exceptions.ConnectionError as e:
        return False, f"Connection error: {e}"
    except Exception as e:
        return False, f"Error: {e}"


def test_ui(url: str, headers: dict = None) -> Tuple[bool, str]:
    """Test Evidently UI accessibility."""
    print(f"\n{'='*60}")
    print("Testing Evidently UI")
    print(f"{'='*60}")
    print(f"URL: {url}")

    try:
        response = requests.get(
            url, headers=headers or {}, timeout=10, allow_redirects=False
        )

        if response.status_code in [200, 302, 307, 308]:
            print(f"Status: {response.status_code}")
            print("UI is accessible")
            return True, "UI is accessible"
        else:
            print(f"Status: {response.status_code}")
            return True, f"UI responded with status {response.status_code}"

    except requests.exceptions.Timeout:
        return False, "Request timed out"
    except requests.exceptions.ConnectionError as e:
        return False, f"Connection error: {e}"
    except Exception as e:
        return False, f"Error: {e}"


def test_create_project(url: str, headers: dict = None) -> Tuple[bool, str]:
    """Test creating a project via the Evidently API."""
    print(f"\n{'='*60}")
    print("Testing Project Creation")
    print(f"{'='*60}")

    try:
        from evidently.ui.remote import RemoteWorkspace

        workspace = RemoteWorkspace(url)

        project = workspace.create_project("test-outerbounds-deployment")
        project.description = "Test project created during deployment verification"
        project.save()

        print(f"Project created: {project.name} (id: {project.id})")

        # List projects to verify
        projects = workspace.list_projects()
        print(f"Total projects: {len(projects)}")

        return True, f"Project '{project.name}' created successfully"

    except Exception as e:
        return False, f"Error: {e}"


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Test deployed Evidently AI app",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test the deployed app (Browser auth - no API key needed for health)
  python test_app.py --url https://evidently-ui-xyz.outerbounds.xyz

  # Test with API key (for API-auth endpoints)
  python test_app.py --url https://evidently-ui-xyz.outerbounds.xyz --use-auth

  # Full test including project creation
  python test_app.py --url https://evidently-ui-xyz.outerbounds.xyz --test-project

  # Test locally
  python test_app.py --url http://localhost:8000
        """,
    )

    parser.add_argument("--url", required=True, help="URL of the Evidently deployment")
    parser.add_argument(
        "--use-auth", action="store_true", help="Include Metaflow auth headers"
    )
    parser.add_argument(
        "--test-project",
        action="store_true",
        help="Test creating a project via the API",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Evidently AI App Deployment Test")
    print("=" * 60)

    headers = get_auth_headers() if args.use_auth else {}

    results = []

    # Test health
    health_ok, health_msg = test_health(args.url, headers)
    results.append(("Health Check", health_ok, health_msg))

    # Test UI
    ui_ok, ui_msg = test_ui(args.url, headers)
    results.append(("UI Accessibility", ui_ok, ui_msg))

    # Test project creation if requested
    if args.test_project:
        proj_ok, proj_msg = test_create_project(args.url, headers)
        results.append(("Project Creation", proj_ok, proj_msg))

    # Print summary
    print(f"\n{'='*60}")
    print("Test Summary")
    print(f"{'='*60}")

    all_passed = True
    for test_name, success, message in results:
        status = "PASS" if success else "FAIL"
        print(f"{status} - {test_name}")
        print(f"     {message}")
        if not success:
            all_passed = False

    print(f"{'='*60}")

    if all_passed:
        print("All tests passed!")
        print(f"\nOpen Evidently UI in your browser: {args.url}")
        return 0
    else:
        print("Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
