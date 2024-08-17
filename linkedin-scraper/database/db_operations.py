from config import DATABASE_URI
from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker

from .models import Base, User

engine = create_engine(DATABASE_URI)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def create_user(urn_id, name, location):
    session = Session()
    new_user = User(urn_id=urn_id, name=name, location=location)
    session.add(new_user)
    session.commit()
    session.close()

def get_user(urn_id):
    session = Session()
    user = session.query(User).filter_by(urn_id=urn_id).first()
    session.close()
    return user

def user_exists(urn_id):
    session = Session()
    does_exist = session.query(exists().where(User.urn_id == urn_id)).scalar()
    session.close()
    return does_exist

def update_user(urn_id, **kwargs):
    session = Session()
    user = session.query(User).filter_by(urn_id=urn_id).first()
    if user:
        for key, value in kwargs.items():
            setattr(user, key, value)
        session.commit()
    session.close()

def delete_user(urn_id):
    session = Session()
    user = session.query(User).filter_by(urn_id=urn_id).first()
    if user:
        session.delete(user)
        session.commit()
    session.close()
