"""All LangChain tools."""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
from langchain_core.tools import tool
from langchain_community.utilities import GoogleSerperAPIWrapper

from config import settings

@tool
def calculator(expression: str) -> str:
    """Do math calculations like 15 * 23 or 100/4."""
    try:
        allowed = set("1234567890-+/*. ()")
        if not all(c in allowed for c in expression):
            return "Error: Only numbers and math symbols allowed"
        return str(eval(expression))
    except Exception:
        return "Error: Try Again"

@tool
def word_count(text: str) -> str:
    """Count number of words in a text."""
    return str(len(text.split()))

@tool
def get_weather(city: str) -> str:
    """Get current weather for any city."""
    try:
        city = city.strip().replace(" ", "+")
        r = requests.get(f"https://wttr.in/{city}?format=%C+%t", timeout=5)
        return r.text if r.status_code == 200 else f"Could not get weather for {city}"
    except Exception:
        return "Weather unavailable"

@tool
def send_email(recipient: str, subject: str, message: str) -> str:
    """Send email to any recipient using SMTP."""
    try:
        sender = settings.EMAIL_SENDER
        password = settings.EMAIL_PASSWORD
        if not sender or not password:
            return "❌ Error: Email credentials not configured in secrets.toml"

        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        return f"✅ Email sent successfully to {recipient}"
    except Exception as e:
        
        return f"❌ Email Error: {str(e)}"

@tool
def web_search(query: str) -> str:
    """Search live internet for news using Google Serper."""
    try:
        import os
        os.environ["SERPER_API_KEY"] = settings.SERPER_API_KEY
        search = GoogleSerperAPIWrapper()
        results = search.results(query)
        formatted = []
        if "organic" in results:
            for item in results["organic"][:3]:
                formatted.append(
                    f"• {item.get('title','')} ({item.get('link','')})\n  "
                    f"{item.get('snippet','')}"
                )
        return "\n\n".join(formatted) if formatted else "No web results found."
    except Exception as e:
        return f"Web search failed: {e}"