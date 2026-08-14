from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    """ 
    Request model for incoming chat messages.
    """
    message: str

class ChatResponse(BaseModel):
    """
    Response model for outgoing chat messages.
    """
    reply: str

class ChatIntent(BaseModel):
    """
    Represents the intent detected by the AI agent.
    """
    intent: str

class ChatBookingData(BaseModel):
    """
    Information extracted from a chat message.
    """

    customer_name: Optional[str] = None
    appointment_date: Optional[str] = None
    appointment_time: Optional[str] = None

class ChatUpdateData(BaseModel):
    """
    Information extracted for updating an appointment.
    """
    appointment_id: int | None = None
    customer_name: str | None = None
    appointment_date: str | None = None
    appointment_time: str | None = None

class ChatCancelData(BaseModel):
    """
    Information extracted for cancelling an appointment.
    """
    appointment_id: int | None = None
    customer_name: str | None = None