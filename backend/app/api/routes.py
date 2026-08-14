from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.booking import (
    AppointmentResponse,
    BookingRequest, 
    BookingResponse,
)
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.booking_service import BookingService
from app.services.chat_service import ChatService

router = APIRouter()

# # User endpoint for chat with AI receptionist
@router.post(
    "/chat",
    response_model=ChatResponse,
    tags=["Chat"]
)

def chat(request: ChatRequest,
         db: Session = Depends(get_db)
) -> ChatResponse:
    """
    Handle incoming chat messages.
    """
    return ChatService.get_response(
        request.message,
        db
    )

# Appointment booking endpoint
@router.post(
    "/booking",
    response_model=BookingResponse,
    tags=["Booking"]
)
def book_appointment(
    request: BookingRequest, 
    db: Session = Depends(get_db)

) -> BookingResponse:
    """
    Book an appointment.
    """
    return BookingService.book_appointment(request, db)


# Retrieve all appointments
@router.get(
    "/appointments",
    response_model=list[AppointmentResponse],
    tags=["Booking"],
)
def get_appointments(
    db: Session = Depends(get_db)
) -> list[AppointmentResponse]:
    """
    Retrieve all appointments.
    """
    return BookingService.get_appointments(db)


# Update an existing appointment 
@router.put(
    "/booking/{appointment_id}",
    response_model=BookingResponse,
    tags=["Booking"]
)
def update_appointment(
    appointment_id: int,
    request: BookingRequest,
    db: Session = Depends(get_db)
) -> BookingResponse:
    """
    Update an existing appointment.
    """
    result = BookingService.update_appointment(
        appointment_id, 
        request, 
        db,
    )

    if result.status == "error":
        raise HTTPException(
            status_code=404,
            detail=result.message,
        )
    return result



# Delete an existing appointment
@router.delete(
    "/booking/{appointment_id}",
    response_model=BookingResponse,
    tags=["Booking"]
)
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db)
) -> BookingResponse:
    """
    Delete an existing appointment.
    """
    # Call the service layer to handle the deletion logic and return the response.
    # No SQL, no business logic—just HTTP handling.
    result = BookingService.delete_appointment(
        appointment_id,
        db
    )
    if result.status == "error":
        raise HTTPException(
            status_code=404,
            detail=result.message,
        )

    return result

