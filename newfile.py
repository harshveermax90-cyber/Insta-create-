import os
import random
import string
import time
import logging
import threading
import json
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

print("🚀 Starting REAL Instagram Account Creator...")

# Keep alive server for 24/7 operation
app = Flask('')

@app.route('/')
def home():
    return """
🤖 Instagram Bot is Running 24/7! 
✅ Bot Status: ACTIVE
⏰ Server Time: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """
🔗 Use Telegram: @YourBotName
📊 Ready for account creation
"""

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# Start keep-alive immediately
keep_alive()
print("✅ 24/7 Keep-alive server started on port 8080!")

# Bot configuration
BOT_TOKEN = "8100070394:AAE5Pov3SnkoV4It9Az2OE7_q3It36mEl50"
ADMIN_USER_ID = 6716174520

# Conversation states
ACCOUNT_COUNT, PASSWORD = range(2)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealInstagramCreator:
    def __init__(self):
        self.created_accounts = []
        self.is_running = False
        self.common_password = ""
        self.current_user_id = None
        self.accounts_file = "real_instagram_accounts.json"
        self.user_limits = {}
        self.load_accounts()
        
        # Working email domains
        self.email_domains = [
            "gmail.com", "yahoo.com", "outlook.com", "hotmail.com"
        ]
    
    def load_accounts(self):
        try:
            if os.path.exists(self.accounts_file):
                with open(self.accounts_file, 'r') as f:
                    self.created_accounts = json.load(f)
                print(f"📂 Loaded {len(self.created_accounts)} real accounts")
        except Exception as e:
            print(f"Note: No existing accounts file found - {e}")
            self.created_accounts = []
    
    def save_accounts(self):
        try:
            with open(self.accounts_file, 'w') as f:
                json.dump(self.created_accounts, f, indent=2)
            print(f"💾 Saved {len(self.created_accounts)} accounts to file")
        except Exception as e:
            print(f"Save error: {e}")

    def generate_username(self):
        """Generate unique username"""
        used_usernames = [acc['username'] for acc in self.created_accounts]
        while True:
            patterns = [
                lambda: ''.join(random.choice(string.ascii_lowercase) for _ in range(8)),
                lambda: ''.join(random.choice(string.ascii_lowercase) for _ in range(6)) + str(random.randint(10, 999)),
                lambda: 'user' + str(random.randint(1000, 99999)),
            ]
            username = random.choice(patterns)()
            if username not in used_usernames:
                return username

    def get_email_domain(self):
        return random.choice(self.email_domains)

    def setup_chrome_driver(self):
        """Setup Chrome driver for Render"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Render-optimized Chrome setup
            chrome_options.binary_location = os.environ.get('CHROME_BIN', '/usr/bin/google-chrome')
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            print("✅ Chrome driver setup successful")
            return driver
        except Exception as e:
            logger.error(f"Chrome setup failed: {e}")
            return None

    def create_real_instagram_account(self, email, username, password):
        """Create REAL Instagram account using Selenium"""
        driver = None
        try:
            print(f"🔄 Attempting REAL Instagram creation: {username}")
            
            driver = self.setup_chrome_driver()
            if not driver:
                return None

            driver.get("https://www.instagram.com/accounts/emailsignup/")
            time.sleep(5)

            wait = WebDriverWait(driver, 20)

            try:
                # Fill email field
                email_field = wait.until(EC.presence_of_element_located((By.NAME, "emailOrPhone")))
                email_field.clear()
                email_field.send_keys(email)
                time.sleep(2)

                # Fill full name
                fullname_field = driver.find_element(By.NAME, "fullName")
                fullname_field.clear()
                fullname_field.send_keys(f"User {username}")
                time.sleep(2)

                # Fill username
                username_field = driver.find_element(By.NAME, "username")
                username_field.clear()
                username_field.send_keys(username)
                time.sleep(2)

                # Fill password
                password_field = driver.find_element(By.NAME, "password")
                password_field.clear()
                password_field.send_keys(password)
                time.sleep(3)

                # Click signup button
                signup_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Sign up')]")
                signup_button.click()
                time.sleep(8)

                # Check if account was created
                current_url = driver.current_url
                page_source = driver.page_source.lower()

                if "challenge" in current_url or "confirm" in current_url:
                    account_data = {
                        'username': username,
                        'password': password,
                        'email': email,
                        'status': 'REAL_ACCOUNT_CREATED',
                        'created_at': datetime.now().isoformat(),
                        'user_id': self.current_user_id,
                        'instagram_url': f'https://instagram.com/{username}',
                        'login_url': 'https://instagram.com/accounts/login/',
                        'verification_required': True,
                        'notes': 'Account created! Email verification may be required.'
                    }
                    print(f"✅ REAL Instagram Account Created: {username}")
                    return account_data

                elif "username isn't available" in page_source:
                    print(f"❌ Username taken: {username}")
                    return None
                elif "enter a valid email" in page_source:
                    print(f"❌ Invalid email: {email}")
                    return None
                else:
                    print(f"❌ Unknown error for: {username}")
                    return None

            except TimeoutException:
                print(f"❌ Timeout during signup for: {username}")
                return None
            except NoSuchElementException:
                print(f"❌ Element not found for: {username}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating account {username}: {str(e)}")
            return None
        finally:
            if driver:
                driver.quit()

    def get_creation_delay(self):
        return 30 if self.current_user_id == ADMIN_USER_ID else 60

    def can_user_create_accounts(self, user_id, num_accounts):
        if user_id == ADMIN_USER_ID:
            return True, "OK"
        
        current_time = datetime.now()
        user_key = str(user_id)
        
        if user_key not in self.user_limits:
            self.user_limits[user_key] = {
                'count': 0,
                'reset_time': current_time + timedelta(hours=1)
            }
        
        user_data = self.user_limits[user_key]
        
        if current_time >= user_data['reset_time']:
            user_data['count'] = 0
            user_data['reset_time'] = current_time + timedelta(hours=1)
        
        if user_data['count'] + num_accounts > 10:
            remaining = 10 - user_data['count']
            return False, f"Limit exceeded! You can create {remaining} more accounts this hour."
        
        return True, "OK"
    
    def update_user_limit(self, user_id, num_accounts):
        if user_id != ADMIN_USER_ID:
            user_key = str(user_id)
            if user_key in self.user_limits:
                self.user_limits[user_key]['count'] += num_accounts

    def start_creation_process(self, num_accounts, common_password, user_id, update, context):
        can_create, message = self.can_user_create_accounts(user_id, num_accounts)
        if not can_create:
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"❌ {message}")
            return
        
        self.is_running = True
        self.common_password = common_password
        self.current_user_id = user_id
        
        self.update_user_limit(user_id, num_accounts)
        
        thread = threading.Thread(
            target=self._create_accounts_thread, 
            args=(num_accounts, update, context)
        )
        thread.start()
    
    def _create_accounts_thread(self, num_accounts, update, context):
        """Thread function for REAL account creation"""
        try:
            delay = self.get_creation_delay()
            user_type = "👑 ADMIN" if self.current_user_id == ADMIN_USER_ID else "👤 USER"
            email_domain = self.get_email_domain()
            
            start_message = (
                f"🚀 Starting REAL Instagram Account Creation...\n\n"
                f"📧 Email Domain: {email_domain}\n"
                f"🔑 Password: {self.common_password}\n"
                f"⏱️ Delay: {delay} seconds\n"
                f"👤 User Type: {user_type}\n"
                f"📊 Limit: {'♾️ UNLIMITED' if self.current_user_id == ADMIN_USER_ID else '10 accounts/hour'}\n\n"
                f"⚠️ **THIS CREATES REAL INSTAGRAM ACCOUNTS**\n"
                f"✅ Using actual Instagram website\n"
                f"🔒 Chrome automation\n"
                f"🕒 24/7 Active on Render"
            )
            context.bot.send_message(chat_id=update.effective_chat.id, text=start_message)
            
            successful = 0
            failed = 0
            
            for i in range(num_accounts):
                if not self.is_running:
                    break
                
                username = self.generate_username()
                email = f"{username}@{email_domain}"
                
                account = self.create_real_instagram_account(email, username, self.common_password)
                
                if account:
                    self.created_accounts.append(account)
                    self.save_accounts()
                    successful += 1
                    
                    success_msg = (
                        f"✅ REAL Instagram Account {i+1} CREATED!\n\n"
                        f"👤 Username: {account['username']}\n"
                        f"📧 Email: {account['email']}\n"
                        f"🔑 Password: {account['password']}\n"
                        f"🔗 Profile: {account['instagram_url']}\n\n"
                        f"📱 Login at: {account['login_url']}\n"
                        f"⚠️ {account['notes']}"
                    )
                    context.bot.send_message(chat_id=update.effective_chat.id, text=success_msg)
                else:
                    failed += 1
                    context.bot.send_message(
                        chat_id=update.effective_chat.id, 
                        text=f"❌ Account {i+1} creation failed"
                    )
                
                if (i + 1) % 2 == 0:
                    progress_msg = (
                        f"📊 Progress: {i+1}/{num_accounts}\n"
                        f"✅ Successful: {successful}\n"
                        f"❌ Failed: {failed}"
                    )
                    context.bot.send_message(chat_id=update.effective_chat.id, text=progress_msg)
                
                if i < num_accounts - 1:
                    time.sleep(delay)
            
            result_message = (
                f"🎉 REAL INSTAGRAM ACCOUNT CREATION COMPLETED!\n\n"
                f"📊 Final Statistics:\n"
                f"✅ Successful: {successful}\n"
                f"❌ Failed: {failed}\n"
                f"📈 Success Rate: {(successful/num_accounts)*100:.1f}%\n"
                f"💾 Total REAL Accounts: {len(self.created_accounts)}\n\n"
                f"🔗 Login at: https://instagram.com\n"
                f"📱 Use the credentials to login\n"
                f"🕒 Bot remains active 24/7 on Render"
            )
            context.bot.send_message(chat_id=update.effective_chat.id, text=result_message)
            
        except Exception as e:
            error_msg = f"❌ Error during account creation: {str(e)}"
            context.bot.send_message(chat_id=update.effective_chat.id, text=error_msg)
    
    def get_total_summary(self):
        if not self.created_accounts:
            return "📊 No REAL Instagram accounts created yet."
        
        total_accounts = len(self.created_accounts)
        
        summary = f"total account {total_accounts}\n\n"
        
        for i, account in enumerate(self.created_accounts, 1):
            summary += f"{i}total account according to user input\n"
            summary += f"password: {account['password']}\n"
            summary += f"username: {account['username']}\n"
            summary += f"email: {account['email']}\n"
            summary += f"status: {account['status']}\n"
            summary += "━" * 40 + "\n"
        
        return summary

