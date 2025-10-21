# AI Email Follow-up Agent

Automatically sends personalized follow-up emails to recipients who haven't replied, with AI-powered personalization using OpenAI GPT-4.

## Features

- 🤖 **AI-Powered**: Uses OpenAI GPT-4 for truly personalized follow-ups
- 📧 **Gmail Integration**: Seamlessly integrates with Gmail API
- 🎯 **Smart Detection**: Automatically detects emails that haven't received replies
- 🔍 **Keyword Filtering**: Filter emails by subject keywords (job applications, opportunities, etc.)
- 📝 **Template Fallback**: Works with template-based emails if API is unavailable
- 🧵 **Thread-Aware**: Sends follow-ups in the same email thread
- 🏃 **Dry-Run Mode**: Preview follow-ups before sending

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up Gmail API credentials (see [SETUP_GUIDE.md](SETUP_GUIDE.md))
4. Set up OpenAI API key (see [OPENAI_SETUP.md](OPENAI_SETUP.md))

## Quick Start

```python
from openai_email_followup_agent import OpenAIEmailFollowupAgent

# Initialize agent
agent = OpenAIEmailFollowupAgent(use_ai=True)

# Run follow-up campaign (dry-run by default)
agent.run_followup_campaign(
    days_ago=14,
    subject_keywords=['application', 'job', 'position'],
    dry_run=True,  # Set to False to actually send emails
    show_previews=True
)
```

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required for AI mode)

### Gmail Setup
- `credentials.json`: Your Gmail API credentials file

See [.env.example](.env.example) and [credentials.json.example](credentials.json.example) for templates.

## Usage

### Run with AI Generation (Recommended)
```bash
python openai_email_followup_agent.py
```

### Run with Template Mode
```bash
python email_followup_agent.py
```

## File Structure

- `openai_email_followup_agent.py` - **Main agent** with AI-powered personalization
- `email_followup_agent.py` - Basic version using templates
- `SETUP_GUIDE.md` - Gmail API setup instructions
- `OPENAI_SETUP.md` - OpenAI API setup instructions
- `requirements.txt` - Python dependencies

## Safety

- ✅ All credentials are environment-based, not hardcoded
- ✅ `.gitignore` prevents accidental credential leaks
- ✅ Dry-run mode for safe preview before sending
- ✅ Gmail limits prevent abuse

## License

MIT
