import os
import resend
from datetime import datetime

def _score_emoji(fit_score):
    """Return emoji for fit score: 🔥 8+, ✨ 7+, 💡 below."""
    if fit_score >= 8:
        return "🔥"
    if fit_score >= 7:
        return "✨"
    return "💡"


def send_email_digest(matched_jobs, companies_checked, config):
    resend.api_key = os.getenv('RESEND_API_KEY')
    email_from = os.getenv('EMAIL_FROM', 'onboarding@resend.dev')
    email_to = os.getenv('EMAIL_TO')
    email_config = config.get('email', {})
    send_empty = email_config.get('send_if_no_matches', False)

    if not matched_jobs and not send_empty:
        return

    today = datetime.now().strftime('%Y-%m-%d')

    if not matched_jobs:
        subject = "Actually Remote — No matches today"
        html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>{subject}</title></head>
<body style="font-family: system-ui, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
  <h1 style="color: #333;">Actually Remote</h1>
  <p style="color: #666;">{today}</p>
  <p>No new matches today. {companies_checked} companies checked.</p>
  <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;">
  <p style="color: #999; font-size: 12px;">Powered by Actually Remote</p>
</body>
</html>
"""
    else:
        subject = f"Actually Remote — {len(matched_jobs)} new matches today"
        cards_html = []
        for job in matched_jobs:
            fit_score = job['fit_score']
            emoji = _score_emoji(fit_score)
            priority_tag = " [PRIORITY]" if job['is_priority'] else ""
            fit_analysis = job['fit_analysis']
            reasons_for = fit_analysis.get('reasons_for', [])[:2]
            reasons_against = fit_analysis.get('reasons_against', [])
            gap = reasons_against[0] if reasons_against else "None"

            reasons_for_html = "".join([f"<li>{r}</li>" for r in reasons_for])

            card = f"""
  <div style="border: 1px solid #eee; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
    <p style="margin: 0 0 8px 0; font-size: 14px;">
      {emoji} <strong>{fit_score}/10</strong>{priority_tag} — {fit_analysis.get('recommendation', '')}
    </p>
    <p style="margin: 0 0 8px 0; font-size: 16px;">
      <a href="{job['url']}" style="color: #0066cc;">{job['title']}</a>
    </p>
    <p style="margin: 0 0 12px 0; color: #666;">{job['company']}</p>
    <p style="margin: 0 0 4px 0; font-size: 14px;"><strong>✅ Good fit:</strong></p>
    <ul style="margin: 0 0 8px 0; padding-left: 20px;">{reasons_for_html}</ul>
    <p style="margin: 0; font-size: 14px;"><strong>⚠️ Gap:</strong> {gap}</p>
  </div>
"""
            cards_html.append(card)

        html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>{subject}</title></head>
<body style="font-family: system-ui, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
  <h1 style="color: #333;">Actually Remote</h1>
  <p style="color: #666;">{today}</p>
{"".join(cards_html)}
  <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;">
  <p style="color: #999; font-size: 12px;">Powered by Actually Remote</p>
</body>
</html>
"""

    try:
        params = {
            "from": os.getenv('EMAIL_FROM', 'onboarding@resend.dev'),
            "to": [os.getenv('EMAIL_TO')],
            "subject": subject,
            "html": html
        }
        resend.Emails.send(params)
        if matched_jobs:
            print(f"    ✅ Email digest sent ({len(matched_jobs)} matches)")
        else:
            print(f"    ✅ Email digest sent (no matches)")
    except Exception as e:
        print(f"    ❌ Failed to send email digest: {str(e)}")