# Initialize
creator = RealInstagramCreator()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_admin = user_id == ADMIN_USER_ID
    
    welcome_text = f"""
🤖 REAL Instagram Account Creator

🚀 **CREATES ACTUAL INSTAGRAM ACCOUNTS**
✅ Uses real Chrome browser automation
📧 Professional email domains
🔐 Real Instagram website signup
🕒 **24/7 ACTIVE ON RENDER**

**Commands:**
/create - Create REAL Instagram accounts
/total - Show all REAL accounts  
/status - Check creation status
/stop - Stop creation process

**Your Account:**
{'👑 ADMIN' if is_admin else '👤 USER'}
⏱️ {creator.get_creation_delay()}s delay between attempts
📊 {'♾️ UNLIMITED' if is_admin else '10 accounts/hour'}

⚠️ **Important:**
- This creates REAL Instagram accounts
- Uses actual Instagram signup form
- Success depends on Instagram restrictions
- Some accounts may require verification
- **Bot runs 24/7 on Render cloud**
"""
    await update.message.reply_text(welcome_text)

async def create_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if creator.is_running:
        await update.message.reply_text("⚠️ Account creation already in progress. Use /stop to cancel.")
        return ConversationHandler.END
    
    user_id = update.effective_user.id
    is_admin = user_id == ADMIN_USER_ID
    
    await update.message.reply_text(
        f"🔢 How many REAL Instagram accounts to create?\n"
        f"({'♾️ UNLIMITED' if is_admin else 'Maximum 10 accounts per hour'})\n\n"
        f"⚠️ **THIS CREATES REAL INSTAGRAM ACCOUNTS**\n"
        f"✅ Uses actual Instagram website\n"
        f"🔒 Chrome automation\n"
        f"🕒 24/7 Active on Render"
    )
    return ACCOUNT_COUNT

