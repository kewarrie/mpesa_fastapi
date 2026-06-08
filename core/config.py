import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# M-Pesa credentials
CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
SHORTCODE = os.getenv("SHORTCODE")
PASSKEY = os.getenv("PASSKEY")
CALLBACK_URL = os.getenv("CALLBACK_URL")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")

# Validate required environment variables
required_vars = {
    "CONSUMER_KEY": CONSUMER_KEY,
    "CONSUMER_SECRET": CONSUMER_SECRET,
    "SHORTCODE": SHORTCODE,
    "PASSKEY": PASSKEY,
    "CALLBACK_URL": CALLBACK_URL,
    "PHONE_NUMBER": PHONE_NUMBER,
}
missing_vars = [key for key, value in required_vars.items() if not value]
if missing_vars:
    raise ValueError(
        f"Missing required environment variables: {', '.join(missing_vars)}"
    )

# URLs (use sandbox for development, replace with live URLs in production)
AUTH_URL = (
    "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
)
STK_PUSH_URL = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

# Production URLs (uncomment for production)
# AUTH_URL = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
# STK_PUSH_URL = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
