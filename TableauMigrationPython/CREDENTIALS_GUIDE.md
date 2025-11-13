# Where to Put Your Credentials

You need credentials for **two systems**:
1. **SOURCE**: Your Tableau Server (on-premises)
2. **DESTINATION**: Your Tableau Cloud

---

## What You Need

For **each system**, you need 4 pieces of information:

### For Tableau Server (Source):
1. **Server URL** - e.g., `https://tableau-server.company.com`
2. **Site Content URL** - e.g., `marketing` (or empty `""` for default site)
3. **Access Token Name** - Personal Access Token name
4. **Access Token Secret** - The actual token value

### For Tableau Cloud (Destination):
1. **POD URL** - e.g., `https://10ax.online.tableau.com`
2. **Site Content URL** - e.g., `production`
3. **Access Token Name** - Personal Access Token name
4. **Access Token Secret** - The actual token value

---

## How to Get Personal Access Tokens

### On Tableau Server:
1. Sign in to Tableau Server
2. Click your profile icon → **My Account Settings**
3. Scroll to **Personal Access Tokens**
4. Click **Create new token**
5. Give it a name (e.g., "Migration Script")
6. Copy the **token name** and **token secret** (you can't see secret again!)

### On Tableau Cloud:
1. Sign in to Tableau Cloud
2. Click your profile icon → **My Account Settings**
3. Scroll to **Personal Access Tokens**
4. Click **Create new token**
5. Give it a name (e.g., "Migration Script")
6. Copy the **token name** and **token secret**

**⚠️ IMPORTANT:** Save the token secret immediately - you can't retrieve it later!

---

## Where to Store Credentials (3 Options)

### Option 1: Environment Variables ⭐ MOST SECURE

**Best for:** Production use, CI/CD pipelines

**Setup:**
```bash
# Linux/Mac - Add to ~/.bashrc or ~/.zshrc
export TABLEAU_SERVER_URL="https://tableau-server.company.com"
export TABLEAU_SERVER_SITE="marketing"
export TABLEAU_SERVER_TOKEN_NAME="migration-script"
export TABLEAU_SERVER_TOKEN="your-server-token-here"

export TABLEAU_CLOUD_URL="https://10ax.online.tableau.com"
export TABLEAU_CLOUD_SITE="production"
export TABLEAU_CLOUD_TOKEN_NAME="migration-script"
export TABLEAU_CLOUD_TOKEN="your-cloud-token-here"

# Then reload:
source ~/.bashrc
```

```powershell
# Windows PowerShell
$env:TABLEAU_SERVER_URL="https://tableau-server.company.com"
$env:TABLEAU_SERVER_SITE="marketing"
$env:TABLEAU_SERVER_TOKEN_NAME="migration-script"
$env:TABLEAU_SERVER_TOKEN="your-server-token-here"

$env:TABLEAU_CLOUD_URL="https://10ax.online.tableau.com"
$env:TABLEAU_CLOUD_SITE="production"
$env:TABLEAU_CLOUD_TOKEN_NAME="migration-script"
$env:TABLEAU_CLOUD_TOKEN="your-cloud-token-here"
```

**Use in code:**
```python
python config_env_vars.py
```

**Pros:**
- ✅ Most secure (never in code or files)
- ✅ Works in CI/CD
- ✅ Easy to change without editing code

**Cons:**
- ⚠️ Need to set for each session (unless in profile)

---

### Option 2: .env File ⭐ EASIEST

**Best for:** Local development, team sharing (with caution)

**Setup:**
```bash
# 1. Copy template
cp .env.template .env

# 2. Edit .env with your credentials
nano .env

# 3. Make sure .env is in .gitignore!
echo ".env" >> .gitignore
```

**Your .env file:**
```bash
TABLEAU_SERVER_URL=https://tableau-server.company.com
TABLEAU_SERVER_SITE=marketing
TABLEAU_SERVER_TOKEN_NAME=migration-script
TABLEAU_SERVER_TOKEN=abc123xyz789

TABLEAU_CLOUD_URL=https://10ax.online.tableau.com
TABLEAU_CLOUD_SITE=production
TABLEAU_CLOUD_TOKEN_NAME=cloud-migration
TABLEAU_CLOUD_TOKEN=def456uvw012
```

**Use in code (with python-dotenv):**
```bash
pip install python-dotenv
```

```python
from dotenv import load_dotenv
load_dotenv()  # Loads .env into environment variables

# Then use config_env_vars.py
```

**Pros:**
- ✅ Easy to manage
- ✅ One file for all credentials
- ✅ Can be shared (carefully) with team

**Cons:**
- ⚠️ Risk of committing to git (use .gitignore!)

---

### Option 3: config.json File

**Best for:** Testing, different environments

**Setup:**
```bash
# 1. Copy template
cp config.json.template config.json

# 2. Edit config.json with your credentials
nano config.json

# 3. Add to .gitignore!
echo "config.json" >> .gitignore
```

**Your config.json:**
```json
{
  "source": {
    "server_url": "https://tableau-server.company.com",
    "site_content_url": "marketing",
    "access_token_name": "migration-script",
    "access_token": "abc123xyz789"
  },
  "destination": {
    "pod_url": "https://10ax.online.tableau.com",
    "site_content_url": "production",
    "access_token_name": "cloud-migration",
    "access_token": "def456uvw012"
  }
}
```

**Use in code:**
```python
python config_json_file.py
```

**Pros:**
- ✅ Easy to read/edit
- ✅ Can have multiple files (config-dev.json, config-prod.json)
- ✅ JSON format

**Cons:**
- ⚠️ Risk of committing to git

---

## Using Credentials in Your Scripts

### Update Any Example Script:

**Original (hardcoded):**
```python
plan_builder = (
    plan_builder
    .from_source_tableau_server(
        server_url="https://tableau-server.company.com",  # ← Change these
        site_content_url="marketing",
        access_token_name="server-token",
        access_token="server-secret"
    )
    .to_destination_tableau_cloud(
        pod_url="https://10ax.online.tableau.com",
        site_content_url="production",
        access_token_name="cloud-token",
        access_token="cloud-secret"
    )
)
```

**Updated (using environment variables):**
```python
import os

plan_builder = (
    plan_builder
    .from_source_tableau_server(
        server_url=os.environ['TABLEAU_SERVER_URL'],
        site_content_url=os.environ['TABLEAU_SERVER_SITE'],
        access_token_name=os.environ['TABLEAU_SERVER_TOKEN_NAME'],
        access_token=os.environ['TABLEAU_SERVER_TOKEN']
    )
    .to_destination_tableau_cloud(
        pod_url=os.environ['TABLEAU_CLOUD_URL'],
        site_content_url=os.environ['TABLEAU_CLOUD_SITE'],
        access_token_name=os.environ['TABLEAU_CLOUD_TOKEN_NAME'],
        access_token=os.environ['TABLEAU_CLOUD_TOKEN']
    )
)
```

**Updated (using JSON config):**
```python
import json

with open('config.json') as f:
    config = json.load(f)

plan_builder = (
    plan_builder
    .from_source_tableau_server(**config['source'])
    .to_destination_tableau_cloud(**config['destination'])
)
```

---

## Security Best Practices

### ✅ DO:
- Use environment variables for production
- Add `.env` and `config.json` to `.gitignore`
- Rotate tokens regularly
- Use separate tokens for dev/test/prod
- Limit token permissions (Site Admin minimum)
- Document which tokens are for what

### ❌ DON'T:
- Commit credentials to git
- Share tokens in Slack/email
- Use the same token for everything
- Leave tokens in code comments
- Give tokens more permissions than needed

---

## Quick Start Checklist

- [ ] Get Personal Access Token from Tableau Server
- [ ] Get Personal Access Token from Tableau Cloud
- [ ] Choose credential storage method:
  - [ ] Environment variables (most secure)
  - [ ] .env file (easiest)
  - [ ] config.json file (flexible)
- [ ] Add credential files to .gitignore
- [ ] Test credentials with Example 1
- [ ] Update your migration scripts

---

## Example: Complete Setup

```bash
# 1. Create .env file
cp .env.template .env

# 2. Edit with your credentials
nano .env

# 3. Add to gitignore
echo ".env" >> .gitignore
echo "config.json" >> .gitignore

# 4. Install python-dotenv (for .env support)
pip install python-dotenv

# 5. Test it
python examples/1_basic_migration_setup.py
```

---

## Troubleshooting

### "Authentication failed"
- Check token name and secret are correct
- Ensure token hasn't expired
- Verify you have Site Admin permissions
- Try creating a new token

### "Site not found"
- Check site_content_url spelling
- Use empty string `""` for default site
- Site names are case-sensitive

### "Invalid server URL"
- Include `https://`
- No trailing slash
- Server must be accessible from your machine

### Environment variables not working
- Make sure you exported them (Linux/Mac)
- Make sure you set them in current session (Windows)
- Check spelling (case-sensitive!)
- Try: `echo $TABLEAU_SERVER_URL` to verify

---

## Summary

**Recommended approach:**

1. **Development:** Use `.env` file (with python-dotenv)
2. **Production:** Use environment variables
3. **Testing:** Use `config.json` with different files per environment

**Never commit credentials to git!**

```bash
# .gitignore
.env
config.json
*.json.local
```
