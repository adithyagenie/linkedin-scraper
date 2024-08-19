from config import DATABASE_URI
from sqlalchemy import and_, create_engine, exists, select
from sqlalchemy.orm import sessionmaker

from .models import Base, Company, JobExperience, User

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

def get_urn_ids() -> list[str]:
    session = Session()
    res = session.execute(select(User.urn_id))
    urn_ids = [row[0] for row in res]
    session.close()
    return urn_ids


def user_exists(urn_id):
    session = Session()
    does_exist = session.query(exists().where(User.urn_id == urn_id)).scalar()
    session.close()
    return does_exist

def update_user(urn_id, **kwargs):
    session = Session()
    try:
        user = session.query(User).filter(User.urn_id == urn_id).first()
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
                else:
                    raise ValueError(f"User object has no attribute '{key}'")
            session.commit()
            return True
        else:
            return False
    finally:
        session.close()

def delete_user(urn_id):
    session = Session()
    user = session.query(User).filter_by(urn_id=urn_id).first()
    if user:
        session.delete(user)
        session.commit()
    session.close()

def create_company(urn, name):
    session = Session()
    new_company = Company(urn=urn, name=name)
    session.add(new_company)
    session.commit()
    company_id = new_company.id
    session.close()
    return company_id

def get_company(identifier, by_urn=False):
    session = Session()
    try:
        if by_urn:
            company = session.query(Company).filter(Company.urn == str(identifier)).first()
        else:
            company = session.query(Company).filter(Company.id == int(identifier)).first()
        
        return company
    finally:
        session.close()

def company_exists(urn):
    session = Session()
    does_exist = session.query(exists().where(Company.urn == urn)).scalar()
    session.close()
    return does_exist

# JobExperience operations
def create_job_experience(person_id, company_id, job_title, location, start_date, end_date, is_current):
    session = Session()
    new_job_exp = JobExperience(
        person_id=person_id,
        company_id=company_id,
        job_title=job_title,
        location=location,
        start_date=start_date,
        end_date=end_date,
        is_current=is_current
    )
    session.add(new_job_exp)
    session.commit()
    job_exp_id = new_job_exp.id
    session.close()
    return job_exp_id

def get_job_experiences(person_id):
    session = Session()
    job_exps = session.query(JobExperience).filter_by(person_id=person_id).all()
    session.close()
    return job_exps

def job_experience_exists(person_id, company_id, job_title):
    session = Session()
    try:
        does_exist = session.query(exists().where(
            and_(
                JobExperience.person_id == person_id,
                JobExperience.company_id == company_id,
                JobExperience.job_title == job_title
            )
        )).scalar()
        return does_exist
    finally:
        session.close()