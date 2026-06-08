import base64
import datetime
import requests
from fastapi import HTTPException
from config import CONSUMER_KEY, CONSUMER_SECRET, AUTH_URL, SHORTCODE, PASSKEY
from logger_config import logger


def get_access_token() -> str:
    """Generate an OAuth access token from M-Pesa."""
    try:
        auth = base64.b64encode(f"{CONSUMER_KEY}:{CONSUMER_SECRET}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}
        logger.info("Requesting M-Pesa access token")
        response = requests.get(AUTH_URL, headers=headers, timeout=30)

        if response.status_code != 200:
            error_detail = response.json().get(
                "errorMessage", "Failed to get access token"
            )
            logger.error("Failed to get access token: %s", error_detail)
            raise HTTPException(status_code=500, detail=error_detail)

        data = response.json()
        access_token = data.get("access_token")
        if not access_token:
            logger.error("No access_token in response: %s", data)
            raise HTTPException(status_code=500, detail="No access token in response")

        logger.info("Successfully retrieved access token")
        return access_token

    except requests.exceptions.RequestException as e:
        logger.error("Failed to retrieve access token: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=502, detail="Failed to connect to M-Pesa API"
        ) from e


def generate_password() -> tuple[str, str]:
    """Generate the password and timestamp for STK Push."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(f"{SHORTCODE}{PASSKEY}{timestamp}".encode()).decode()
    logger.info("Generated STK Push password for timestamp: %s", timestamp)
    return password, timestamp
