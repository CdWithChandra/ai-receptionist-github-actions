from pydantic import BaseModel

class BookingRequest(BaseModel):
    """
    Represents a booking request with necessary details.
    """
    customer_name: str
    appointment_date:str 
    appointment_time:str

class BookingResponse(BaseModel):
    """
     Represents the response after booking an appointment.
    """
    status: str
    message: str

class AppointmentResponse(BookingRequest):
    """
    Response schema for an appointment.
    """
    id: int

    # You may create this schema directly from a SQLAlchemy model.
    # FastAPI and Pydantic will automatically convert SQLAlchemy objects into JSON responses.
    model_config = {
        "from_attributes": True
    }