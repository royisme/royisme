#!/usr/bin/env python3
"""
Auto-update Featured Projects section in README.md based on GitHub repository data.

This script fetches user's public repositories, calculates a composite score,
and updates the README with the top projects.
"""

import os
import sys
import re
from datetime import datetime, timezone
from typing import List, Dict, Optional
import requests


class GitHubProjectUpdater:
    """Handles fetching and updating featured GitHub projects."""

    def __init__(self, username: str, github_token: Optional[str] = None):
        self.username = username
        self.github_token = github_token
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if github_token:
            self.headers["Authorization"] = f"token {github_token}"

    def fetch_repositories(self) -> List[Dict]:
        """Fetch all public repositories for the user."""
        repos = []
        page = 1
        per_page = 100

        print(f"Fetching repositories for user: {self.username}")

        while True:
            url = f"https://api.github.com/users/{self.username}/repos"
            params = {
                "type": "owner",  # Only repos owned by user, not forks
                "sort": "updated",
                "per_page": per_page,
                "page": page
            }

            response = requests.get(url, headers=self.headers, params=params)

            if response.status_code != 200:
                print(f"Error fetching repositories: {response.status_code}")
                print(response.text)
                sys.exit(1)

            data = response.json()
            if not data:
                break

            repos.extend(data)
            page += 1

        print(f"Fetched {len(repos)} repositories")
        return repos

    def calculate_score(self, repo: Dict) -> float:
        """
        Calculate composite score for a repository.

        Formula: (stars * 3) + (forks * 2) + recency_score
        - Stars: High weight (3x) - indicates popularity
        - Forks: Medium weight (2x) - indicates usefulness
        - Recency: Days since last update, normalized (max 100 points)
        """
        stars = repo.get("stargazers_count", 0)
        forks = repo.get("forks_count", 0)

        # Calculate recency score (0-100 based on days since update)
        updated_at = repo.get("updated_at", "")
        if updated_at:
            updated_date = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            days_since_update = (datetime.now(timezone.utc) - updated_date).days
            # More recent = higher score (max 100 for today, decreases linearly to 0 after 1 year)
            recency_score = max(0, 100 - days_since_update * (100 / 365))  # Decay over ~1 year
        else:
            recency_score = 0

        total_score = (stars * 3) + (forks * 2) + recency_score

        return total_score

    def filter_and_rank_repos(self, repos: List[Dict], top_n: int = 4) -> List[Dict]:
        """Filter repositories and return top N by composite score."""
        # Filter out forks and profile README repo
        filtered_repos = [
            repo for repo in repos
            if not repo.get("fork", False)  # Not a fork
            and repo["name"].lower() != self.username.lower()  # Not profile README
            and not repo.get("private", False)  # Public only
        ]

        print(f"Filtered to {len(filtered_repos)} non-fork, non-profile repos")

        # Calculate scores
        for repo in filtered_repos:
            repo["_score"] = self.calculate_score(repo)

        # Sort by score (descending)
        ranked_repos = sorted(filtered_repos, key=lambda r: r["_score"], reverse=True)

        # Return top N
        top_repos = ranked_repos[:top_n]

        print(f"\nTop {len(top_repos)} projects:")
        for i, repo in enumerate(top_repos, 1):
            print(f"{i}. {repo['name']} (score: {repo['_score']:.2f}, "
                  f"stars: {repo['stargazers_count']}, forks: {repo['forks_count']})")

        return top_repos

    def get_language_emoji(self, language: Optional[str]) -> str:
        """Get emoji for programming language."""
        emoji_map = {
            "Python": "🐍",
            "JavaScript": "🟨",
            "TypeScript": "🔷",
            "Java": "☕",
            "Go": "🐹",
            "Rust": "🦀",
            "Ruby": "💎",
            "PHP": "🐘",
            "C++": "⚡",
            "C#": "🎯",
            "Swift": "🦅",
            "Kotlin": "🅺",
            "Vue": "💚",
            "React": "⚛️",
            "HTML": "🌐",
            "CSS": "🎨",
            "Shell": "🐚",
            "Jupyter Notebook": "📓",
        }
        return emoji_map.get(language, "📦")

    def format_project_section(self, repos: List[Dict]) -> str:
        """Format repositories as Markdown for README."""
        if not repos:
            return "No featured projects available.\n"

        sections = []

        for repo in repos:
            name = repo["name"]
            description = repo.get("description", "No description available.")
            html_url = repo["html_url"]
            language = repo.get("language", "")
            topics = repo.get("topics", [])
            stars = repo.get("stargazers_count", 0)
            forks = repo.get("forks_count", 0)
            updated_at = repo.get("updated_at", "")

            # Parse update date
            if updated_at:
                updated_date = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                last_update = updated_date.strftime("%B %Y")
            else:
                last_update = "Unknown"

            # Build tech stack from language and topics
            tech_stack = []
            if language:
                tech_stack.append(language)
            if topics:
                # Capitalize topics nicely
                formatted_topics = [t.replace('-', ' ').title() for t in topics[:5]]
                tech_stack.extend(formatted_topics)

            tech_stack_str = " • ".join(tech_stack[:6]) if tech_stack else "Various Technologies"

            # Get emoji
            emoji = self.get_language_emoji(language)

            # Build section
            section = f"""### {emoji} [{name}]({html_url})
**{tech_stack_str}**

{description}

- ⭐ **{stars}** stars | 🔀 **{forks}** forks
- 📅 Last updated: {last_update}

---
"""
            sections.append(section)

        return "\n".join(sections)

    def update_readme(self, readme_path: str, featured_content: str) -> bool:
        """Update README.md with new featured projects section."""
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Error: {readme_path} not found")
            return False

        # Define markers
        start_marker = "<!-- FEATURED_PROJECTS_START -->"
        end_marker = "<!-- FEATURED_PROJECTS_END -->"

        # Check if markers exist
        if start_marker not in content or end_marker not in content:
            print(f"Error: Markers not found in README")
            print(f"Please add the following markers to your README.md:")
            print(f"  {start_marker}")
            print(f"  {end_marker}")
            return False

        # Replace content between markers
        pattern = f"{re.escape(start_marker)}.*?{re.escape(end_marker)}"
        replacement = f"{start_marker}\n\n{featured_content}\n{end_marker}"

        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

        # Write back
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"\n✅ Successfully updated {readme_path}")
        return True


