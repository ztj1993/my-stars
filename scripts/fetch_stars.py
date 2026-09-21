#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch all starred repositories for a GitHub user.
Saves the raw metadata to data/raw_stars.json.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error

USERNAME = "ztj1993"
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw_stars.json")
PER_PAGE = 100


def get_headers():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) GitHubStarsFetcher/1.0",
        "Accept": "application/vnd.github.v3.star+json",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
        print("Using GitHub Token for authenticated API requests.")
    else:
        print("No GitHub Token provided; using unauthenticated API requests.")
    return headers


def fetch_page(user: str, page: int, headers: dict):
    url = f"https://api.github.com/users/{user}/starred?per_page={PER_PAGE}&page={page}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            rate_limit_remaining = resp.headers.get("X-RateLimit-Remaining")
            rate_limit_reset = resp.headers.get("X-RateLimit-Reset")
            link_header = resp.headers.get("Link", "")
            data = json.loads(resp.read().decode("utf-8"))
            return data, rate_limit_remaining, rate_limit_reset, link_header
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        print(f"HTTP Error {e.code}: {e.reason}\nBody: {body}", file=sys.stderr)
        raise
    except Exception as e:
        print(f"Error fetching page {page}: {e}", file=sys.stderr)
        raise


def fetch_all_stars(user: str):
    headers = get_headers()
    all_stars = []
    page = 1

    print(f"Starting to fetch stars for user '{user}'...")

    while True:
        print(f"Fetching page {page}...", end=" ", flush=True)
        data, remaining, reset_time, link_header = fetch_page(user, page, headers)
        
        if not data:
            print("Done (empty page).")
            break

        for item in data:
            # When Accept header is application/vnd.github.v3.star+json,
            # item has format: {"starred_at": "...", "repo": {...}}
            if "repo" in item and "starred_at" in item:
                repo_info = item["repo"]
                repo_info["starred_at"] = item["starred_at"]
                all_stars.append(repo_info)
            else:
                all_stars.append(item)

        print(f"Retrieved {len(data)} repos (Total so far: {len(all_stars)}). Rate limit remaining: {remaining}")

        if len(data) < PER_PAGE:
            print("Reached last page.")
            break

        if 'rel="next"' not in link_header and link_header:
            print("No next page indicated in Link header.")
            break

        page += 1
        time.sleep(0.5)  # Be polite to GitHub API

    print(f"Successfully fetched a total of {len(all_stars)} starred repositories.")
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_stars, f, ensure_ascii=False, indent=2)
    print(f"Raw stars data saved to: {OUTPUT_FILE}")
    return all_stars


if __name__ == "__main__":
    fetch_all_stars(USERNAME)
