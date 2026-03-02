import os

import requests


def send_discord_alert(job, fit_analysis, is_priority, config):
    """Send one Discord message per job."""
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    if not webhook_url:
        print("    ⚠️ Discord webhook not configured, skipping alert")
        return

    fit_score = fit_analysis['fit_score']
    if fit_score >= 8:
        color = 3066993  # Green
        emoji = "🔥"
    elif fit_score >= 7:
        color = 15844367  # Gold
        emoji = "✨"
    else:
        color = 10181046  # Purple
        emoji = "💡"

    priority_tag = " [PRIORITY]" if is_priority else ""
    reasons_for = "\n".join([f"• {r}" for r in fit_analysis['reasons_for'][:2]])
    reasons_against = fit_analysis['reasons_against'][0] if fit_analysis['reasons_against'] else "None"

    message = {
        "content": f"{emoji} **{fit_score}/10{priority_tag}** - {fit_analysis['recommendation']}",
        "embeds": [{
            "title": job['title'],
            "url": job['url'],
            "description": f"**{job['company']}**",
            "color": color,
            "fields": [
                {"name": "✅ Good Fit", "value": reasons_for[:500], "inline": False},
                {"name": "⚠️ Gap", "value": reasons_against[:200], "inline": False}
            ]
        }]
    }

    try:
        requests.post(webhook_url, json=message, timeout=10)
        print(f"    ✅ Discord alert sent for {job['company']}")
    except Exception as e:
        print(f"    ❌ Failed to send Discord alert: {str(e)}")


def send_discord_summary(matched_jobs, companies_checked, config):
    """Send summary after all jobs processed. Only sends when no matches and send_if_no_matches is True."""
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    if not webhook_url:
        return

    send_if_no_matches = config.get('discord', {}).get('send_if_no_matches', False)

    if matched_jobs:
        # Individual alerts already sent per job — do not send summary
        return

    if not send_if_no_matches:
        return

    message = (
        f"📊 Actually Remote — No matches today\n"
        f"{companies_checked} companies checked. ☕"
    )

    try:
        requests.post(webhook_url, json={"content": message}, timeout=10)
        print("    ✅ Discord summary sent (no matches)")
    except Exception as e:
        print(f"    ❌ Failed to send Discord summary: {str(e)}")
