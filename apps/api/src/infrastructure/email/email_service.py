"""Email Service.

Sends transactional emails (verification OTP, password reset).
Uses aiosmtplib for async SMTP. In dev, use Mailpit on port 1025.
"""

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import structlog

from infrastructure.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


async def _send_email(to: str, subject: str, html_body: str) -> None:
    """Send an email via SMTP (async).

    In development, Mailpit catches all emails on port 1025.
    View at http://localhost:8025.
    """
    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = to
        msg.attach(MIMEText(html_body, "html"))

        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER or None,
            password=settings.SMTP_PASSWORD or None,
            use_tls=settings.SMTP_PORT == 465,
            start_tls=settings.SMTP_PORT == 587,
        )
        logger.info("email_sent", to=to, subject=subject)
    except ImportError:
        # aiosmtplib not installed — log instead
        logger.warning("email_skipped_no_aiosmtplib", to=to, subject=subject)
    except Exception as e:
        logger.error("email_failed", to=to, subject=subject, error=str(e))
        # Don't raise — email failure should not block auth flow


async def send_verification_email(to: str, otp: str) -> None:
    """Send email verification OTP.

    Args:
        to: Recipient email address.
        otp: 6-digit OTP code.
    """
    subject = "💗 Eralove — Xác minh email của bạn"
    html = f"""
    <div style="font-family: 'Nunito', sans-serif; max-width: 500px; margin: 0 auto; padding: 40px 20px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <span style="font-size: 48px;">💗</span>
            <h1 style="
                background: linear-gradient(135deg, #FF6B9D, #C084FC);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: 28px;
                margin: 10px 0;
            ">Eralove</h1>
        </div>
        <div style="
            background: #ffffff;
            border-radius: 16px;
            padding: 32px;
            box-shadow: 0 4px 14px rgba(255, 107, 157, 0.15);
        ">
            <h2 style="color: #2d1b3d; margin-bottom: 16px;">Xác minh email 📧</h2>
            <p style="color: #666; line-height: 1.6;">
                Cảm ơn bạn đã đăng ký Eralove! Nhập mã OTP bên dưới để xác minh email:
            </p>
            <div style="
                text-align: center;
                margin: 24px 0;
                padding: 20px;
                background: linear-gradient(135deg, #FFF0F5, #F3E8FF);
                border-radius: 12px;
            ">
                <span style="
                    font-size: 36px;
                    font-weight: 800;
                    letter-spacing: 8px;
                    color: #7C3AED;
                    font-family: monospace;
                ">{otp}</span>
            </div>
            <p style="color: #999; font-size: 14px;">
                ⏰ Mã này hết hạn sau 5 phút.<br>
                Nếu bạn không yêu cầu mã này, hãy bỏ qua email.
            </p>
        </div>
        <p style="text-align: center; color: #ccc; font-size: 12px; margin-top: 24px;">
            © Eralove — Nơi lưu giữ mọi khoảnh khắc yêu thương
        </p>
    </div>
    """
    await _send_email(to, subject, html)


async def send_reset_password_email(to: str, reset_token: str) -> None:
    """Send password reset email.

    Args:
        to: Recipient email address.
        reset_token: Password reset token.
    """
    reset_url = f"http://localhost:3000/reset-password?token={reset_token}"
    subject = "💗 Eralove — Đặt lại mật khẩu"
    html = f"""
    <div style="font-family: 'Nunito', sans-serif; max-width: 500px; margin: 0 auto; padding: 40px 20px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <span style="font-size: 48px;">💗</span>
            <h1 style="
                background: linear-gradient(135deg, #FF6B9D, #C084FC);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: 28px;
                margin: 10px 0;
            ">Eralove</h1>
        </div>
        <div style="
            background: #ffffff;
            border-radius: 16px;
            padding: 32px;
            box-shadow: 0 4px 14px rgba(255, 107, 157, 0.15);
        ">
            <h2 style="color: #2d1b3d; margin-bottom: 16px;">Đặt lại mật khẩu 🔑</h2>
            <p style="color: #666; line-height: 1.6;">
                Bạn đã yêu cầu đặt lại mật khẩu. Nhấn nút bên dưới:
            </p>
            <div style="text-align: center; margin: 24px 0;">
                <a href="{reset_url}" style="
                    display: inline-block;
                    padding: 14px 32px;
                    background: linear-gradient(135deg, #FF6B9D, #C084FC);
                    color: #fff;
                    border-radius: 9999px;
                    text-decoration: none;
                    font-weight: 700;
                    font-size: 16px;
                ">Đặt lại mật khẩu</a>
            </div>
            <p style="color: #999; font-size: 14px;">
                ⏰ Link này hết hạn sau 15 phút.<br>
                Nếu bạn không yêu cầu, hãy bỏ qua email này.
            </p>
        </div>
    </div>
    """
    await _send_email(to, subject, html)
