"""
Email notification service using Gmail SMTP.

Requires GMAIL_USER and GMAIL_APP_PASSWORD in environment variables.
If either is missing, emails are silently skipped (app still works).
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import GMAIL_APP_PASSWORD, GMAIL_USER


def _send(to_email: str, subject: str, body_html: str) -> None:
    print(f"[EMAIL DEBUG] GMAIL_USER='{GMAIL_USER}' PASSWORD_SET={bool(GMAIL_APP_PASSWORD)}")
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        print("[EMAIL DEBUG] Credentials missing, skipping.")
        return
    print(f"[EMAIL DEBUG] Sending to {to_email}...")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = to_email
    msg.attach(MIMEText(body_html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, to_email, msg.as_string())


def send_rsvp_confirmation(
    to_email: str,
    username: str,
    event_title: str,
    event_date: str,
    event_location: str | None,
) -> None:
    location_line = f"<p><b>Location:</b> {event_location}</p>" if event_location else ""
    body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 500px; margin: auto;">
        <h2 style="color: #2c3e50;">RSVP Confirmed!</h2>
        <p>Hi <b>{username}</b>,</p>
        <p>Your RSVP has been confirmed for the following event:</p>
        <div style="background:#f4f4f4; padding:16px; border-radius:8px;">
            <p><b>Event:</b> {event_title}</p>
            <p><b>Date:</b> {event_date}</p>
            {location_line}
        </div>
        <p style="margin-top:16px;">See you there!</p>
        <p style="color:#999; font-size:12px;">— CampusHub</p>
    </div>
    """
    try:
        _send(to_email, f"RSVP Confirmed: {event_title}", body)
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send RSVP confirmation: {e}")


def send_rsvp_cancellation(
    to_email: str,
    username: str,
    event_title: str,
) -> None:
    body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 500px; margin: auto;">
        <h2 style="color: #2c3e50;">RSVP Cancelled</h2>
        <p>Hi <b>{username}</b>,</p>
        <p>Your RSVP for <b>{event_title}</b> has been cancelled.</p>
        <p>You can re-register anytime on CampusHub.</p>
        <p style="color:#999; font-size:12px;">— CampusHub</p>
    </div>
    """
    try:
        _send(to_email, f"RSVP Cancelled: {event_title}", body)
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send RSVP cancellation: {e}")


def send_event_reminder(
    to_email: str,
    username: str,
    event_title: str,
    event_date: str,
    event_time: str | None,
    event_location: str | None,
) -> None:
    time_line = f"<p><b>Time:</b> {event_time}</p>" if event_time else ""
    location_line = f"<p><b>Location:</b> {event_location}</p>" if event_location else ""
    body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 500px; margin: auto;">
        <h2 style="color: #2c3e50;">Upcoming Event Reminder</h2>
        <p>Hi <b>{username}</b>,</p>
        <p>This is a reminder that your RSVP'd event is coming up soon:</p>
        <div style="background:#f4f4f4; padding:16px; border-radius:8px;">
            <p><b>Event:</b> {event_title}</p>
            <p><b>Date:</b> {event_date}</p>
            {time_line}
            {location_line}
        </div>
        <p style="margin-top:16px;">We hope you have a great time!</p>
        <p style="color:#999; font-size:12px;">CampusHub</p>
    </div>
    """
    try:
        _send(to_email, f"Reminder: {event_title} is coming up", body)
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send event reminder: {e}")
