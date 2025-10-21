"""
AI Email Follow-up Agent - Powered by OpenAI GPT-4
Generates truly personalized follow-ups based on original email context
Automatically sends follow-up emails to recipients who haven't replied
"""

import os
import base64
import time
import re
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
from openai import OpenAI

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Get OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

class OpenAIEmailFollowupAgent:
    def __init__(self, use_ai=True):
        self.service = None
        self.use_ai = use_ai and OPENAI_API_KEY
        
        if self.use_ai:
            self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
            print("✓ AI mode enabled (OpenAI GPT-4)")
        else:
            print("⚠️  AI mode disabled (using templates)")
            if not OPENAI_API_KEY:
                print("   Set OPENAI_API_KEY to enable AI generation")
        
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Gmail API"""
        creds = None
        
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
        print("✓ Successfully authenticated with Gmail")
    
    def extract_name_from_email(self, email_address):
        """Extract name from email address"""
        name_match = re.search(r'^([^<]+)<', email_address)
        if name_match:
            name = name_match.group(1).strip()
            name = name.replace('"', '').replace("'", '')
            return name
        
        email_parts = email_address.split('@')[0]
        name_parts = re.split(r'[._-]', email_parts)
        name = ' '.join([part.capitalize() for part in name_parts if len(part) > 1])
        
        return name if name else None
    
    def get_email_body(self, message):
        """Extract email body text from message"""
        try:
            if 'parts' in message['payload']:
                parts = message['payload']['parts']
                for part in parts:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data', '')
                        if data:
                            return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    elif part['mimeType'] == 'text/html':
                        data = part['body'].get('data', '')
                        if data:
                            html = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                            text = re.sub('<[^<]+?>', '', html)
                            return text
            else:
                data = message['payload']['body'].get('data', '')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        except Exception as e:
            pass
        
        return ""
    
    def find_sent_emails(self, days_ago=7, subject_keywords=None):
        """Find emails you sent"""
        print(f"\n🔍 Searching for emails sent in the last {days_ago} days...")
        
        date_filter = (datetime.now() - timedelta(days=days_ago)).strftime('%Y/%m/%d')
        query = f'in:sent after:{date_filter}'
        
        if subject_keywords:
            keyword_query = ' OR '.join([f'subject:{kw}' for kw in subject_keywords])
            query += f' ({keyword_query})'
        
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=500
            ).execute()
            
            messages = results.get('messages', [])
            print(f"✓ Found {len(messages)} sent emails")
            return messages
        
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def check_for_reply(self, thread_id, original_msg_id):
        """Check if thread has replies"""
        try:
            thread = self.service.users().threads().get(
                userId='me',
                id=thread_id
            ).execute()
            
            messages = thread.get('messages', [])
            
            original_timestamp = None
            for msg in messages:
                if msg['id'] == original_msg_id:
                    original_timestamp = int(msg['internalDate'])
                    break
            
            if not original_timestamp:
                return False
            
            for msg in messages:
                msg_timestamp = int(msg['internalDate'])
                if msg_timestamp > original_timestamp:
                    headers = msg['payload']['headers']
                    from_header = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
                    
                    if 'me' not in from_header.lower():
                        return True
            
            return False
        except:
            return False
    
    def get_email_details(self, message_id):
        """Get detailed email information"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            headers = message['payload']['headers']
            
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            to = next((h['value'] for h in headers if h['name'].lower() == 'to'), '')
            thread_id = message['threadId']
            
            body = self.get_email_body(message)
            
            recipient_name = self.extract_name_from_email(to)
            recipient_email = to.split('<')[-1].replace('>', '').strip() if '<' in to else to.strip()
            
            return {
                'id': message_id,
                'thread_id': thread_id,
                'subject': subject,
                'to': to,
                'recipient_name': recipient_name,
                'recipient_email': recipient_email,
                'body': body[:1000],
                'snippet': message.get('snippet', ''),
            }
        
        except Exception as e:
            return None
    
    def generate_ai_followup(self, recipient_name, subject, original_body):
        """Generate personalized follow-up using OpenAI GPT-4"""
        
        first_name = recipient_name.split()[0] if recipient_name and ' ' in recipient_name else recipient_name
        
        prompt = f"""You are helping write a professional follow-up email. 

Original email details:
- Recipient: {recipient_name or "Unknown"}
- Subject: {subject}
- Original message preview: {original_body[:500]}

Requirements:
1. Write a natural, warm follow-up email
2. Use the recipient's first name ({first_name}) if available, otherwise use "Hi,"
3. DO NOT use the word "follow-up" or "following up" 
4. Reference the original topic naturally
5. Keep it brief (3-4 sentences max)
6. Sound genuine and human, not robotic
7. End with a simple question or call to action
8. Don't include a signature (I'll add that)
9. Make it sound like a natural second email, not a reminder

Write ONLY the email body, nothing else."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # Using GPT-4o (fastest and most cost-effective)
                messages=[
                    {"role": "system", "content": "You are an expert at writing natural, personalized professional emails."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.8
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"  ⚠️  AI generation failed, using template: {e}")
            return self.generate_template_followup(recipient_name, subject, original_body)
    
    def generate_template_followup(self, recipient_name, subject, original_body):
        """Fallback template-based follow-up"""
        
        first_name = recipient_name.split()[0] if recipient_name and ' ' in recipient_name else recipient_name
        greeting = f"Hi {first_name}," if first_name else "Hi,"
        
        is_job = any(word in subject.lower() for word in ['application', 'position', 'job', 'role'])
        
        if is_job:
            return f"""{greeting}

I hope this email finds you well. I wanted to reach out regarding the position I applied for recently.

