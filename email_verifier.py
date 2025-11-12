"""
Commercial-grade IMAP Email Verification Code Retriever
Automatically fetches Instagram verification codes from email
"""

import imaplib
import email
from email.header import decode_header
import re
import time
import socket
from datetime import datetime, timedelta

class EmailVerifier:
    def __init__(self, imap_server, imap_port, use_ssl=True, timeout=60):
        """Initialize email verifier with server details"""
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.use_ssl = use_ssl
        self.timeout = timeout
        self.imap = None

    def connect(self, email_address, password):
        """Connect to IMAP server with timeout and retries"""
        max_retries = 3
        retry_delay = 5

        for attempt in range(max_retries):
            try:
                print(f"Connecting to {self.imap_server}:{self.imap_port} (attempt {attempt + 1}/{max_retries})...")

                # Set socket timeout before creating connection
                socket.setdefaulttimeout(self.timeout)

                if self.use_ssl:
                    self.imap = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
                else:
                    self.imap = imaplib.IMAP4(self.imap_server, self.imap_port)

                # Set read timeout for subsequent operations
                self.imap.sock.settimeout(self.timeout)

                print(f"Logging in as {email_address}...")
                self.imap.login(email_address, password)
                print(f"✓ Connected to email server for {email_address}")
                return True

            except socket.timeout:
                print(f"✗ Connection timeout (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
            except Exception as e:
                print(f"✗ Connection failed: {e}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)

        print(f"✗ Failed to connect after {max_retries} attempts")
        return False

    def disconnect(self):
        """Disconnect from IMAP server"""
        try:
            if self.imap:
                self.imap.close()
                self.imap.logout()
        except:
            pass

    def get_verification_code(self, email_address, password, max_wait=180, check_interval=8):
        """
        Retrieve Instagram verification code from email

        Args:
            email_address: Email to check
            password: Email password
            max_wait: Maximum seconds to wait for email
            check_interval: Seconds between checks

        Returns:
            6-digit verification code or None
        """
        print(f"\n{'='*60}")
        print(f"Retrieving verification code for: {email_address}")
        print(f"{'='*60}")

        if not self.connect(email_address, password):
            return None

        start_time = time.time()
        attempts = 0

        while time.time() - start_time < max_wait:
            attempts += 1
            elapsed = int(time.time() - start_time)
            print(f"Attempt {attempts} (elapsed: {elapsed}s / {max_wait}s)...")

            try:
                # Select inbox (with small delay for server)
                time.sleep(0.5)
                self.imap.select('INBOX')

                # Search for recent Instagram emails
                # Look for emails from the last 5 minutes
                date = (datetime.now() - timedelta(minutes=5)).strftime("%d-%b-%Y")

                # Search for Instagram emails (with small delay)
                time.sleep(0.5)
                status, messages = self.imap.search(None, f'(FROM "instagram" SINCE {date})')

                if status != 'OK':
                    print("  No new emails found")
                    time.sleep(check_interval)
                    continue

                email_ids = messages[0].split()

                if not email_ids:
                    print("  No Instagram emails found, waiting...")
                    time.sleep(check_interval)
                    continue

                # Check emails from newest to oldest
                for email_id in reversed(email_ids):
                    # Fetch the email (with small delay between fetches)
                    time.sleep(0.3)
                    status, msg_data = self.imap.fetch(email_id, '(RFC822)')

                    if status != 'OK':
                        continue

                    # Parse email
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)

                    # Get email subject and sender
                    subject = self.decode_subject(email_message['Subject'])
                    sender = email_message['From']

                    print(f"  Checking email from: {sender}")
                    print(f"  Subject: {subject}")

                    # Filter: Only process Instagram emails
                    if not self.is_instagram_email(sender, subject):
                        print(f"  ⊗ Skipping - not an Instagram verification email")
                        continue

                    # Extract verification code
                    code = self.extract_code_from_email(email_message)

                    if code:
                        print(f"\n{'='*60}")
                        print(f"✓ Instagram verification code found: {code}")
                        print(f"{'='*60}\n")
                        self.disconnect()
                        return code

                print(f"  No code found in recent emails, retrying in {check_interval}s...")
                time.sleep(check_interval)

            except Exception as e:
                print(f"  Error checking email: {e}")
                time.sleep(check_interval)

        print(f"\n✗ Timeout: No verification code found after {max_wait} seconds")
        self.disconnect()
        return None

    def is_instagram_email(self, sender, subject):
        """
        Check if email is from Instagram and is a verification code email

        Args:
            sender: Email sender address
            subject: Email subject line

        Returns:
            True if this is an Instagram verification email, False otherwise
        """
        if sender is None or subject is None:
            return False

        sender_lower = sender.lower()
        subject_lower = subject.lower()

        # Check if sender is from Instagram
        instagram_domains = [
            'instagram.com',
            'mail.instagram.com',
            'facebookmail.com',  # Instagram sometimes sends from Facebook domain
        ]

        is_from_instagram = any(domain in sender_lower for domain in instagram_domains)

        if not is_from_instagram:
            return False

        # Check if subject contains verification/confirmation keywords
        verification_keywords = [
            'confirmation code',
            'verify',
            'verification',
            'security code',
            'instagram code',
            'confirm your',
        ]

        is_verification_email = any(keyword in subject_lower for keyword in verification_keywords)

        return is_verification_email

    def decode_subject(self, subject):
        """Decode email subject"""
        if subject is None:
            return ""

        decoded_parts = decode_header(subject)
        subject_str = ""

        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                subject_str += part.decode(encoding or 'utf-8')
            else:
                subject_str += part

        return subject_str

    def extract_code_from_email(self, email_message):
        """
        Extract 6-digit Instagram verification code from email

        Instagram codes are typically 6 digits and appear in patterns like:
        - "123456 is your Instagram code"
        - "Your code is 123456"
        - "confirmation code we sent to... 123456"
        """
        # Get email body
        body = self.get_email_body(email_message)

        if not body:
            print("  ⚠ Could not extract email body")
            return None

        # Pattern 1: "123456 is your Instagram code" (most common)
        match = re.search(r'(\d{6})\s+is your Instagram code', body, re.IGNORECASE)
        if match:
            print(f"  ✓ Found code using pattern 1: 'XXX is your Instagram code'")
            return match.group(1)

        # Pattern 2: "confirmation code we sent to... 123456"
        match = re.search(r'confirmation code we sent[^0-9]*(\d{6})', body, re.IGNORECASE)
        if match:
            print(f"  ✓ Found code using pattern 2: 'confirmation code we sent'")
            return match.group(1)

        # Pattern 3: "Your Instagram code is 123456"
        match = re.search(r'Instagram code is[:\s]+(\d{6})', body, re.IGNORECASE)
        if match:
            print(f"  ✓ Found code using pattern 3: 'Instagram code is'")
            return match.group(1)

        # Pattern 4: "code: 123456" or "code 123456"
        match = re.search(r'(?:code|verify)[:\s]+(\d{6})', body, re.IGNORECASE)
        if match:
            print(f"  ✓ Found code using pattern 4: 'code: XXX'")
            return match.group(1)

        # Pattern 5: Look for 6-digit numbers near Instagram keywords
        # This is more targeted than just any 6-digit number
        instagram_context = re.search(r'Instagram[^0-9]{0,50}(\d{6})', body, re.IGNORECASE)
        if instagram_context:
            print(f"  ✓ Found code using pattern 5: near 'Instagram' keyword")
            return instagram_context.group(1)

        # Pattern 6: Fallback - any 6-digit number (only if from verified Instagram email)
        matches = re.findall(r'\b(\d{6})\b', body)
        if matches:
            print(f"  ✓ Found code using pattern 6: first 6-digit number")
            return matches[0]

        print("  ✗ No 6-digit code found in email body")
        return None

    def get_email_body(self, email_message):
        """Extract text body from email message"""
        body = ""

        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                if "attachment" in content_disposition:
                    continue

                if content_type == "text/plain":
                    try:
                        body += part.get_payload(decode=True).decode()
                    except:
                        pass
                elif content_type == "text/html":
                    try:
                        html_body = part.get_payload(decode=True).decode()
                        # Simple HTML tag removal
                        body += re.sub('<[^<]+?>', '', html_body)
                    except:
                        pass
        else:
            try:
                body = email_message.get_payload(decode=True).decode()
            except:
                pass

        return body


def get_instagram_verification_code(email_address, password, imap_server='170.9.13.229',
                                    imap_port=993, use_ssl=True, max_wait=180, timeout=60):
    """
    Convenience function to get Instagram verification code

    Args:
        email_address: Email to check
        password: Email password
        imap_server: IMAP server address
        imap_port: IMAP port
        use_ssl: Use SSL connection
        max_wait: Maximum seconds to wait for email
        timeout: Socket timeout for connection (seconds)

    Returns:
        6-digit verification code or None
    """
    verifier = EmailVerifier(imap_server, imap_port, use_ssl, timeout=timeout)
    return verifier.get_verification_code(email_address, password, max_wait)


if __name__ == "__main__":
    # Test the email verifier
    print("Email Verification Code Retriever - Test Mode")
    print("="*60)

    test_email = input("Enter email address to test: ")
    test_password = input("Enter email password: ")

    code = get_instagram_verification_code(test_email, test_password, max_wait=60)

    if code:
        print(f"\n✓ SUCCESS: Code retrieved: {code}")
    else:
        print("\n✗ FAILED: Could not retrieve code")