def main():
    """Main execution function."""
    # Get configuration from environment
    github_repository = os.environ.get("GITHUB_REPOSITORY", "")
    if github_repository and "/" in github_repository:
        username = github_repository.split("/")[0]
    else:
        username = os.environ.get("GITHUB_ACTOR", "")

    if not username:
        print("Error: Could not determine GitHub username")
        print("Set GITHUB_REPOSITORY or GITHUB_ACTOR environment variable")
        sys.exit(1)

    github_token = os.environ.get("GITHUB_TOKEN")
    readme_path = os.environ.get("README_PATH", "README.md")
    top_n = int(os.environ.get("TOP_N_PROJECTS", "4"))

    print(f"Configuration:")
    print(f"  Username: {username}")
    print(f"  README path: {readme_path}")
    print(f"  Top N projects: {top_n}")
    print(f"  Token present: {bool(github_token)}\n")

    # Initialize updater
    updater = GitHubProjectUpdater(username, github_token)

    # Fetch and process repositories
    repos = updater.fetch_repositories()
    top_repos = updater.filter_and_rank_repos(repos, top_n=top_n)

    # Format content
    featured_content = updater.format_project_section(top_repos)

    # Update README
    success = updater.update_readme(readme_path, featured_content)

    if success:
        print("\n🎉 Featured projects updated successfully!")
        sys.exit(0)
    else:
        print("\n❌ Failed to update featured projects")
        sys.exit(1)


if __name__ == "__main__":
    main()
