import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st

def generate_otp(length=6):
    """Generate a random numeric OTP string."""
    return ''.join(str(random.randint(0, 9)) for _ in range(length))

def send_otp_email(to_email: str, otp: str) -> bool:
    """
    Sends an OTP email using smtplib and settings from st.secrets.
    Returns True if successful, False if failed.
    """
    try:
        if 'email' not in st.secrets:
            # Fallback (Dự phòng) cho chế độ dev
            print(f"\n[DEV MODE] Mật khẩu OTP của bạn là: {otp}\n")
            st.session_state.dev_otp_msg = f"DEV MODE (No Streamlit secrets found): Your OTP is **{otp}**"
            return True

        smtp_server = st.secrets["email"].get("smtp_server", "smtp.gmail.com")
        smtp_port = st.secrets["email"].get("smtp_port", 587)
        sender_email = st.secrets["email"].get("sender_email", "")
        sender_password = st.secrets["email"].get("sender_password", "")

        if not sender_email or not sender_password or sender_email == "your-email@gmail.com":
            print(f"\n[DEV MODE] OTP của bạn là: {otp}\n")
            st.session_state.dev_otp_msg = f"DEV MODE (Credentials missing in secrets.toml): Your OTP is **{otp}**"
            return True

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = "Pet Shop Premium - Your Password Reset OTP"

        body = f"""
        <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>Hello,</p>
                <p>You have requested to reset your password. Use the following OTP to proceed:</p>
                <h3 style="color: #64DD17; font-size: 24px; letter-spacing: 5px;">{otp}</h3>
                <p>If you did not request this, please ignore this email.</p>
                <br>
                <p>Best regards,<br>Pet Shop Premium Team</p>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, to_email, text)
        server.quit()

        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        st.error(f"Failed to send email: {str(e)}")
        # In OTP ra terminal để phòng hờ
        print(f"FAILED TO SEND OTP = {otp}")
        return False
