from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
import asyncio
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from messages import get_goal_message, get_followup_message

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

app = ApplicationBuilder().token(BOT_TOKEN).build()
scheduler = BackgroundScheduler()
scheduler.start()

async def goal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if context.args:
        await update.message.reply_text(get_goal_message())

        # Schedule 23-hour follow-up message
        scheduler.add_job(
            send_followup,
            'date',
            run_date=datetime.now() + timedelta(hours=23),
            args=[user.id],
            id=f"followup_{user.id}_{datetime.now().timestamp()}"
        )
    else:
        await update.message.reply_text("Please enter your goal after the command.\nExample: /goal Finish 2 Leetcode problems")

async def send_followup(user_id):
    try:
        await app.bot.send_message(chat_id=user_id, text=get_followup_message())
    except Exception as e:
        print(f"[Error] Follow-up failed for {user_id}: {e}")

from database import (
    update_progress,
    get_users_inactive_for,
    add_to_blacklist,
    remove_from_blacklist,
    get_blacklist,
    get_near_blacklist_users
)

async def progress_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    update_progress(user.id, user.username or f"id_{user.id}")
    await update.message.reply_text("Progress recorded! ✅")

async def blacklist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    entries = get_blacklist()
    if not entries:
        await update.message.reply_text("Blacklist is empty. Everyone's grinding. 💯")
    else:
        msg = "\n".join([f"{u} (since {t[:16]})" for u, t in entries])
        await update.message.reply_text(f"⛔ Blacklisted Users:\n{msg}")

async def blacklistshow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Only the owner can use this command.")
        return
    entries = get_near_blacklist_users()
    if not entries:
        await update.message.reply_text("No users approaching blacklist.")
    else:
        msg = "\n".join([f"{u} - Last update: {t[:16]}" for _, u, t in entries])
        await update.message.reply_text(f"⚠️ At-Risk Users (48h+ inactivity):\n{msg}")

async def unblacklist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("You aren't allowed to do that.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /unblacklist <username>")
        return
    username = context.args[0]
    remove_from_blacklist(username)
    await update.message.reply_text(f"✅ Removed {username} from the blacklist.")

app.add_handler(CommandHandler("progress", progress_command))
app.add_handler(CommandHandler("blacklist", blacklist_command))
app.add_handler(CommandHandler("blacklistshow", blacklistshow_command))
app.add_handler(CommandHandler("unblacklist", unblacklist_command))
app.add_handler(CommandHandler("goal", goal_command))

async def daily_check():
    inactive = get_users_inactive_for(24)
    for uid, uname in inactive:
        try:
            await app.bot.send_message(chat_id=uid, text="👋 Don't forget to log your daily progress with /progress")
        except Exception as e:
            print(f"Couldn't DM {uid} - {e}")

    too_inactive = get_users_inactive_for(72)
    for uid, uname in too_inactive:
        add_to_blacklist(uid, uname)

# Run every day at 00:00
scheduler.add_job(lambda: asyncio.run(daily_check()), 'cron', hour=0, minute=0)


if __name__ == "__main__":
    print("Bot running...")
    app.run_polling()
