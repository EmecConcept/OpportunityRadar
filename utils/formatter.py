import re

def clean_markdown(text: str) -> str:
    """Strips rogue Markdown characters that break Telegram message rendering."""
    if not text:
        return ""
    return text.replace("*", "").replace("_", " ").strip()

def format_telegram_message(opp: dict) -> str:
    """Detailed layout formatted exclusively for individual scholarship alerts."""
    title = clean_markdown(opp.get('title', 'Scholarship Opportunity'))
    country = clean_markdown(opp.get('country', 'International'))
    org = clean_markdown(opp.get('organization', 'N/A'))
    level = clean_markdown(opp.get('degree_level', 'N/A'))
    funding = clean_markdown(opp.get('funding_type', 'Fully Funded'))
    eligibility = clean_markdown(opp.get('eligibility', 'Open'))
    deadline = clean_markdown(opp.get('deadline', 'Check Website'))
    requirements = clean_markdown(opp.get('requirements', 'Standard documents'))
    link = opp.get('link', '').strip()

    return (
        f"🚨 *NEW SCHOLARSHIP ALERT* 🚨\n\n"
        f"🎓 *{title}*\n\n"
        f"🌍 *Country:* {country}\n"
        f"🏛 *Organization:* {org}\n"
        f"🎯 *Level:* {level}\n"
        f"💰 *Funding:* {funding}\n"
        f"👥 *Eligibility:* {eligibility}\n"
        f"⏳ *Deadline:* {deadline}\n"
        f"📋 *Requirements:* {requirements}\n\n"
        f"🔗 *Apply Here:* {link}\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📢 *Join CampusZone Telegram Channel for daily alerts!*"
    )

def format_job_bundle(jobs: list) -> str:
    """Compiles hourly & contract jobs into a clean, unified broadcast message."""
    if not jobs:
        return ""
        
    lines = ["💼 *Remote Hourly & Contract Opportunities Today* 💼\n"]
    
    sources = sorted(list(set(job.get('source', 'Remote') for job in jobs)))
    
    for source in sources:
        lines.append(f"*{source}*")
        source_jobs = [j for j in jobs if j.get('source', 'Remote') == source]
        
        for i, job in enumerate(source_jobs, 1):
            title = clean_markdown(job.get('title', 'Remote Contract Role'))
            rate = clean_markdown(job.get('funding_type', 'Hourly / Contract'))
            link = job.get('link', '').strip()
            
            lines.append(f"{i}. {title} ({rate}) :")
            lines.append(f"{link}\n")
            
    lines.append("━━━━━━━━━━━━━━━━━━━")
    lines.append("📢 *Join CampusZone Telegram Channel:*")
    lines.append("https://t.me/YOUR_CHANNEL_USERNAME")
    
    return "\n".join(lines)
