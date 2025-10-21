"""
AI Email Follow-up Agent - Basic Template Version
Automatically sends follow-up emails to recipients who haven't replied
Sends follow-ups in the same email thread

For AI-powered personalization, use openai_email_followup_agent.py instead.
"""

import os
import base64
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


class EmailFollowupAgent:
    def __init__(self):
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Gmail API"""
        creds = None
        
        # Token file stores the user's access and refresh tokens
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no valid credentials, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
        print("✓ Successfully authenticated with Gmail")
    
    def find_sent_emails(self, days_ago=7, subject_keywords=None):
        """
        Find emails you sent in the last N days
        
        Args:
            days_ago: How many days back to search (default: 7)
            subject_keywords: List of keywords to filter subjects (optional)
        """
        print(f"\n🔍 Searching for emails sent in the last {days_ago} days...")
        
        # Calculate the date for the query
        date_filter = (datetime.now() - timedelta(days=days_ago)).strftime('%Y/%m/%d')
        
        # Build query
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
            print(f"❌ Error finding sent emails: {e}")
            return []
    
    def check_for_reply(self, thread_id, original_msg_id):
        """
        Check if a thread has replies after the original message
        
        Args:
            thread_id: Gmail thread ID
            original_msg_id: The ID of your original sent message
        """
        try:
            thread = self.service.users().threads().get(
                userId='me',
                id=thread_id
            ).execute()
            
            messages = thread.get('messages', [])
            
            # Find the original message timestamp
            original_timestamp = None
            for msg in messages:
                if msg['id'] == original_msg_id:
                    original_timestamp = int(msg['internalDate'])
                    break
            
            if not original_timestamp:
                return False
            
            # Check if there are any messages after the original
            for msg in messages:
                msg_timestamp = int(msg['internalDate'])
                # If message is after original and not from us
                if msg_timestamp > original_timestamp:
                    headers = msg['payload']['headers']
                    from_header = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
                    
                    # Check if it's not from us (they replied)
                    if 'me' not in from_header.lower():
                        return True
            
            return False
        
        except Exception as e:
            print(f"❌ Error checking for reply: {e}")
            return False
    
    def get_email_details(self, message_id):
        """Get details of an email message"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            headers = message['payload']['headers']
            
            # Extract relevant headers
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            to = next((h['value'] for h in headers if h['name'].lower() == 'to'), '')
            thread_id = message['threadId']
            
            return {
                'id': message_id,
                'thread_id': thread_id,
                'subject': subject,
                'to': to,
                'snippet': message.get('snippet', ''),
            }
        
        except Exception as e:
            print(f"❌ Error getting email details: {e}")
            return None
    
    def create_followup_message(self, to, subject, thread_id, original_subject, recipient_name=None):
        """
        Create a follow-up email message
        
        Args:
            to: Recipient email address
            subject: Email subject (should match original for threading)
            thread_id: Gmail thread ID to continue the conversation
            original_subject: Original email subject for reference
            recipient_name: Name of recipient (optional)
        """
        # Personalize greeting
        greeting = f"Hi {recipient_name}," if recipient_name else "Hi,"
        
        # Follow-up email body
        body = f"""{greeting}

I wanted to follow up on my previous email regarding {original_subject.replace('Re: ', '').replace('Fwd: ', '')}.

I understand you're likely busy, but I wanted to reach out again as I'm very interested in exploring potential opportunities with your organization.

Could you spare a few minutes to discuss this further? I'm happy to work around your schedule.

Looking forward to hearing from you.

Best regards"""

        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject if subject.startswith('Re:') else f'Re: {subject}'
        
        # Encode the message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        return {
            'raw': raw_message,
            'threadId': thread_id
        }
    
    def send_followup(self, to, subject, thread_id, original_subject):
        """Send a follow-up email in the same thread"""
        try:
            # Create the follow-up message
            message = self.create_followup_message(to, subject, thread_id, original_subject)
            
            # Send the message
            sent_message = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            
            print(f"  ✓ Sent follow-up to {to}")
            return True
        
        except Exception as e:
            print(f"  ❌ Failed to send follow-up to {to}: {e}")
            return False
    
    def run_followup_campaign(self, days_ago=7, subject_keywords=None, dry_run=True):
        """
        Main function to run the follow-up campaign
        
        Args:
            days_ago: How many days back to search for sent emails
            subject_keywords: Filter emails by subject keywords
            dry_run: If True, only show what would be sent without actually sending
        """
        print("="*60)
        print("📧 EMAIL FOLLOW-UP AGENT")
        print("="*60)
        
        # Find sent emails
        sent_messages = self.find_sent_emails(days_ago, subject_keywords)
        
        if not sent_messages:
            print("\n⚠️  No sent emails found matching your criteria")
            return
        
        # Track statistics
        total_emails = len(sent_messages)
        needs_followup = []
        already_replied = []
        
        print(f"\n📊 Analyzing {total_emails} emails for replies...\n")
        
        # Check each email for replies
        for idx, msg in enumerate(sent_messages, 1):
            msg_id = msg['id']
            details = self.get_email_details(msg_id)
            
            if not details:
                continue
            
            print(f"[{idx}/{total_emails}] Checking: {details['to'][:50]}...")
            
            # Check if they replied
            has_reply = self.check_for_reply(details['thread_id'], msg_id)
            
            if has_reply:
                already_replied.append(details)
                print(f"  ✓ Already replied - skipping")
            else:
                needs_followup.append(details)
                print(f"  ⚠️  No reply - needs follow-up")
            
            # Small delay to avoid rate limits
            time.sleep(0.5)
        
        # Summary
        print("\n" + "="*60)
        print("📊 SUMMARY")
        print("="*60)
        print(f"Total emails analyzed: {total_emails}")
        print(f"Already replied: {len(already_replied)}")
        print(f"Need follow-up: {len(needs_followup)}")
        print("="*60)
        
        # Send follow-ups
        if needs_followup:
            print(f"\n📤 {'[DRY RUN] Would send' if dry_run else 'Sending'} {len(needs_followup)} follow-up emails...\n")
            
            for idx, email in enumerate(needs_followup, 1):
                print(f"[{idx}/{len(needs_followup)}] {email['to']}")
                
                if not dry_run:
                    self.send_followup(
                        email['to'],
                        email['subject'],
                        email['thread_id'],
                        email['subject']
                    )
                    # Rate limiting - wait 2 seconds between sends
                    time.sleep(2)
                else:
                    print(f"  [DRY RUN] Would send follow-up")
        
        print("\n✅ Follow-up campaign complete!")
        
        if dry_run:
            print("\n⚠️  This was a DRY RUN - no emails were actually sent")
            print("Run with dry_run=False to send actual follow-ups")


def main():
    """Main execution function"""
    
    # Initialize the agent
    agent = EmailFollowupAgent()
    
    # Configuration
    DAYS_BACK = 14  # Look for emails sent in the last 14 days
    SUBJECT_KEYWORDS = ['application', 'opportunity', 'position', 'job', 'resume']  # Filter by these keywords (optional)
    DRY_RUN = True  # Set to False to actually send emails
    
    print("\n⚙️  Configuration:")
    print(f"   Days back: {DAYS_BACK}")
    print(f"   Subject keywords: {SUBJECT_KEYWORDS if SUBJECT_KEYWORDS else 'None (all emails)'}")
    print(f"   Dry run: {DRY_RUN}")
    
    # Run the campaign
    agent.run_followup_campaign(
        days_ago=DAYS_BACK,
        subject_keywords=SUBJECT_KEYWORDS,
        dry_run=DRY_RUN
    )


if __name__ == "__main__":
    main()
