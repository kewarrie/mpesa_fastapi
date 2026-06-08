from fastapi import FastAPI, HTTPException
from models import PaymentRequest, CallbackData
from utils import get_access_token, generate_password
from config import SHORTCODE, CALLBACK_URL, STK_PUSH_URL
import requests
from logger_config import logger

app = FastAPI(title="M-Pesa FastAPI Integration")


@app.post("/initiate-payment/")
async def initiate_payment(payment: PaymentRequest):
    """Initiate an STK Push payment request."""
    try:
        # Get access token
        access_token = get_access_token()
        if not access_token:
            raise HTTPException(
                status_code=401, detail="Failed to retrieve access token"
            )

        # Generate password and timestamp
        password, timestamp = generate_password()

        # Prepare STK Push payload
        payload = {
            "BusinessShortCode": SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": str(
                int(payment.amount)
            ),  # Convert to integer string (M-Pesa doesn't accept decimals)
            "PartyA": payment.phone_number,  # Customer phone number
            "PartyB": SHORTCODE,  # Business shortcode
            "PhoneNumber": payment.phone_number,
            "CallBackURL": CALLBACK_URL,
            "AccountReference": payment.account_reference,
            "TransactionDesc": f"Payment for {payment.account_reference}",
        }

        # Send STK Push request
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        logger.info(
            "Initiating STK Push for phone number: %s, amount: %s",
            payment.phone_number,
            payment.amount,
        )
        response = requests.post(
            STK_PUSH_URL, json=payload, headers=headers, timeout=60
        )

        if response.status_code != 200:
            error_detail = response.json().get(
                "errorMessage", "Failed to initiate STK Push"
            )
            logger.error("STK Push failed: %s", error_detail)
            raise HTTPException(status_code=500, detail=error_detail)

        result = response.json()
        logger.info(
            "STK Push successful. CheckoutRequestID: %s",
            result.get("CheckoutRequestID"),
        )
        return result

    except requests.exceptions.Timeout as e:
        logger.error(
            "Request timed out for phone number: %s",
            payment.phone_number,
            exc_info=True,
        )
        raise HTTPException(status_code=504, detail="Request timed out") from e
    except requests.exceptions.RequestException as e:
        logger.error("Request failed: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=502, detail="Bad gateway or network error"
        ) from e
    except Exception as e:
        logger.error("Unexpected error: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e


@app.post("/callback/")
async def payment_callback(callback_data: CallbackData):
    """Handle M-Pesa callback response."""
    logger.info("Callback received: %s", callback_data.model_dump())

    # Extract callback details
    stk_callback = callback_data.Body.stkCallback

    # Check if payment was successful
    if stk_callback.ResultCode == 0:
        # Payment successful
        checkout_request_id = stk_callback.CheckoutRequestID
        if not checkout_request_id:
            logger.warning("Missing CheckoutRequestID in successful callback")
            raise HTTPException(status_code=400, detail="Missing CheckoutRequestID")

        callback_metadata = stk_callback.CallbackMetadata
        amount = None
        if callback_metadata:
            for item in callback_metadata.get("Item", []):
                if item.get("Name") == "Amount":
                    amount = item.get("Value")
                    break
        if not amount:
            logger.warning("Missing amount in callback metadata")
            raise HTTPException(status_code=400, detail="Missing payment amount")

        logger.info(
            "Payment successful for CheckoutRequestID: %s, amount: %s",
            checkout_request_id,
            amount,
        )
        return {
            "status": "success",
            "message": f"Payment of {amount} received",
            "checkout_request_id": checkout_request_id,
        }
    else:
        # Payment failed
        result_desc = stk_callback.ResultDesc
        logger.warning("Payment failed: %s", result_desc)
        return {"status": "failed", "message": result_desc}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
