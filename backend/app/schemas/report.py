"""
Pydantic schemas for issue reports.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Literal


class ReportIssueRequest(BaseModel):
    """Schema for reporting an issue with a service location."""

    issue_type: Literal['closed', 'hours', 'full', 'referral', 'other'] = Field(
        ...,
        description="Type of issue being reported"
    )
    location_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Name of the location with the issue"
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Detailed description of the issue"
    )
    captcha_token: str = Field(
        ...,
        description="Google reCAPTCHA v2 token for spam prevention"
    )

    @field_validator('location_name', 'description')
    @classmethod
    def sanitize_text(cls, v: str) -> str:
        """Remove potentially dangerous characters."""
        if not v:
            return v
        # Remove HTML tags and trim
        return v.strip().replace('<', '').replace('>', '')

    class Config:
        json_schema_extra = {
            "example": {
                "issue_type": "hours",
                "location_name": "Holy Apostles Soup Kitchen",
                "description": "The hours listed are incorrect. They close at 1pm not 2pm."
            }
        }


class ReportIssueResponse(BaseModel):
    """Response after submitting an issue report."""

    status: str = Field(..., description="Status of the submission")
    message: str = Field(..., description="Human-readable message")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Thank you for your report. We will review it shortly."
            }
        }
