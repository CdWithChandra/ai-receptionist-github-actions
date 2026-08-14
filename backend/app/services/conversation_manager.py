class ConversationManager:
    """
    Manages the current conversation state.

    For now, conversation data is stored in memory.
    Later, this can be replaced with Redis or a database.
    """

    _conversation = {
        "intent": None,
        "customer_name": None,
        "appointment_date": None,
        "appointment_time": None,
        "waiting_for": None,
    }

    @classmethod
    def get_state(cls) -> dict:
        """
        Return the current conversation state.
        """
        return cls._conversation

    @classmethod
    def update_state(cls, **kwargs) -> None:
        """
        Update one or more conversation fields.
        """
        cls._conversation.update(kwargs)

    @classmethod
    def clear_state(cls) -> None:
        """
        Reset the conversation.
        """
        cls._conversation = {
            "intent": None,
            "customer_name": None,
            "appointment_date": None,
            "appointment_time": None,
            "waiting_for": None,
        }