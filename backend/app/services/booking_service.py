
from sqlalchemy.orm import Session
from app.database.models.appointment import Appointment
from app.schemas.booking import (AppointmentResponse, BookingRequest, BookingResponse)

class BookingService:
    """
    Service class for appointment booking operations.
    """

    @staticmethod
    def _check_duplicate(
        request: BookingRequest,
        db: Session
    ) -> BookingResponse | None:
        """
        Check whether the customer already has the same appointment.
        """
        existing_appointment =(
            db.query(Appointment)
            .filter(
                Appointment.customer_name == request.customer_name,
                Appointment.appointment_date == request.appointment_date,
                Appointment.appointment_time == request.appointment_time,
            )
            .first()
        )

        if existing_appointment:
            return BookingResponse(
                status= "error",
                message=(
                    f"{request.customer_name} already has an appointment "
                    f"on {request.appointment_date} at "
                    f"{request.appointment_time}."
                )
            )
        return None


    @staticmethod
    def _check_duplicate_for_update(
        appointment_id: int,
        request: BookingRequest,
        db: Session
    ) -> BookingResponse | None:
        """
        Check for duplicate appointments while excluding
        the appointment being updated.
        """
        existing_appointment =(
            db.query(Appointment)
            .filter(
                Appointment.id != appointment_id,
                Appointment.customer_name == request.customer_name,
                Appointment.appointment_date == request.appointment_date,
                Appointment.appointment_time == request.appointment_time,
            )
            .first()
        )

        if existing_appointment:
            return BookingResponse(
                status="error",
                message=(
                    f"{request.customer_name} already has an appointment "
                    f"on {request.appointment_date} at "
                    f"{request.appointment_time}."
                )
            )
        return None

    @staticmethod
    def _check_time_slot_for_update(
        appointment_id: int,
        request: BookingRequest,
        db: Session
    ) -> BookingResponse | None:
        """
        Check whether the requested time slot is already booked,
        excluding the appointment being updated.
        """

        conflicting_appointment = (
            db.query(Appointment)
            .filter(
                Appointment.id != appointment_id,
                Appointment.appointment_date == request.appointment_date,
                Appointment.appointment_time == request.appointment_time,
            )
            .first()
        )

        if conflicting_appointment:
            return BookingResponse(
                status="error",
                message=(
                    f"Sorry, the time slot "
                    f"{request.appointment_time} on "
                    f"{request.appointment_date} "
                    f"is already booked. "
                    f"Please choose another time."
                )
            )
        return None

    @staticmethod
    def _check_time_slot(
        request: BookingRequest,
        db: Session,
    ) -> BookingResponse | None:
        """
        Check whether the requested time slot is already booked.
        """
        conflicting_appointment = (
            db.query(Appointment)
            .filter(
                Appointment.appointment_date == request.appointment_date,
                Appointment.appointment_time == request.appointment_time,
            )
            .first()
        )
        if conflicting_appointment:
            return BookingResponse(
                status ="error",
                message=(
                    f"Sorry, the time slot "
                    f"{request.appointment_time} on "
                    f"{request.appointment_date} "
                    f"is already booked. "
                    f"Please choose another time."
                )
            )
        return None

    
    @staticmethod
    def book_appointment(
        request: BookingRequest,
        db: Session) -> BookingResponse:
        """
       Save an appointment to the database. 

        Args:
            request (BookingRequest): Appointment details.
            db (Session): Database session.

        Returns:
            BookingResponse: Booking confirmation.
        """
        # Check for duplicate appointment
        duplicate_result = BookingService._check_duplicate(
            request,
            db
        )
        if duplicate_result:
            return duplicate_result

        # Check whether the requested time slot is already booked
        conflict_result = BookingService._check_time_slot(
            request,db
        )
        if conflict_result:
            return conflict_result

         # Create new appointment
        appointment = Appointment(
            customer_name=request.customer_name,
            appointment_date=request.appointment_date,
            appointment_time=request.appointment_time
        )
        db.add(appointment)
        db.commit()
        db.refresh(appointment)


        return BookingResponse(
            status="success",
            message=(
                f"Appointment booked successfully for " 
                f"{request.customer_name} on "
                f"{request.appointment_date} at "
                f"{request.appointment_time} "
                ),
        )

    @staticmethod
    def get_appointments(
        db: Session,
    ) -> list[AppointmentResponse]:
        """
        Retrieve all appointments from the database.

        Args:
          db (Session): Database session.

        Returns:
         list[AppointmentResponse]: List of appointments.
        """
        appointments = db.query(Appointment).all()
        return appointments

    @staticmethod
    def update_appointment(
        appointment_id: int,
        request: BookingRequest,
        db: Session,
    ) -> BookingResponse:
      """
          Update an existing appointment.

      Args:
          appointment_id (int): Appointment ID.
          request (BookingRequest): Updated appointment details.
          db (Session): Database session.

    Returns:
        BookingResponse: Status message.
      """
      # Find one record based on filter criteria. If no record is found , return None.
      # Equivalent SQL: SELECT * FROM appointments WHERE id = appointment_id LIMIT 1;
      appointment = (
          db.query(Appointment)
          .filter(Appointment.id == appointment_id)
          .first()
     )
      if appointment is None:
          return BookingResponse(
              status="error",
              message=f"Appointment with ID {appointment_id} not found."
          )
      
      duplicate_result = BookingService._check_duplicate_for_update(
          appointment_id,
          request,
          db
      )

      if duplicate_result:
          return duplicate_result

      conflict_result = BookingService._check_time_slot_for_update(
          appointment_id,
          request,
          db
      )

      if conflict_result:
          return conflict_result

      # Update values
      if request.customer_name:
          appointment.customer_name = request.customer_name

      if request.appointment_date:
          appointment.appointment_date=request.appointment_date

      if request.appointment_time:
          appointment.appointment_time = request.appointment_time

      db.commit()
      db.refresh(appointment) #Reloads the object from the database to ensure it's synchronized with the latest stored values.

      return BookingResponse(
          status="success",
          message=(
              f"Appointment {appointment.id} updated successfully."
          )
         
      )

    @staticmethod
    def delete_appointment(
        appointment_id: int,
        db: Session,   
    ) -> BookingResponse:
        """
        Delete an existing appointment.

        Args:
            appointment_id (int): Appointment ID.
            db (Session): Database session.

        Returns:
            BookingResponse: Status message.
        """
        appointment = (
            db.query(Appointment)
            .filter(Appointment.id == appointment_id)
            .first()
        )
        if appointment is None:
            return BookingResponse(
                status="error",
                message=f"Appointment with ID {appointment_id} not found."
            )

        db.delete(appointment) # DELETE FROM appointments WHERE id = ?;
        db.commit()            # deletion is permanently saved to the database.

        return BookingResponse(
            status="success",
            message=f"Appointment {appointment_id} deleted successfully."
        )

    # Delete an appointment using the customer's name.
    @staticmethod
    def delete_appointment_by_name(
        customer_name: str,
        db: Session
    )-> BookingResponse:
        """
        Delete an appointment using the customer's name.
        """
        appointment = (
            db.query(Appointment)
            .filter(
                Appointment.customer_name == customer_name
            )
            .first()
        )

        if appointment is None:
            return BookingResponse(
                status="error",
                message=(
                    f"No appointment found for {customer_name}."
                )
            )
        db.delete(appointment)
        db.commit()

        return BookingResponse(
            status="success",
            message=(
                f"Appointment for {customer_name} "
                f"has been cancelled successfully."
            )
        )
    
