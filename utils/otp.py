import random
import base64
import json
import uuid
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.template import Template, Context
from django.core.mail import EmailMultiAlternatives

from helpers.phone import format_mm_phone


def generate_otp(length=6):
    return "".join([str(random.randint(0, 9)) for _ in range(length)])


def send_otp_sms(phone, otp_code):
    if not settings.SMSPOH_API_KEY or not settings.SMSPOH_API_SECRET:
        raise RuntimeError("SMSPoh API credentials are not configured")

    credentials = f"{settings.SMSPOH_API_KEY}:{settings.SMSPOH_API_SECRET}".encode()
    bearer_token = base64.b64encode(credentials).decode("ascii")
    payload = {
        "from": settings.SMSPOH_SENDER_ID,
        "to": format_mm_phone(phone),
        "message": f"Your DigiLex verification code is {otp_code}",
        "clientReference": f"digilex-otp-{uuid.uuid4().hex}",
    }
    request = Request(
        settings.SMSPOH_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=15) as response:
            response_data = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError) as error:
        raise RuntimeError("SMSPoh request failed") from error
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise RuntimeError("SMSPoh returned an invalid response") from error

    messages = response_data.get("messages", [])
    if not messages:
        raise RuntimeError("SMSPoh returned no message result")

    message_result = messages[0]
    if message_result.get("status") not in {"Accepted", "Sent", "Delivered"}:
        provider_message = message_result.get("message") or "unknown provider error"
        raise RuntimeError(f"SMSPoh rejected the OTP message: {provider_message}")

    return True


def send_otp_email(user_email, otp_code):
    html_template = """
    <div style="background-color: #f8f9fa; padding: 40px 0; font-family: 'Segoe UI', Helvetica, Arial, sans-serif; margin: 0;">
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 520px; background-color: #0d1b3e; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px rgba(13, 27, 62, 0.15);">
            <!-- Header Section -->
            <tr>
                <td style="padding: 35px 20px; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <table align="center" border="0" cellpadding="0" cellspacing="0">
                        <tr>
                            <td style="padding-right: 10px; vertical-align: middle;">
                                <!-- Simple Scaled Scale Icon using HTML Shape fallback -->
                                <span style="color: #d4a017; font-size: 28px; font-weight: bold;">⚖</span>
                            </td>
                            <td style="text-align: left; vertical-align: middle;">
                                <h1 style="color: #ffffff; margin: 0; font-size: 26px; font-weight: 700; letter-spacing: 0.5px;">Digi<span style="color: #d4a017;">Lex</span></h1>
                                <p style="color: rgba(255,255,255,0.5); margin: 2px 0 0 0; font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px;">Digital Law Platform</p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
            
            <!-- Body Content Card -->
            <tr>
                <td style="padding: 30px 30px 40px 30px; text-align: center;">
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #ffffff; border-radius: 12px; padding: 35px 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
                        <tr>
                            <td>
                                <h2 style="color: #0d1b3e; margin-top: 0; font-size: 22px; font-weight: 700;">Security Verification</h2>
                                <p style="color: #495057; font-size: 15px; line-height: 1.6; margin: 20px 0 10px 0;">Hello,</p>
                                <p style="color: #495057; font-size: 15px; line-height: 1.6; margin: 0 0 25px 0;">To complete your secure registration, please use the following 6-digit One-Time Password (OTP):</p>
                                
                                <!-- OTP Display Box -->
                                <div style="margin: 30px 0;">
                                    <span style="display: inline-block; font-size: 34px; font-weight: 700; color: #0d1b3e; letter-spacing: 6px; padding: 14px 28px; border: 2px dashed #d4a017; border-radius: 8px; background-color: #fffbee;">
                                        {{ otp_code }}
                                    </span>
                                </div>
                                
                                <p style="color: #6c757d; font-size: 13px; line-height: 1.5; margin: 25px 0 0 0;">
                                    This verification code is valid for <b style="color: #dc3545;">15 minutes</b>.<br>
                                    For security layout purposes, do not share this code with anyone.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
            
            <!-- Footer Section -->
            <tr>
                <td style="padding: 24px; text-align: center; background-color: #09132c; border-top: 1px solid rgba(255,255,255,0.03);">
                    <p style="color: rgba(255,255,255,0.4); font-size: 12px; margin: 0;">&copy; 2026 DigiLex Platform. All rights reserved.</p>
                    <p style="color: rgba(255,255,255,0.3); font-size: 11px; margin: 6px 0 0 0;">Digital Law at Your Fingertips</p>
                </td>
            </tr>
        </table>
    </div>
    """
    template = Template(html_template)
    context = Context({"otp_code": otp_code})
    html_content = template.render(context)

    subject = "Verify Your Email Address - DigiLex"
    msg = EmailMultiAlternatives(subject, "", None, [user_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()