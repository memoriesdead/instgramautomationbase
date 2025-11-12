"""
Script to create Instagram accounts from a CSV spreadsheet
The spreadsheet should have columns: first_name, last_name, email, password, email_password
"""

import csv
import sys
from time import sleep
from instabot import instaBot
import first
from setup_logging import setup_logging

# Setup logging
logger, log_file = setup_logging()

# Import and configure email automation
try:
    from email_config import EMAIL_CONFIG
    EMAIL_CONFIGURED = True
    logger.info("✓ Email configuration module loaded")
except:
    EMAIL_CONFIGURED = False
    logger.warning("✗ Email configuration not available")

def read_accounts_from_csv(filename='accounts.csv'):
    """Read account data from CSV file"""
    logger.info(f"Reading accounts from {filename}...")
    accounts = []
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Ensure status field exists
                if 'status' not in row:
                    row['status'] = 'pending'
                if 'created_date' not in row:
                    row['created_date'] = ''
                if 'username' not in row:
                    row['username'] = ''
                accounts.append(row)
                logger.debug(f"Loaded account: {row['email']} - Status: {row.get('status', 'pending')}")

        # Filter out already created accounts
        pending_accounts = [acc for acc in accounts if acc.get('status', 'pending').lower() != 'created']
        skipped_count = len(accounts) - len(pending_accounts)

        if skipped_count > 0:
            logger.info(f"ℹ Skipping {skipped_count} already created account(s)")

        logger.info(f"✓ Successfully loaded {len(pending_accounts)} pending accounts (Total: {len(accounts)})")
        return pending_accounts
    except FileNotFoundError:
        logger.error(f"✗ Error: {filename} not found!")
        logger.error("Please create a CSV file with columns: first_name, last_name, email, password, email_password")
        sys.exit(1)
    except Exception as e:
        logger.error(f"✗ Error reading CSV: {e}")
        sys.exit(1)

def update_account_status(filename, email, status, username='', created_date=''):
    """Update account status in CSV file"""
    from datetime import datetime
    import tempfile
    import shutil

    if not created_date:
        created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        # Read all rows
        rows = []
        with open(filename, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames
            for row in reader:
                if row['email'] == email:
                    row['status'] = status
                    row['created_date'] = created_date
                    if username:
                        row['username'] = username
                    logger.info(f"✓ Marked {email} as '{status}'")
                rows.append(row)

        # Write back to file
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        return True
    except Exception as e:
        logger.error(f"✗ Failed to update status for {email}: {e}")
        return False

def create_accounts_from_spreadsheet():
    """Main function to create accounts from spreadsheet"""

    # Read accounts from CSV
    accounts = read_accounts_from_csv('accounts.csv')

    # Configure email credentials if email automation is available
    if EMAIL_CONFIGURED:
        for account in accounts:
            if 'email_password' in account and account['email_password'] != 'YOUR_EMAIL_PASSWORD_HERE':
                EMAIL_CONFIG['credentials'][account['email']] = account['email_password']
                logger.debug(f"Configured email credentials for {account['email']}")
        logger.info(f"✓ Email automation configured for {len(EMAIL_CONFIG['credentials'])} account(s)")

    if not accounts:
        logger.error("✗ No accounts found in the spreadsheet!")
        sys.exit(1)

    logger.info(f"\nFound {len(accounts)} account(s) in the spreadsheet:")
    for i, account in enumerate(accounts, 1):
        logger.info(f"{i}. {account['first_name']} {account['last_name']} - {account['email']}")

    # Automatically process all accounts
    accounts_to_create = accounts
    logger.info(f"\nAutomatically creating all {len(accounts_to_create)} account(s)...\n")

    # Create each account
    for i, account_data in enumerate(accounts_to_create, 1):
        logger.info(f"\n{'='*60}")
        logger.info(f"Creating account {i}/{len(accounts_to_create)}")
        logger.info(f"Name: {account_data['first_name']} {account_data['last_name']}")
        logger.info(f"Email: {account_data['email']}")
        logger.info(f"{'='*60}\n")

        try:
            logger.debug(f"Initializing bot for {account_data['email']}")
            # Create bot instance with account data
            bot = instaBot(account_data=account_data)

            # Get properties and driver
            properties = bot.get_properties()
            driver = bot.return_driver()
            logger.debug("Bot initialized successfully")

            # Skip post-creation actions for now (first.main)
            # The account is already created successfully at this point
            logger.info("Account creation completed - skipping optional post-creation actions")

            # Close the driver
            driver.quit()
            logger.debug("Browser closed")

            logger.info(f"\n✓ Account created successfully for {account_data['email']}")

            # Mark account as created in CSV - use the actual username from the bot
            username = bot.username  # Get the final accepted username (may have been retried)
            logger.info(f"Final username: {username}")
            update_account_status('accounts.csv', account_data['email'], 'created', username)

            # Wait between accounts to avoid detection
            if i < len(accounts_to_create):
                wait_time = 30
                logger.info(f"\nWaiting {wait_time} seconds before creating next account...")
                sleep(wait_time)

        except Exception as e:
            logger.error(f"\n✗ Error creating account for {account_data['email']}: {e}", exc_info=True)

            # Mark account as failed in CSV
            update_account_status('accounts.csv', account_data['email'], 'failed')

            logger.info("Automatically continuing with next account...")
            # Close browser if it's open
            try:
                if 'driver' in locals():
                    driver.quit()
            except:
                pass
            # Continue to next account automatically
            continue

    logger.info("\n" + "="*60)
    logger.info("Account creation process completed!")
    logger.info(f"Check log file for details: {log_file}")
    logger.info("="*60)

if __name__ == "__main__":
    create_accounts_from_spreadsheet()
