import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

FROM_EMAIL = os.getenv("GMAIL_USER")
FROM_PASSWORD = os.getenv("GMAIL_PASS")

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

def build_html_email(news_items):
    """Build the newsletter HTML."""
    date_today = datetime.now().strftime("%d %B %Y")

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f6f6f6;">
        <div style="max-width: 600px; margin: auto; background: #ffffff; padding: 20px; border-radius: 8px;">
            <h2 style="text-align: center; color: #333;">🧠 Building Startup - Daily AI Digest</h2>
            <p style="text-align: center; color: #777;">{date_today}</p>
            <hr style="margin: 20px 0;">
    """
    ind = 0
    for category, articles in news_items.items():
        # html += f"<h3 style='color: #555;'>{category}:</h3>"

        for idx, item in enumerate(articles, start=1):
            # Safeguard to check if the 'title' and 'link' keys exist
            title = item.get('title', 'No title available')
            link = item.get('link', '#')
            ind+=1
            html += f"""
                <div style="margin-bottom: 30px;">
                    <h4 style="color: #333;">#{ind}. <a href="{link}" style="color: #1a73e8; text-decoration: none;">{title}</a></h4>
            """
            
            if item.get('summary') and "Summary unavailable" not in item['summary']:
                formatted_summary = item['summary'].replace("* ", "<br>• ")
                html += f"""
                    <p style="color: #555; font-size: 15px; line-height: 1.6;">{formatted_summary}</p>
                """
            else:
                html += """
                    <p style="color: #888;">Summary not available for this article. 💤</p>
                """
            html += "</div>"

    html += """
            <hr style="margin: 20px 0;">
            <p style="text-align: center; font-size: 12px; color: #aaa;">
                You are receiving this email because you subscribed to Building Startup Daily News.<br>
                Made with ❤️ by the Building Startup Team.
            </p>
        </div>
    </body>
    </html>
    """
    return html

def send_newsletter(to_emails, html_content):
    """Send newsletter using Gmail SMTP."""
    print("📧 Sending email using Gmail SMTP...")
    try:
        for recipient in to_emails:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "🧠 Building Startup - Today's Top AI News!"
            msg['From'] = FROM_EMAIL
            msg['To'] = recipient

            part = MIMEText(html_content, 'html')
            msg.attach(part)

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(FROM_EMAIL, FROM_PASSWORD)
                server.sendmail(FROM_EMAIL, recipient, msg.as_string())

        print("✅ Emails sent successfully.")

    except Exception as e:
        print("❌ Gmail SMTP Error:", e)
