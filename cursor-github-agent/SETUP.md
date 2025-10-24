# GitHub Agent Setup Guide

## Quick Setup

### 1. Create a GitHub Personal Access Token

1. Go to https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Give it a name: `Cursor GitHub MCP Agent`
4. Select scopes:
   - ✅ `public_repo` (for public repositories)
   - ✅ `repo` (if you need access to private repositories)
5. Click **"Generate token"**
6. **Copy the token** (you won't be able to see it again!)

### 2. Configure the Token

Copy the example environment file and add your token:

```bash
cd /home/omcgonag/Work/mymcp/cursor-github-agent
cp example.env .env
```

Edit `.env` and replace `your_github_token_here` with your actual token:

```bash
GITHUB_TOKEN=ghp_your_actual_token_here
```

### 3. Restart Cursor

After adding the token:
1. Save all files
2. Fully quit Cursor
3. Reopen Cursor

### 4. Test the Agent

In Cursor chat, try:

```
@github-reviewer-agent Review https://github.com/openstack-k8s-operators/horizon-operator/pull/402
```

## Troubleshooting

### "GITHUB_TOKEN environment variable not set"

- Make sure you created the `.env` file in the `cursor-github-agent` directory
- Make sure the `.env` file contains: `GITHUB_TOKEN=your_token_here`
- Restart Cursor completely

### "GitHub API error: 401"

- Your token is invalid or expired
- Create a new token and update your `.env` file

### "GitHub API error: 404"

- The repository or PR doesn't exist
- You don't have access to the repository (if private)

## Security Notes

- ⚠️ **Never commit the `.env` file to Git** - it contains your token!
- ✅ The `.gitignore` file is already configured to exclude `.env`
- 🔄 You can revoke/regenerate tokens at any time from GitHub settings



