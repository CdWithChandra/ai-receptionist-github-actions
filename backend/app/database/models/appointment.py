from sqlalchemy import Column, Integer, String, DateTime
from app.database.session import Base

# This class represents a database table. 
class Appointment(Base):
 """
    Database model for appointments.
 """
 __tablename__ ="appointments"
 id = Column(
      Integer, 
      primary_key=True, 
      index=True)

 customer_name= Column(
        String,
        nullable=False
    )

 appointment_date = Column(
        String,
        nullable=False
    )

 appointment_time = Column(
        String,
        nullable=False
    )