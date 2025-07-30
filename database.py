import sqlite3
from datetime import datetime, timedelta
import os

conn = sqlite3.connect("/data/bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS progress (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    last_checkin DATETIME
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS blacklist (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    blacklisted_at DATETIME
)
""")

conn.commit()

def update_progress(user_id, username):
    now = datetime.now()
    cursor.execute("""
        INSERT INTO progress (user_id, username, last_checkin)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET last_checkin=excluded.last_checkin, username=excluded.username
    """, (user_id, username, now))
    conn.commit()

def get_users_inactive_for(hours):
    threshold = datetime.now() - timedelta(hours=hours)
    cursor.execute("SELECT user_id, username FROM progress WHERE last_checkin < ?", (threshold,))
    return cursor.fetchall()

def add_to_blacklist(user_id, username):
    cursor.execute("""
        INSERT OR IGNORE INTO blacklist (user_id, username, blacklisted_at)
        VALUES (?, ?, ?)
    """, (user_id, username, datetime.now()))
    conn.commit()

def remove_from_blacklist(username):
    cursor.execute("DELETE FROM blacklist WHERE username = ?", (username,))
    conn.commit()

def get_blacklist():
    cursor.execute("SELECT username, blacklisted_at FROM blacklist")
    return cursor.fetchall()

def get_near_blacklist_users():
    threshold = datetime.now() - timedelta(hours=48)
    cursor.execute("SELECT user_id, username, last_checkin FROM progress WHERE last_checkin < ?", (threshold,))
    return cursor.fetchall()