async def get_account_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        num_accounts = int(update.message.text)
        user_id = update.effective_user.id
        
        if num_accounts <= 0:
            await update.message.reply_text("❌ Please enter a positive number")
            return ACCOUNT_COUNT
        
        can_create, message = creator.can_user_create_accounts(user_id, num_accounts)
        if not can_create:
            await update.message.reply_text(f"❌ {message}")
            return ACCOUNT_COUNT
        
        context.user_data['num_accounts'] = num_accounts
        await update.message.reply_text(
            f"🔑 Enter common password for {num_accounts} accounts:\n"
            f"(Minimum 8 characters recommended)"
        )
        return PASSWORD
        
    except ValueError:
        await update.message.reply_text("❌ Please enter a valid number")
        return ACCOUNT_COUNT

async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = update.message.text.strip()
    
    if len(password) < 6:
        await update.message.reply_text("❌ Password must be at least 6 characters")
        return PASSWORD
    
    num_accounts = context.user_data['num_accounts']
    user_id = update.effective_user.id
    
    await update.message.reply_text(
        f"🔄 Starting REAL Instagram account creation...\n"
        f"⏱️ This will take approximately {num_accounts * creator.get_creation_delay()} seconds\n"
        f"🔒 Using Chrome automation\n"
        f"🕒 24/7 Active on Render"
    )
    
    creator.start_creation_process(num_accounts, password, user_id, update, context)
    
    context.user_data.clear()
    return ConversationHandler.END

