# Red Hat Jira API Token Setup

**Issue**: OSPRH-19705 not appearing in activity reports  
**Cause**: JIRA_API_TOKEN not configured with real token

---

## 🔐 How to Get Your Red Hat Jira API Token

### Step 1: Generate Personal Access Token

Red Hat Jira uses **Personal Access Tokens** (not the same as Atlassian Cloud API tokens).

**Instructions**:

1. **Log in to Red Hat Jira**:
   - Go to: https://issues.redhat.com

2. **Access Your Profile**:
   - Click your profile icon (top right)
   - Select "Profile" or "Account Settings"

3. **Find Personal Access Tokens**:
   - Look for "Personal Access Tokens" section
   - Or navigate to: https://issues.redhat.com/secure/ViewProfile.jspa
   - Click on "Personal Access Tokens" in the left menu

4. **Create New Token**:
   - Click "Create token" or similar button
   - Give it a name: `mymcp-activity-tracker`
   - Set expiration (recommend: 1 year)
   - Click "Create"

5. **Copy the Token**:
   - **IMPORTANT**: Copy the token immediately!
   - You won't be able to see it again after closing the dialog

---

### Step 2: Update Configuration

**Edit file**: `/home/omcgonag/Work/mymcp/jira-agent/.env`

**Replace this line**:
```bash
JIRA_API_TOKEN=<your-api-token>
```

**With your actual token**:
```bash
JIRA_API_TOKEN=YOUR_ACTUAL_TOKEN_HERE
```

**Example** (not a real token):
```bash
JIRA_API_TOKEN=YOUR_ACTUAL_JIRA_TOKEN_HERE_DO_NOT_COMMIT
```

---

### Step 3: Verify Configuration

After updating, your `.env` file should look like:

```bash
# See https://github.com/redhat-ai-tools/jira-mcp
JIRA_URL=https://issues.redhat.com
JIRA_API_TOKEN=YOUR_ACTUAL_TOKEN_HERE
JIRA_EMAIL=omcgona@redhat.com
```

---

### Step 4: Test the Configuration

Run this command to verify:

```bash
cd /home/omcgonag/Work/mymcp/activity-tracker-agent
python3 << 'EOF'
import server
import requests

headers = {
    'Authorization': f'Bearer {server.JIRA_API_TOKEN}',
    'Content-Type': 'application/json'
}

# Test query
jql = f'key = OSPRH-19705'
response = requests.get(
    f'{server.JIRA_URL}/rest/api/3/search',
    headers=headers,
    params={'jql': jql, 'fields': 'key,summary,status,assignee'}
)

if response.status_code == 200:
    data = response.json()
    if data.get('total', 0) > 0:
        issue = data['issues'][0]
        print(f"✅ Successfully fetched OSPRH-19705!")
        print(f"   Summary: {issue['fields']['summary']}")
        print(f"   Status: {issue['fields']['status']['name']}")
    else:
        print("❌ No issues found")
else:
    print(f"❌ API Error: {response.status_code}")
    print(f"Response: {response.text[:500]}")
EOF
```

---

### Step 5: Regenerate Report

Once configured, clear the cache and regenerate:

```bash
cd /home/omcgonag/Work/mymcp/activity-tracker-agent
rm ~/Work/mymcp/workspace/iproject/activity/2025-W46.json
python3 -c "import server; print(server.generate_status_report('this week'))"
```

OSPRH-19705 should now appear in the "Jira: My Open Tickets" section!

---

## 🔍 Alternative: Check Authentication Method

If Personal Access Tokens don't work, Red Hat Jira might use a different auth method:

### Option 1: Basic Auth (Username + Password)
Some enterprise Jira instances use basic auth. Try:

```bash
# In jira-agent/.env, change the API token line to:
JIRA_USERNAME=omcgona
JIRA_PASSWORD=your_password
```

Then update `server.py` to use basic auth instead of Bearer token.

### Option 2: Check with IT/Admin
Ask your Red Hat IT team:
- "How do I generate an API token for https://issues.redhat.com?"
- "What authentication method should I use for the Jira REST API?"

---

## 📚 References

- **Red Hat Jira**: https://issues.redhat.com
- **Jira REST API Docs**: https://docs.atlassian.com/software/jira/docs/api/REST/latest/
- **Personal Access Tokens**: Check your Jira profile settings

---

## 🆘 Need Help?

If you're having trouble:

1. **Check if you can access Jira API manually**:
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        "https://issues.redhat.com/rest/api/3/myself"
   ```
   
   Should return your user info if auth works.

2. **Check your Jira profile**:
   - Make sure OSPRH-19705 is actually assigned to you
   - Make sure status is not "Done", "Closed", or "Resolved"

3. **Contact me**:
   - Share the error message you get (without the token!)
   - I can help debug the authentication

---

*Last updated: 2025-11-24*

