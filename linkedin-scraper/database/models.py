from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    urn_id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<User(urn_id='{self.urn_id}', name='{self.name}', location='{self.location}')>"
