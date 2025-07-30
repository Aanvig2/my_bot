import random

GOAL_MESSAGES = [
"Good work so far! Just make sure to update your progress within 24 hours. I'm keeping an eye 👀",
"Nice going! Don’t forget to drop your next update within the day.⏳",
"Nice job keeping up. Let’s see the next update within 24 hours.",
"You’re doing well! just stay consistent. Progress update due in 24 hours.",
"Doing good! Just make sure to send your next update within the time window."
]

FOLLOWUP_MESSAGES = [
    "Hey! It's been 23 hours since your last update. Share your daily progress and don't forget to tag it with today’s date (e.g., 30/07)!",
    "⏰ Just a heads-up, 23 hours passed! Time to post your daily update. Remember to tag it with the date!",
    "Daily grind check-in time! It’s been 23 hours — post your progress and slap today’s date on it.",
    "Progress time! You’re 23 hours in, don’t break the chain. Drop your daily update and tag it with today’s date before the timer resets.",
    "23 hours gone in a flash ⚡ Time to report your LeetCode wins. Include today’s date so the bot overlord stays pleased."
]


def get_goal_message():
    return random.choice(GOAL_MESSAGES)

def get_followup_message():
    return random.choice(FOLLOWUP_MESSAGES)
