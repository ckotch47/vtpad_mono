#!/usr/bin/env python3
"""Smoke-test all API endpoints and report 500s."""

import asyncio
import json
import sys
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin

import httpx
from jose import jwt

BASE_URL = "http://localhost:3003"
ENV = {}


def load_env():
    with open(".env") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                ENV[k] = v


def make_token():
    secret = ENV.get("SECRET_KEY")
    algo = ENV.get("ALGORITHM", "HS256")
    admin_id = ENV.get("main_admin_id", "b81d76f4-eb39-4ba7-a9eb-c9d192426553")
    expire = datetime.now(timezone.utc) + timedelta(minutes=30000)
    payload = {"mail": "admin@vtpad.local", "id": admin_id, "exp": expire}
    return jwt.encode(payload, secret, algorithm=algo)


async def test_all():
    load_env()
    token = make_token()
    headers_auth = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=15.0) as client:
        # fetch OpenAPI schema
        r = await client.get("/openapi.json")
        if r.status_code != 200:
            print("ERROR: cannot fetch /openapi.json")
            sys.exit(1)
        schema = r.json()

        results = {"ok": 0, "err": 0, "details": []}
        paths = list(schema["paths"].items())
        total = len(paths)

        for idx, (path, methods) in enumerate(paths, 1):
            for method, info in methods.items():
                if method == "options":
                    continue
                url = path
                # replace path params with dummy values
                url = url.replace("{space_id}", "00000000-0000-0000-0000-000000000001")
                url = url.replace("{bug_id}", "00000000-0000-0000-0000-000000000002")
                url = url.replace("{pad_id}", "00000000-0000-0000-0000-000000000003")
                url = url.replace("{run_id}", "00000000-0000-0000-0000-000000000004")
                url = url.replace("{item_id}", "00000000-0000-0000-0000-000000000005")
                url = url.replace("{folder_id}", "00000000-0000-0000-0000-000000000006")
                url = url.replace("{tag_id}", "00000000-0000-0000-0000-000000000007")
                url = url.replace("{testcase_id}", "00000000-0000-0000-0000-000000000008")
                url = url.replace("{comment_id}", "00000000-0000-0000-0000-000000000009")
                url = url.replace("{note_id}", "00000000-0000-0000-0000-000000000010")
                url = url.replace("{checklist_id}", "00000000-0000-0000-0000-000000000011")
                url = url.replace("{user_id}", "00000000-0000-0000-0000-000000000012")
                url = url.replace("{company_id}", "00000000-0000-0000-0000-000000000013")
                url = url.replace("{notification_id}", "00000000-0000-0000-0000-000000000014")
                url = url.replace("{element_id}", "00000000-0000-0000-0000-000000000015")
                url = url.replace("{image_id}", "00000000-0000-0000-0000-000000000016")
                url = url.replace("{short_name}", "TEST-1")
                url = url.replace("{row}", "state")
                url = url.replace("{suite_id}", "00000000-0000-0000-0000-000000000017")
                url = url.replace("{test_id}", "00000000-0000-0000-0000-000000000018")
                url = url.replace("{file_id}", "00000000-0000-0000-0000-000000000019")
                url = url.replace("{paditem_id}", "00000000-0000-0000-0000-000000000020")

                req_headers = headers_auth.copy()
                body = None

                if method in ("post", "put", "patch"):
                    # try empty JSON body; most will 422, that's fine
                    body = {}
                    req_headers["Content-Type"] = "application/json"

                try:
                    resp = await client.request(
                        method.upper(), url, headers=req_headers, json=body
                    )
                except Exception as e:
                    results["err"] += 1
                    results["details"].append(
                        {"method": method.upper(), "url": url, "status": f"EXC: {e}"}
                    )
                    continue

                status = resp.status_code
                if status >= 500:
                    results["err"] += 1
                    results["details"].append(
                        {"method": method.upper(), "url": url, "status": status}
                    )
                else:
                    results["ok"] += 1

                print(f"[{idx}/{total}] {method.upper():7} {url:60} -> {status}")

        print(f"\n{'='*70}")
        print(f"Total endpoints tested: {results['ok'] + results['err']}")
        print(f"OK (no 500): {results['ok']}")
        print(f"ERRORS (500 or exception): {results['err']}")
        if results["details"]:
            print("\nFailed endpoints:")
            for d in results["details"]:
                print(f"  {d['method']} {d['url']} -> {d['status']}")
        print(f"{'='*70}")
        return results["err"]


if __name__ == "__main__":
    err_count = asyncio.run(test_all())
    sys.exit(err_count)
