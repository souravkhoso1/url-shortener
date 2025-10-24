# shortener/email_utils.py
import os
from mailersend import MailerSendClient, EmailBuilder
from dotenv import load_dotenv

load_dotenv()


def send_password_reset_email(user_email, username, reset_link):
    """
    Send password reset email using MailerSend API

    Args:
        user_email: Email address of the user
        username: Username of the user
        reset_link: The password reset link

    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        # Get API key from environment
        api_key = os.getenv('MAILERSEND_API_KEY')

        if not api_key:
            print("Error: MAILERSEND_API_KEY not set in environment variables")
            return False

        # Initialize MailerSend client
        client = MailerSendClient(api_key)

        # Email configuration
        from_email = os.getenv('MAILERSEND_FROM_EMAIL', 'admin@souravkhoso1.pythonanywhere.com')
        from_name = os.getenv('MAILERSEND_FROM_NAME', 'URL Shortener Support')

        # Build email content
        html_content = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f8f9fa;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background-color: #667eea;
                    color: white !important;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    font-size: 12px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔗 Password Reset Request</h1>
                </div>
                <div class="content">
                    <p>Hello <strong>{username}</strong>,</p>

                    <p>We received a request to reset your password for your URL Shortener account.</p>

                    <p>Click the button below to reset your password:</p>

                    <p style="text-align: center;">
                        <a href="{reset_link}" class="button">Reset Password</a>
                    </p>

                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; background: white; padding: 10px; border-radius: 5px;">
                        {reset_link}
                    </p>

                    <p><strong>This link will expire in 24 hours.</strong></p>

                    <p>If you didn't request a password reset, you can safely ignore this email. Your password will remain unchanged.</p>

                    <div class="footer">
                        <p>This is an automated message from URL Shortener. Please do not reply to this email.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Password Reset Request

        Hello {username},

        We received a request to reset your password for your URL Shortener account.

        Click or copy the following link to reset your password:
        {reset_link}

        This link will expire in 24 hours.

        If you didn't request a password reset, you can safely ignore this email.

        ---
        URL Shortener Support
        """

        # Build and send email
        email = (EmailBuilder()
                 .from_email(from_email, from_name)
                 .to_many([{"email": user_email, "name": username}])
                 .subject("Reset Your Password - URL Shortener")
                 .html(html_content)
                 .text(text_content)
                 .build())

        response = client.emails.send(email)
        print(f"Password reset email sent successfully to {user_email}")
        return True

    except Exception as e:
        print(f"Error sending password reset email: {e}")
        return False
