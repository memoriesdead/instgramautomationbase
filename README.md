# Instagram Automation Base

🤖 **Commercial-grade Instagram account creation automation with IMAP email verification**

## Features

✅ **Fully Automated Account Creation**
- CSV-based bulk account creation
- Automatic form filling and submission
- Smart birthday selection
- IMAP email verification (auto-retrieves codes)

✅ **Smart Email Verification**
- Connects to any IMAP email server
- Filters specifically for Instagram emails
- 6 intelligent code extraction patterns
- Works with shared/work email accounts

✅ **Status Tracking**
- Tracks created/pending/failed accounts
- Never creates duplicates
- Timestamps and username logging
- Resume capability after interruption

✅ **Production Ready**
- Comprehensive error handling
- Detailed logging system
- Multiple fallback methods
- Works with Chrome + ChromeDriver

## Quick Start

```bash
# 1. Install dependencies
pip install selenium

# 2. Configure email settings in email_config.py
# 3. Add accounts to accounts.csv
# 4. Run automation
python create_from_spreadsheet.py
```

## Configuration

Create `email_config.py`:
```python
EMAIL_CONFIG = {
    'imap_server': 'your.server.com',
    'imap_port': 993,
    'use_ssl': True,
    'credentials': {},
}
```

Create `accounts.csv`:
```csv
first_name,last_name,email,password,email_password,status,created_date,username
John,Doe,john@example.com,Pass123!,EmailPass!,pending,,
```

## How It Works

1. Reads pending accounts from CSV
2. Opens Chrome browser
3. Fills Instagram signup form
4. Selects birthday automatically
5. Connects to email via IMAP
6. Retrieves verification code
7. Submits and completes signup
8. Updates CSV with status
9. Repeats for next account

## File Structure

- `create_from_spreadsheet.py` - Main script
- `instabot.py` - Instagram bot core
- `email_verifier.py` - IMAP email automation
- `setup_logging.py` - Logging system
- `accounts.csv` - Account database

## Security

⚠️ **Never commit sensitive files:**
- `accounts.csv` (passwords)
- `email_config.py` (credentials)
- `*.log` files

These are excluded in `.gitignore`

## Requirements

- Python 3.7+
- Google Chrome 142+
- IMAP email access
- Windows/Linux/macOS

## License

For educational and authorized use only.

---

**Built with commercial-grade automation practices**
