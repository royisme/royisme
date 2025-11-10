# 🤖 Automated Featured Projects

This directory contains automation scripts for maintaining the GitHub profile README.

## 📋 Overview

The `update_featured_projects.py` script automatically updates the "Featured Projects" section in the main README.md based on your GitHub repository activity.

## 🎯 Features

- **Automated Selection**: Picks top 4 projects based on composite score
- **Composite Scoring**: `(stars × 3) + (forks × 2) + recency_score`
- **Smart Filtering**:
  - Only includes repositories you own (not forks)
  - Excludes profile README repository
  - Only public repositories
- **Rich Metadata**: Displays stars, forks, language, topics, and last update
- **Weekly Updates**: Runs automatically every Monday via GitHub Actions

## 🔄 How It Works

### Scoring Algorithm

Each repository gets a score based on:

1. **Stars (×3)**: Community popularity and interest
2. **Forks (×2)**: Practical usefulness and collaboration
3. **Recency (0-100)**: Days since last update
   - Recently updated projects get higher scores
   - Score decays over approximately 1 year
   - Formula: `max(0, 100 - (days_since_update / 3.65))`

### Project Selection

The script:
1. Fetches all your public repositories
2. Filters out forks and profile README
3. Calculates composite score for each
4. Selects top 4 projects
5. Generates formatted Markdown
6. Updates README between markers

## 🚀 Usage

### Automatic (Recommended)

The GitHub Actions workflow runs automatically:
- **Schedule**: Every Monday at 00:00 UTC
- **Manual**: Can be triggered manually from Actions tab

### Manual Execution

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GITHUB_TOKEN="your_github_token"
export README_PATH="README.md"
export TOP_N_PROJECTS="4"

# Run script
python scripts/update_featured_projects.py
```

## 📝 Configuration

Environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `GITHUB_TOKEN` | GitHub personal access token | Required for API |
| `README_PATH` | Path to README file | `README.md` |
| `TOP_N_PROJECTS` | Number of projects to feature | `4` |

## 🔧 Customization

### Change Number of Projects

Edit `.github/workflows/update-readme.yml`:

```yaml
env:
  TOP_N_PROJECTS: 6  # Change from 4 to 6
```

### Change Update Frequency

Edit the cron schedule in `.github/workflows/update-readme.yml`:

```yaml
schedule:
  - cron: '0 0 * * 1'  # Weekly on Monday
  # - cron: '0 0 * * *'  # Daily
  # - cron: '0 0 1 * *'  # Monthly
```

### Modify Scoring

Edit the `calculate_score()` method in `update_featured_projects.py`:

```python
# Current formula
total_score = (stars * 3) + (forks * 2) + recency_score

# Example: Prioritize stars more
total_score = (stars * 5) + (forks * 1) + recency_score
```

## 📄 README Markers

The script updates content between these markers in README.md:

```markdown
<!-- FEATURED_PROJECTS_START -->
... auto-generated content ...
<!-- FEATURED_PROJECTS_END -->
```

**Important**: Do not remove these markers!

## 🐛 Troubleshooting

### Script Fails to Run

- Check GitHub Actions logs in repository → Actions tab
- Verify markers exist in README.md
- Ensure workflow has write permissions

### Wrong Projects Selected

- Review scoring algorithm weights
- Check repository visibility (must be public)
- Verify repositories aren't forks

### No Updates Appearing

- Check if repositories have recent activity
- Verify GitHub token has correct permissions
- Look for changes in GitHub Actions logs

## 📚 Dependencies

- Python 3.11+
- `requests` library for GitHub API calls

## 🔒 Security

- Uses GitHub's built-in `GITHUB_TOKEN` (no personal token needed)
- Token is automatically provided by GitHub Actions
- Limited scope: only repository content access

## 📖 Resources

- [GitHub REST API](https://docs.github.com/en/rest)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Cron Expression Format](https://crontab.guru/)
