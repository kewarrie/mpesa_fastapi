from typing import Annotated, Optional
from pydantic import BaseModel, Field, StringConstraints, field_validator
from config import PHONE_NUMBER


class PaymentRequest(BaseModel):
    phone_number: Annotated[str, StringConstraints(min_length=12, max_length=12)] = (
        Field(
            examples=[PHONE_NUMBER],
            description="Phone number in international format",
        )
    )

    amount: float = Field(
        ge=1.0, examples=[1.0], description="Amount to be paid in KES"
    )

    account_reference: Annotated[
        str, StringConstraints(min_length=1, max_length=12)
    ] = Field(examples=["Order123"], description="Account reference")

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v):
        if not v.startswith("254") or not v.isdigit():
            raise ValueError(
                "Phone number must start with '254' and contain only digits"
            )
        return v

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        if v > 150000:
            raise ValueError("Amount exceeds M-Pesa transaction limit of 150,000 KES")
        return v


# Models for callback validation (optional, but recommended)
class CallbackMetadataItem(BaseModel):
    Name: str
    Value: str


class StkCallback(BaseModel):
    ResultCode: int
    ResultDesc: str
    CheckoutRequestID: Optional[str] = None
    CallbackMetadata: Optional[dict] = None


class CallbackBody(BaseModel):
    stkCallback: StkCallback


class CallbackData(BaseModel):
    Body: CallbackBody
