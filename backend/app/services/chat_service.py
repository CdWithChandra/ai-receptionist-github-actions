from sqlalchemy.orm import Session
import re

from app.ai.booking_agent import BookingAgent
from app.schemas.booking import BookingRequest
from app.schemas.chat import ChatIntent, ChatResponse
from app.services.booking_service import BookingService
from app.services.conversation_manager import ConversationManager
from app.services.ai_service import AIService


class ChatService:
    """
    Service class for handling chat-related operations.
    """

    @staticmethod
    def get_response(message: str, db: Session) -> ChatResponse:
        """
        Generate a response based on the detected intent.
        """
        state =ConversationManager.get_state()

        # Continue an existing booking conversation
        if (
            state["intent"]=="book_appointment"
            and state["waiting_for"] == "customer_name"
        ):
            ConversationManager.update_state(
                customer_name = message.strip(),
                waiting_for = "appointment_date",
            ) 
            return ChatResponse (
                reply="What appointment date would you like? (YYYY-MM-DD)"
            )
        
        if (
            state["intent"] == "book_appointment"
            and state["waiting_for"] == "appointment_date"
        ):
            appointment_date = message.strip()

            # Validate date format: YYYY-MM-DD
            if not re.fullmatch(
                r"\d{4}-\d{2}-\d{2}",
                appointment_date,
            ):
                return ChatResponse(
                    reply="Please enter the appointment date in YYYY-MM-DD format."
                )
 
            ConversationManager.update_state(
                appointment_date = appointment_date,
                waiting_for="appointment_time",
            )
            return ChatResponse(
                reply="What appointment time would you like? (e.g., 10:30 AM)"     
         )

        
        if (
            state["intent"] == "book_appointment"
            and state["waiting_for"] == "appointment_time"
        ):
            appointment_time = message.strip().upper()
            # Validate time format: HH:MM AM/PM
            if not re.fullmatch(
                r"(0?[1-9]|1[0-2]):[0-5][0-9]\s?(AM|PM)",
                appointment_time,
            ):
                return ChatResponse(
                    reply="Please enter the appointment time in a valid format, "
                    "for example 10:30 AM."
                )
            ConversationManager.update_state(
                appointment_time= appointment_time,
            )
            state = ConversationManager.get_state()
            request= BookingRequest(
                customer_name=state["customer_name"],
                appointment_date=state["appointment_date"],
                appointment_time=state["appointment_time"],
            )
            result = BookingService.book_appointment(
                request,
                db,
            )

            if result.status == "error":
                return ChatResponse(
                    reply=result.message
                )
            ConversationManager.clear_state()
            return ChatResponse(
                reply=result.message
            )

        # Detect a new intent
        detected_intent: ChatIntent = BookingAgent.process_message(message)

        if detected_intent.intent == "empty":
            return ChatResponse(
                reply="Please enter a valid message."
            )

        if detected_intent.intent == "greeting":
            return ChatService._handle_greeting()

        if detected_intent.intent == "book_appointment":
            return ChatService._handle_booking(message, db)

        if detected_intent.intent == "show_appointments":
            return ChatService._handle_show_appointments(db)

        if detected_intent.intent == "update_appointment":
            return ChatService._handle_update(message, db)
        
        if detected_intent.intent == "cancel_appointment":
            return ChatService._handle_cancel(message, db)

        return AIService.get_ai_response(message)

    @staticmethod
    def _handle_greeting() -> ChatResponse:
        """
        Handle greeting messages.
        """
        return ChatResponse(
            reply="Hello! Welcome to AI Receptionist. How can I help you today?"
        )
    
    @staticmethod
    def _handle_booking(
        message: str,
        db: Session,       
    ) -> ChatResponse:
        """
        Handle appointment booking requests.
        """
        state = ConversationManager.get_state()
        booking_data = BookingAgent.extract_booking_data(message)
        if (
            booking_data.customer_name is None 
            and booking_data.appointment_date is None
            and booking_data.appointment_time is None
        ):
            ConversationManager.update_state(
                intent="book_appointment",
                waiting_for="customer_name",
            )
            return ChatResponse(
                reply="Sure! What's the customer's name?"
            )
        if (
            booking_data.customer_name is None
            or booking_data.appointment_date is None
            or booking_data.appointment_time is None
        ):
            return ChatResponse(
                reply=(
                    "Please provide the customer's name, "
                    "appointment date (YYYY-MM-DD), "
                    "and appointment time."
                )
            )
        request =BookingRequest (
            customer_name=booking_data.customer_name,
            appointment_date=booking_data.appointment_date,
            appointment_time=booking_data.appointment_time
        )
        request = BookingRequest(
            customer_name = booking_data.customer_name,
            appointment_date = booking_data.appointment_date,
            appointment_time = booking_data.appointment_time
        )
        result = BookingService.book_appointment(
            request,db
        )
        ConversationManager.clear_state()
        return ChatResponse(
            reply=result.message
        )
    
    @staticmethod
    def _handle_show_appointments(
            db: Session
    ) -> ChatResponse:
        """
        Handle requests to view appointments.
        """
        appointments = BookingService.get_appointments(db)
        if not appointments:
            return ChatResponse(
                reply="There are no appointments scheduled."
            )
        lines = ["Here are your appointments:\n"]
        for appointment in appointments:
            lines.append(
                f"{appointment.id}. "
                f"{appointment.customer_name} - "
                f"{appointment.appointment_date} - "
                f"{appointment.appointment_time}"
            )
        return ChatResponse(
            reply="\n".join(lines)
        )
    @staticmethod
    def _handle_update(message: str,
                       db: Session) -> ChatResponse:
         """
         Handle update appointment requests.
         """
         update_data = BookingAgent.extract_update_data(message)
         if (
             update_data.appointment_id is None
             or update_data.customer_name is None
             or update_data.appointment_date is None
             or update_data.appointment_time is None
         ):
             return ChatResponse (
                 reply= (
                     "Please provide the appointment ID, "
                     "customer name, new date (YYYY-MM-DD), "
                     "and new time."
                 )
             )
         request= BookingRequest(
             customer_name=update_data.customer_name,
             appointment_date=update_data.appointment_date,
             appointment_time=update_data.appointment_time,
         )

         result = BookingService.update_appointment(
             update_data.appointment_id,
             request,
             db
         )
         if result.status== "error":
             return ChatResponse(
                 reply=result.message
             )

         return ChatResponse(
             reply=(
                 f"appointment {update_data.appointment_id} updated successfully "
                 f"for {update_data.customer_name} on "
                 f"{update_data.appointment_date} at "
                 f"{update_data.appointment_time}."
             )
         )

    @staticmethod
    def _handle_cancel(
        messsage: str,
        db: Session
    ) -> ChatResponse:
        """
        Handle appointment cancellation requests.
        """

        cancel_data = BookingAgent.extract_cancel_data(messsage)

        if cancel_data.appointment_id is not None:
            result = BookingService.delete_appointment(
                cancel_data.appointment_id,
                db
            )
            return ChatResponse(
                reply=result.message
            )

        # Cancel using customer name
        if cancel_data.customer_name is not None:
            appointments = BookingService.get_appointments(db)
            customer_appointments = [
                appointment 
                for appointment in appointments
                if appointment .customer_name.lower()
                == cancel_data.customer_name.lower()
            ]

            if not customer_appointments:
                return ChatResponse (
                    reply= (
                        f"No appointment found for "
                        f"{cancel_data.customer_name}."
                    )
                )

            # Only one appointment found
            if len(customer_appointments) == 1:
                result = BookingService.delete_appointment_by_name(
                    cancel_data.customer_name,
                    db
                )

                return ChatResponse(
                    reply=result.message
                )

            # Multiple appointments found
            appointment_list = "\n".join(
               (
                   f"{appointment.id}. "
                   f"{appointment.appointment_date} at "
                   f"{appointment.appointment_time}"
               )
               for appointment in customer_appointments
            )

            return ChatResponse (
                reply=(
                    f"{cancel_data.customer_name} has multiple appointments:\n"
                    f"{appointment_list}\n"
                    f"Please provide the appointment ID you want to cancel."
                )
            )
        
        return ChatResponse(
            reply=(
                "Please provide an appointment ID or customer name."  
            )
        )

    @staticmethod
    def _handle_unknown() -> ChatResponse:
        """
        Handle unknown requests.
        """
        return ChatResponse(
            reply= "I'm sorry, I didn't understand your request."
        )


