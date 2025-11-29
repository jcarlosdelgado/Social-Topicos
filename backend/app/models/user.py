from sqlalchemy import Column, Integer, String
<<<<<<< HEAD
from sqlalchemy.orm import relationship
=======
>>>>>>> edab826f1c006fb5c88c99504b503d04cf67df9a
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
<<<<<<< HEAD
    
    # Relationships
    publications = relationship("Publication", back_populates="user")
=======
>>>>>>> edab826f1c006fb5c88c99504b503d04cf67df9a
