#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests",
# ]
# ///

"""
List GitHub issues from a repository.

Usage:
    uv run scripts/list_issues.py <org> <repo>

Example:
    uv run scripts/list_issues.py python cpython
"""

import sys
import requests
from typing import Optional


def list_issues(org: str, repo: str, state: str = "open") -> None:
    """
    List GitHub issues for a given organization and repository.
    
    Args:
        org: GitHub organization or user name
        repo: Repository name
        state: Issue state - 'open', 'closed', or 'all' (default: 'open')
    """
    url = f"https://api.github.com/repos/{org}/{repo}/issues"
    params = {"state": state, "per_page": 30}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        issues = response.json()
        
        if not issues:
            print(f"No {state} issues found in {org}/{repo}")
            return
        
        print(f"\n{state.upper()} Issues for {org}/{repo}:\n")
        print(f"{'#':<6} {'Title':<60} {'State':<10}")
        print("-" * 76)
        
        for issue in issues:
            # Skip pull requests (GitHub API includes PRs in issues endpoint)
            if "pull_request" in issue:
                continue
                
            number = issue["number"]
            title = issue["title"][:57] + "..." if len(issue["title"]) > 60 else issue["title"]
            state_display = issue["state"]
            
            print(f"{number:<6} {title:<60} {state_display:<10}")
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"Error: Repository {org}/{repo} not found")
        else:
            print(f"Error: {e}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching issues: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) < 3:
        print("Usage: uv run scripts/list_issues.py <org> <repo> [state]")
        print("  state: open (default), closed, or all")
        sys.exit(1)
    
    org = sys.argv[1]
    repo = sys.argv[2]
    state = sys.argv[3] if len(sys.argv) > 3 else "open"
    
    if state not in ["open", "closed", "all"]:
        print(f"Error: Invalid state '{state}'. Must be 'open', 'closed', or 'all'")
        sys.exit(1)
    
    list_issues(org, repo, state)


if __name__ == "__main__":
    main()
