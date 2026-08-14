from app.ai.prompts import SYSTEM_PROMPT
from app.schemas.chat import ChatIntent
import re
from app.schemas.chat import ChatBookingData, ChatIntent, ChatUpdateData, ChatCancelData

class BookingAgent:
    """
    AI agent responsible for understanding
    user messages and detecting user intent.
    """

    @staticmethod
    def process_message(message: str) -> str:
        """
        Detect the user's intent.

        Args:
           message (str): User message.

        Returns:
           ChatIntent: Detected intent.
        """
        message = message.strip().lower()

        if not message:
            return ChatIntent(intent="empty")

        if any(word in message for word in ["hi", "hello", "hey"]):
            return ChatIntent(intent="greeting")

        if "book" in message:
            return ChatIntent(intent="book_appointment")

        if "appointment" in message and (
            "show" in message or "view" in message
        ):
            return ChatIntent(intent="show_appointments")

        if "update" in message:
            return ChatIntent(intent="update_appointment")

        if "cancel" in message or "delete" in message:
            return ChatIntent(intent="cancel_appointment")

        return ChatIntent(intent="unknown")
    
    @staticmethod
    def extract_booking_data(message: str) -> ChatBookingData:
        """
        Extract booking details from a user's message.
        """

        customer_name = None
        appointment_date = None
        appointment_time = None

        # Match: for Chandra
        name_match = re.search(
            r"for\s+([A-Za-z ]+?)\s+on",
            message,
            re.IGNORECASE,
        )

        if name_match:
            customer_name = name_match.group(1).strip()

        # Match: 2026-09-10
        date_match = re.search(
            r"\d{4}-\d{2}-\d{2}",
            message,
        )

        if date_match:
            appointment_date = date_match.group()

        # Time Match: 11:00 AM
        time_match = re.search(
            r"\d{1,2}:\d{2}\s?(AM|PM)",
            message,
            re.IGNORECASE,
        )

        if time_match:
            appointment_time = time_match.group().upper()

        return ChatBookingData(
            customer_name=customer_name,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
        )

    @staticmethod
    def extract_update_data(message: str) -> ChatUpdateData:
        """
        Extract update details from a user's message.
        """
        appointment_id = None
        customer_name = None
        appointment_date = None
        appointment_time = None

        # Id match:  appointment 4
        id_match = re.search(
            r"appointment\s+(\d+)",
            message,
            re.IGNORECASE
        )
        if id_match:
            appointment_id =int(id_match.group(1))

        # Match: for Rahul
        name_match =re.search(
            r"for\s+([A-Za-z ]+?)(?=\s+(?:to|on|at)\s+)",
            message,
            re.IGNORECASE
        )
        if name_match:
            customer_name = name_match.group(1).strip()

        # Match: 2026-09-30
        date_match = re.search(
            r"\d{4}-\d{2}-\d{2}",
            message,
        )
        if date_match:
            appointment_date= date_match.group()

        # Time match: 2:30 PM
        time_match= re.search(
            r"\d{1,2}:\d{2}\s?(AM|PM)",
            message,
            re.IGNORECASE
        )
        if time_match:
            appointment_time=time_match.group().upper()

        return ChatUpdateData(
            appointment_id=appointment_id,
            customer_name= customer_name,
            appointment_date=appointment_date,
            appointment_time=appointment_time
        )

    @staticmethod
    def extract_cancel_data(message: str) -> ChatCancelData:
        """
        Extract cancellation details from a user's message.
        """

        appointment_id = None
        customer_name = None

        # Match: appointment 11
        id_match =re.search(
            r"appointment\s+(\d+)",
            message,
            re.IGNORECASE
        )
        if id_match:
            appointment_id = int(id_match.group(1))

        # Match:
        # Cancel Kiran's appointment
        # Cancel Kiran appointment
        # Delete Rahul's appointment
        name_match = re.search(
            r"(?:cancel|delete)\s+([A-Za-z ]+?)(?:'s)?\s+appointment",
            message,
            re.IGNORECASE
        )

        if name_match:
            customer_name = name_match.group(1).strip()

        return ChatCancelData(
            appointment_id=appointment_id,
            customer_name=customer_name,
        )

        
