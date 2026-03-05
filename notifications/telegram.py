"""
Telegram notifications for job alerts and summaries.
Note: Telegram's Markdown is strict — underscores and asterisks in job titles
may need escaping. Consider switching to parse_mode='HTML' if formatting issues occur.
"""
import os

import requests


def _score_emoji(fit_score):
    """Return emoji for fit score: 🔥 8+, ✨ 7+, 💡 below."""
    if fit_score >= 8:
        return "🔥"
    if fit_score >= 7:
        return "✨"
    return "💡"


def send_telegram_alert(job, fit_analysis, is_priority, config):
    """Send one Telegram message per job."""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not bot_token or not chat_id:
        print("    ⚠️ Telegram not configured (TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing)")
        return

    fit_score = fit_analysis['fit_score']
    emoji = _score_emoji(fit_score)
    priority_tag = " [PRIORITY]" if is_priority else ""
    reasons_for = fit_analysis.get('reasons_for', [])[:1]
    reasons_against = fit_analysis.get('reasons_against', [])
    gap = reasons_against[0] if reasons_against else "None"
    reason_for = reasons_for[0] if reasons_for else ""

    lines = [
        f"{emoji} {fit_score}/10{priority_tag} — {fit_analysis.get('recommendation', '')}",
        job['title'],
        job['company'],
    ]
    if reason_for:
        lines.append(f"✅ {reason_for}")
    lines.append(f"⚠️ {gap}")
    lines.append(f"🔗 {job['url']}")

    message = "\n".join(lines)

    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        requests.post(url, json={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }, timeout=10)
        print(f"    ✅ Telegram alert sent for {job['company']}")
    except Exception as e:
        print(f"    ❌ Failed to send Telegram alert: {str(e)}")


def send_telegram_summary(matched_jobs, companies_checked, config):
    """Send summary after all jobs processed. Only sends when no matches and send_if_no_matches is True."""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not bot_token or not chat_id:
        return

    send_if_no_matches = config.get('telegram', {}).get('send_if_no_matches', False)

    if matched_jobs:
        # Individual alerts already sent per job — do not send summary
        return

    if not send_if_no_matches:
        return

    message = (
        f"🤖 Actually Remote — No matches today\n"
        f"{companies_checked} companies checked. ☕"
    )

    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        requests.post(url, json={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }, timeout=10)
        print("    ✅ Telegram summary sent (no matches)")
    except Exception as e:
        print(f"    ❌ Failed to send Telegram summary: {str(e)}")
