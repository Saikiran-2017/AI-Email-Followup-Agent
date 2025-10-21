# Email Follow-up Agent - Setup Guide

## 🎯 What This Does

This automated agent will:
1. ✅ Find all emails you've sent to vendors/recruiters
2. ✅ Check if they replied to each email
3. ✅ Send follow-up emails ONLY to those who didn't reply
4. ✅ Send follow-ups in the SAME thread (below the original email)

---

## 📋 Prerequisites

- Python 3.7 or higher
- A Gmail account
- Internet connection

---

## 🚀 Setup Instructions

### Step 1: Install Python Dependencies

Open your terminal/command prompt and run:

```bash
pip install -r requirements.txt
```

### Step 2: Enable Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing one)
3. Enable the Gmail API:
   - Click "Enable APIs and Services"
   - Search for "Gmail API"
   - Click "Enable"

### Step 3: Create OAuth Credentials

1. In Google Cloud Console, go to "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Configure OAuth consent screen (if prompted):
   - User Type: External
   - App name: Email Follow-up Agent
   - Add your email as test user
4. Application type: "Desktop app"
5. Download the credentials
6. Rename downloaded file to `credentials.json`
7. Place `credentials.json` in the same folder as `email_followup_agent.py`

### Step 4: First Run (Authentication)

Run the script for the first time:

```bash
python email_followup_agent.py
```

- A browser window will open
- Sign in to your Gmail account
- Grant permissions to the app
- You'll see "The authentication flow has completed"
- Close the browser tab

A `token.pickle` file will be created (this stores your authentication for future runs)

---

## 🎮 How to Use

### Basic Usage

1. **DRY RUN (Test Mode - Recommended First)**

   Edit `email_followup_agent.py` and set:
   ```python
   DRY_RUN = True  # No emails will be sent
   DAYS_BACK = 14  # Check emails from last 14 days
   ```

   Run:
   ```bash
   python email_followup_agent.py
   ```

   This will show you:
   - How many emails were found
   - Which ones need follow-ups
   - What would be sent (without actually sending)

2. **LIVE RUN (Actually Send Follow-ups)**

   After verifying the dry run results, edit:
   ```python
   DRY_RUN = False  # This will send actual emails
   ```

   Run:
   ```bash
   python email_followup_agent.py
   ```

### Advanced Configuration

In the `main()` function, you can customize:

```python
# How many days back to search
DAYS_BACK = 14  # Default: 14 days

# Filter by subject keywords (optional)
SUBJECT_KEYWORDS = ['application', 'opportunity', 'position', 'job']
# Or set to None to check ALL sent emails
SUBJECT_KEYWORDS = None

# Dry run mode
DRY_RUN = True  # True = test mode, False = actually send
```

---

## 📧 Customizing the Follow-up Email

To customize the follow-up message, edit the `create_followup_message()` function in the script:

```python
body = f"""{greeting}

I wanted to follow up on my previous email regarding {original_subject}.

[Your custom message here]

Best regards"""
```

---

## 🔒 Security & Privacy

- **Your credentials are stored locally** in `credentials.json` and `token.pickle`
- **Never share these files** with anyone
- The script only accesses YOUR Gmail account
- No data is sent to any third-party servers (except Google's Gmail API)

---

## 📊 What the Output Looks Like

```
==============================================================
📧 EMAIL FOLLOW-UP AGENT
==============================================================

🔍 Searching for emails sent in the last 14 days...
✓ Found 100 sent emails

📊 Analyzing 100 emails for replies...

[1/100] Checking: recruiter@company.com...
  ✓ Already replied - skipping
[2/100] Checking: vendor@example.com...
  ⚠️  No reply - needs follow-up
...

==============================================================
📊 SUMMARY
==============================================================
Total emails analyzed: 100
Already replied: 45
Need follow-up: 55
==============================================================

📤 [DRY RUN] Would send 55 follow-up emails...

[1/55] vendor@example.com
  [DRY RUN] Would send follow-up
...

✅ Follow-up campaign complete!
```

---

## ⚡ Pro Tips

1. **Always run in DRY RUN mode first** to verify what will be sent

2. **Rate Limiting**: The script automatically waits 2 seconds between sending each email to avoid Gmail's rate limits

3. **Customize the timeframe**: If you sent emails more than 14 days ago, increase `DAYS_BACK`

4. **Filter by subject**: Use `SUBJECT_KEYWORDS` to only follow up on specific types of emails

5. **Check sent folder**: The follow-ups will appear in your Sent folder and in the original thread

---

## ❓ Troubleshooting

### "Authentication failed"
- Delete `token.pickle` and run again
- Make sure `credentials.json` is in the same folder

### "No emails found"
- Increase `DAYS_BACK` value
- Remove or adjust `SUBJECT_KEYWORDS` filter

### "Rate limit exceeded"
- Gmail has daily sending limits (usually 500/day for free accounts)
- Increase the delay between sends in the code

### "Permission denied"
- Make sure you granted all permissions during OAuth flow
- Check that Gmail API is enabled in Google Cloud Console

---

## 🎯 Example Workflow

1. You sent 100 emails last week
2. Run the script in DRY RUN mode
3. See that 55 people didn't reply
4. Review the list to make sure it's correct
5. Switch to `DRY_RUN = False`
6. Run again to send 55 follow-ups
7. Follow-ups appear in the same email threads
8. Wait for responses!

---

## 📝 Notes

- **Threading**: Follow-ups are sent in the SAME thread as the original email (they'll see "Re: [Original Subject]")
- **Duplicate Protection**: The script checks for replies, so you won't send follow-ups to people who already responded
- **Customization**: You can modify the follow-up template to match your tone and needs

---

## 🆘 Need Help?

If you encounter issues:
1. Check the troubleshooting section above
2. Make sure all prerequisites are installed
3. Verify your `credentials.json` is correct
4. Check that Gmail API is enabled in your Google Cloud project

Good luck with your follow-ups! 🚀
