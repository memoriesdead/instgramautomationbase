# Commercial-Grade Email Automation Setup

## Overview
Automated IMAP-based email verification code retrieval for Instagram account creation.

## Setup Steps

### 1. Update accounts.csv
Add your email passwords to the CSV file:

```csv
first_name,last_name,email,password,email_password
Eveline,Ross,eveline.ross@pumplabsweb3.com,Welcome2025!,YOUR_ACTUAL_EMAIL_PASSWORD
John,Smith,john.smith@pumplabsweb3.com,SecurePass123!,YOUR_ACTUAL_EMAIL_PASSWORD
```

### 2. Verify IMAP Settings
Check that your email server settings in `email_config.py` are correct:

```python
'imap_server': '170.9.13.229',  # Your Oracle Cloud server
'imap_port': 993,  # SSL port (or 143 for non-SSL)
'use_ssl': True,  # SSL enabled
```

### 3. Test Email Connection (Optional but Recommended)
Run the email verifier test:

```bash
python email_verifier.py
```

Enter a test email and password to verify IMAP connection works.

### 4. Run the Automation
```bash
python create_from_spreadsheet.py
```

## How It Works

1. **Form Filling**: Script fills Instagram signup form automatically
2. **Code Retrieval**: Script connects to your email via IMAP
3. **Code Extraction**: Parses Instagram email for 6-digit code
4. **Auto-Complete**: Enters code and completes signup

## Features

✓ **Automatic IMAP connection** to your Oracle Cloud email server
✓ **Intelligent code parsing** with multiple regex patterns
✓ **Fallback to manual entry** if automation fails
✓ **Secure credential handling** from CSV file
✓ **Real-time status updates** showing progress
✓ **Retry logic** checks email every 5 seconds for up to 2 minutes

## Security Notes

- Keep `accounts.csv` and `email_config.py` secure
- Add to `.gitignore` to prevent committing passwords
- Use app-specific passwords if your email supports them
- Email passwords are only stored locally

## Troubleshooting

### "Connection refused" error
- Check IMAP port (993 for SSL, 143 for non-SSL)
- Verify firewall allows IMAP connections
- Confirm IMAP is enabled on your email server

### "Authentication failed" error
- Verify email password is correct
- Check if 2FA is enabled (may need app password)
- Confirm email address format is correct

### "No code found" timeout
- Email might be in spam/junk folder
- Instagram might be rate-limiting
- Email might take longer than 2 minutes to arrive
- Script will fall back to manual entry

## Advanced Configuration

Edit `email_config.py` to customize:

```python
'check_interval': 5,      # Seconds between email checks
'max_wait_time': 120,     # Maximum seconds to wait
'mark_as_read': True,     # Mark emails as read after retrieval
```

## Production Ready

This implementation is:
- Enterprise-grade IMAP client
- Robust error handling
- Automatic fallback mechanisms
- Detailed logging and status updates
- Tested with commercial email servers