async def total_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    summary = creator.get_total_summary()
    await update.message.reply_text(f"```\n{summary}\n```", parse_mode='MarkdownV2')

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if creator.is_running:
        status_msg = (
            f"🔄 REAL Instagram Account Creation in Progress...\n\n"
            f"📊 Accounts created: {len(creator.created_accounts)}\n"
            f"⏱️ Delay: {creator.get_creation_delay()} seconds\n"
            f"👤 User Type: {'👑 ADMIN' if creator.current_user_id == ADMIN_USER_ID else '👤 USER'}\n"
            f"⚡ Actively creating REAL accounts\n"
            f"🕒 24/7 Active on Render"
        )
    else:
        status_msg = (
            f"✅ Ready for REAL Instagram account creation\n"
            f"📊 Total REAL accounts: {len(creator.created_accounts)}\n"
            f"🚀 Use /create to start\n"
            f"🕒 24/7 Active on Render"
        )
    
    await update.message.reply_text(status_msg)

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if creator.is_running:
        creator.is_running = False
        await update.message.reply_text("🛑 Instagram account creation stopped")
    else:
        await update.message.reply_text("❌ No active creation process to stop")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Operation cancelled.")
    return ConversationHandler.END

def main():
    print("🤖 REAL Instagram Account Creator Started!")
    print("🚀 Using Chrome/Selenium for actual account creation")
    print("🕒 24/7 Keep-alive server running on port 8080")
    print(f"👑 ADMIN {ADMIN_USER_ID}: 30-second delay | ♾️ UNLIMITED")
    print("👤 USERS: 60-second delay | 10 accounts/hour")
    print("📧 Using professional email domains")
    print("💾 Account storage: real_instagram_accounts.json")
    print("🌐 Web interface: http://0.0.0.0:8080")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('create', create_command)],
        states={
            ACCOUNT_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_account_count)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("total", total_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(conv_handler)
    
    print("✅ Bot is now running 24/7!")
    application.run_polling()

if __name__ == "__main__":
    main()