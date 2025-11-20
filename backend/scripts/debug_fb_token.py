#!/usr/bin/env python3
"""Validate a Facebook token and display basic info (id, name, scopes/expiry when possible).

Usage:
  python scripts/debug_fb_token.py --token "PAGE_OR_USER_TOKEN"

If `APP_ACCESS_TOKEN` (app_id|app_secret) is present in env, we will call debug_token for full info.
Otherwise we call /me and /oauth/access_token_info alternatives when available.
"""
from __future__ import annotations

import argparse
import os
import requests


def debug_with_app_token(input_token: str, app_access_token: str):
    endpoint = "https://graph.facebook.com/debug_token"
    params = {"input_token": input_token, "access_token": app_access_token}
    r = requests.get(endpoint, params=params, timeout=15)
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, {"text": r.text}


def me_call(token: str):
    endpoint = "https://graph.facebook.com/me"
    params = {"access_token": token, "fields": "id,name"}
    r = requests.get(endpoint, params=params, timeout=15)
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, {"text": r.text}


def main():
    parser = argparse.ArgumentParser(description="Debug a Facebook token")
    parser.add_argument("--token", required=False, help="Token to inspect (if omitted will use FB_PAGE_ACCESS_TOKEN env var)")
    args = parser.parse_args()

    token = args.token or os.environ.get("FB_PAGE_ACCESS_TOKEN")
    if not token:
        print("No token provided. Use --token or set FB_PAGE_ACCESS_TOKEN in your environment.")
        return

    app_token = os.environ.get("APP_ACCESS_TOKEN") or os.environ.get("FB_APP_ACCESS_TOKEN")

    if app_token:
        status, data = debug_with_app_token(token, app_token)
        print("debug_token status:", status)
        print(data)
        return

    # Fallback: call /me to see if token is valid and which user/page it belongs to
    status, data = me_call(token)
    print("/me status:", status)
    print(data)
    if status != 200:
        print("Consider setting APP_ACCESS_TOKEN env var (app_id|app_secret) to get full debug_token info.")


if __name__ == "__main__":
    main()
