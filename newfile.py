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

print("🚀 Instagram Bot Starting on Render...")

# Keep alive server
app = Flask('')

@app.route('/')
def home():
    return "🤖 Bot is running on Render! Use /start in Telegram"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# Start keep-alive
keep_alive()

# Bot configuration
BOT_TOKEN = "8100070394:AAE5Pov3SnkoV4It9Az2OE7_q3It36mEl50"
ADMIN_USER_ID = 6716174520

logging.basicConfig(level=logging.INFO)

class InstagramCreator:
    def __init__(self):
        self.created_accounts = []
        self.is_running = False
        self.accounts_file = "accounts.json"
        self.load_accounts()
    
    def load_accounts(self):
        try:
            if os.path.exists(self.accounts_file):
                with open(self.accounts_file, 'r') as f:
                    self.created_accounts = json.load(f)
                print(f"📂 Loaded {len(self.created_accounts)} accounts")
        except:
            self.created_accounts = []
    
    def save_accounts(self):
        try:
            with open(self.accounts_file, 'w') as f:
                json.dump(self.created_accounts, f, indent=2)
        except Exception as e:
            print(f"Save error: {e}")

# Initialize
creator = InstagramCreator()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_admin = user_id == ADMIN_USER_ID
    
    welcome_text = f"""
🤖 Instagram Account Creator Bot

🚀 Ready to create Instagram accounts!
✅ 24/7 Active on Render Cloud

**Commands:**
/start - Show this message
/create - Create Instagram accounts  
/total - Show all accounts
/status - Check bot status
/stop - Stop creation process

**Your Account:**
{'👑 ADMIN' if is_admin else '👤 USER'}
📊 {'♾️ UNLIMITED' if is_admin else '50 accounts/hour'}

🕒 Bot is running 24/7 on Render!
"""
    await update.message.reply_text(welcome_text)

async def create_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if creator.is_running:
        await update.message.reply_text("⚠️ Already running. Use /stop to cancel.")
        return
    
    await update.message.reply_text("🔢 How many accounts to create? (1-50)")

async def total_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not creator.created_accounts:
        await update.message.reply_text("📊 No accounts created yet. Use /create")
    else:
        summary = f"total account {len(creator.created_accounts)}\n\n"
        for i, account in enumerate(creator.created_accounts, 1):
            summary += f"{i}total account according to user input\n"
            summary += f"password: {account['password']}\n"
            summary += f"username: {account['username']}\n"
            summary += f"email: {account['email']}\n"
            summary += "━" * 30 + "\n"
        
        await update.message.reply_text(f"```\n{summary}\n```", parse_mode='MarkdownV2')

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if creator.is_running:
        status_msg = f"🔄 Creating accounts... Created: {len(creator.created_accounts)}"
    else:
        status_msg = f"✅ Ready | Total accounts: {len(creator.created_accounts)}"
    
    status_msg += "\n🕒 24/7 Active on Render!"
    await update.message.reply_text(status_msg)

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if creator.is_running:
        creator.is_running = False
        await update.message.reply_text("🛑 Creation stopped")
    else:
        await update.message.reply_text("❌ Not running")

def main():
    print("🤖 Instagram Bot Starting on Render...")
    print("✅ Keep-alive server running on port 8080")
    print("🚀 Bot will be ready for /start command")
    
    # Create application with modern syntax
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("create", create_command))
    application.add_handler(CommandHandler("total", total_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("stop", stop_command))
    
    print("✅ Bot started successfully!")
    print("📱 Use /start in Telegram to begin")
    
    # Start polling
    application.run_polling()

if __name__ == "__main__":
    main()