I'm still very interested in this opportunity and would love to discuss how I can contribute to your team.

Would you have time for a brief conversation?"""
        else:
            return f"""{greeting}

I hope you're doing well. I wanted to touch base on my previous email.

I'd really appreciate the chance to discuss this further when you have a moment.

Are you available for a quick chat?"""
    
    def generate_personalized_followup(self, recipient_name, subject, original_body):
        """Generate personalized follow-up (AI or template)"""
        if self.use_ai:
            return self.generate_ai_followup(recipient_name, subject, original_body)
        else:
            return self.generate_template_followup(recipient_name, subject, original_body)
    
    def create_followup_message(self, email_details, thread_id):
        """Create follow-up message"""
        body = self.generate_personalized_followup(
            email_details['recipient_name'],
            email_details['subject'],
            email_details['body']
        )
        
        message = MIMEText(body)
        message['to'] = email_details['to']
        
        subject = email_details['subject']
        if not subject.startswith('Re:'):
            subject = f'Re: {subject}'
        message['subject'] = subject
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        return {
            'raw': raw_message,
            'threadId': thread_id
        }
    
    def send_followup(self, email_details):
        """Send follow-up email"""
        try:
            message = self.create_followup_message(email_details, email_details['thread_id'])
            
            sent_message = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            
            display_name = email_details['recipient_name'] or email_details['recipient_email']
            print(f"  ✓ Sent to {display_name}")
            return True
        
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            return False
    
    def preview_followup(self, email_details):
        """Preview the follow-up"""
        body = self.generate_personalized_followup(
            email_details['recipient_name'],
            email_details['subject'],
            email_details['body']
        )
        
        print("\n" + "="*70)
        print(f"To: {email_details['recipient_name'] or email_details['recipient_email']}")
        print(f"Email: {email_details['recipient_email']}")
        subject = email_details['subject']
        if not subject.startswith('Re:'):
            subject = f'Re: {subject}'
        print(f"Subject: {subject}")
        print("-"*70)
        print(body)
        print("="*70)
    
    def run_followup_campaign(self, days_ago=7, subject_keywords=None, dry_run=True, show_previews=False):
        """Run the campaign"""
        print("="*70)
        print(f"🤖 AI EMAIL FOLLOW-UP AGENT {'(OPENAI GPT-4)' if self.use_ai else '(TEMPLATE MODE)'}")
        print("="*70)
        
        sent_messages = self.find_sent_emails(days_ago, subject_keywords)
        
        if not sent_messages:
            print("\n⚠️  No emails found")
            return
        
        total_emails = len(sent_messages)
        needs_followup = []
        already_replied = []
        
        print(f"\n📊 Analyzing {total_emails} emails...\n")
        
        for idx, msg in enumerate(sent_messages, 1):
            msg_id = msg['id']
            details = self.get_email_details(msg_id)
            
            if not details:
                continue
            
            display_name = details['recipient_name'] or details['recipient_email']
            print(f"[{idx}/{total_emails}] {display_name[:40]}...")
            
            has_reply = self.check_for_reply(details['thread_id'], msg_id)
            
            if has_reply:
                already_replied.append(details)
                print(f"  ✓ Replied - skip")
            else:
                needs_followup.append(details)
                print(f"  ⚠️  No reply - needs email")
            
            time.sleep(0.5)
        
        print("\n" + "="*70)
        print("📊 SUMMARY")
        print("="*70)
        print(f"Total: {total_emails} | Replied: {len(already_replied)} | Need follow-up: {len(needs_followup)}")
        print("="*70)
        
        if show_previews and needs_followup:
            print("\n📧 SAMPLE PERSONALIZED EMAILS:")
            for i, email in enumerate(needs_followup[:3], 1):
                print(f"\n--- Sample {i} ---")
                self.preview_followup(email)
            
            if len(needs_followup) > 3:
                print(f"\n... and {len(needs_followup) - 3} more")
        
        if needs_followup:
            print(f"\n📤 {'[DRY RUN]' if dry_run else 'SENDING'} {len(needs_followup)} emails...\n")
            
            for idx, email in enumerate(needs_followup, 1):
                display_name = email['recipient_name'] or email['recipient_email']
                print(f"[{idx}/{len(needs_followup)}] {display_name}")
                
                if not dry_run:
                    self.send_followup(email)
                    time.sleep(2)
                else:
                    print(f"  [DRY RUN] Would send")
        
        print("\n✅ Complete!")
        
        if dry_run:
            print("\n⚠️  DRY RUN - no emails sent")
            print("💡 Set DRY_RUN=False to send")


def main():
    """Main execution"""
    
    # Initialize agent (set use_ai=False to disable OpenAI API)
    agent = OpenAIEmailFollowupAgent(use_ai=True)
    
    # Configuration
    DAYS_BACK = 14
    SUBJECT_KEYWORDS = ['application', 'opportunity', 'position', 'job', 'resume']
    DRY_RUN = True
    SHOW_PREVIEWS = True
    
    print("\n⚙️  Settings:")
    print(f"   Days: {DAYS_BACK}")
    print(f"   Keywords: {SUBJECT_KEYWORDS if SUBJECT_KEYWORDS else 'All'}")
    print(f"   Dry run: {DRY_RUN}")
    print(f"   Previews: {SHOW_PREVIEWS}")
    
    agent.run_followup_campaign(
        days_ago=DAYS_BACK,
        subject_keywords=SUBJECT_KEYWORDS,
        dry_run=DRY_RUN,
        show_previews=SHOW_PREVIEWS
    )


if __name__ == "__main__":
    main()
