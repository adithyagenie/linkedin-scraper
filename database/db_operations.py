from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from config import DATABASE_URI, UPDATE_HOURS
from sqlalchemy import and_, create_engine, exists, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

from .models import Base, Company, JobExperience, School, SchoolExperience, User

engine = create_engine(DATABASE_URI)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def create_user(urn_id, name, location=None, alumni=False):
    session = Session()
    new_user = User(urn_id=urn_id, name=name, location=location, alumni=alumni, last_updated_at=func.now())
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

def get_urn_ids_not_updated() -> list[str]:
    session = Session()
    try:
        hours_ago = datetime.now(ZoneInfo("UTC")) - timedelta(hours=UPDATE_HOURS)
        query = select(User.urn_id).where(User.last_updated_at < hours_ago)
        result = session.execute(query)
        urn_ids = [row[0] for row in result]
        return urn_ids
    finally:
        session.close()

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

def update_user_last_updated(urn_id):
    session = Session()
    try:
        user = session.query(User).filter(User.urn_id == urn_id).first()
        if user:
            user.last_updated_at = func.now()
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        print(f"Error updating user last_updated_at: {e}")
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
    session.close()

def get_job_experiences(person_id):
    session = Session()
    job_exps = session.query(JobExperience).filter_by(person_id=person_id).all()
    session.close()
    return job_exps

def job_experience_exists(person_id, company_id, job_title, start_date):
    session = Session()
    try:
        existing_job = session.query(JobExperience).filter(
            and_(
                JobExperience.person_id == person_id,
                JobExperience.company_id == company_id,
                JobExperience.job_title == job_title,
                JobExperience.start_date == start_date
            )
        ).first()
        
        return existing_job is not None
    finally:
        session.close()

def update_job_experience(person_id, company_id, job_title, start_date, **kwargs):
    session = Session()
    try:
        job_exp = session.query(JobExperience).filter(
            and_(
                JobExperience.person_id == person_id,
                JobExperience.company_id == company_id,
                JobExperience.job_title == job_title,
                JobExperience.start_date == start_date
            )
        ).first()
        if job_exp:
            for key, value in kwargs.items():
                if hasattr(job_exp, key):
                    setattr(job_exp, key, value)
                else:
                    raise ValueError(f"JobExperience object has no attribute '{key}'")
            session.commit()
            return True
        else:
            return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def upsert_job_experience(person_id, company_id, job_title, start_date, location=None, end_date=None, is_current=None):
    session = Session()
    try:
        # Prepare the insert statement
        insert_stmt = insert(JobExperience).values(
            person_id=person_id,
            company_id=company_id,
            job_title=job_title,
            start_date=start_date,
            location=location,
            end_date=end_date,
            is_current=is_current
        )

        # Prepare the "on conflict" part
        on_conflict_stmt = insert_stmt.on_conflict_do_update(
            index_elements=['person_id', 'company_id', 'job_title', 'start_date'],
            set_={
                'location': insert_stmt.excluded.location,
                'end_date': insert_stmt.excluded.end_date,
                'is_current': insert_stmt.excluded.is_current
            }
        )

        # Execute the upsert
        session.execute(on_conflict_stmt)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error in upsert_job_experience: {e}")
        return False
    finally:
        session.close()

def delete_user_job_experiences(person_id):
    session = Session()
    try:
        # Delete all job experiences for the given person_id
        session.query(JobExperience).filter(JobExperience.person_id == person_id).delete()
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error deleting job experiences: {e}")
        return False
    finally:
        session.close()

def create_school(urn, name):
    session = Session()
    new_school = School(urn=urn, name=name)
    session.add(new_school)
    session.commit()
    school_id = new_school.id
    session.close()
    return school_id

def get_school(identifier, by_urn=False):
    session = Session()
    try:
        if by_urn:
            school = session.query(School).filter(School.urn == str(identifier)).first()
        else:
            school = session.query(School).filter(School.id == int(identifier)).first()
        
        return school
    finally:
        session.close()

def school_exists(urn):
    session = Session()
    does_exist = session.query(exists().where(School.urn == urn)).scalar()
    session.close()
    return does_exist

# SchoolExperience operations
def create_school_experience(person_id, school_id, degree, field=None, grade=None, start_date=None, end_date=None, is_current=None):
    session = Session()
    new_school_exp = SchoolExperience(
        person_id=person_id,
        school_id=school_id,
        degree=degree,
        field=field,
        grade=grade,
        start_date=start_date,
        end_date=end_date,
        is_current=is_current
    )
    session.add(new_school_exp)
    session.commit()
    session.close()

def get_school_experiences(person_id):
    session = Session()
    school_exps = session.query(SchoolExperience).filter_by(person_id=person_id).all()
    session.close()
    return school_exps

def school_experience_exists(person_id, school_id):
    session = Session()
    try:
        existing_school_exp = session.query(SchoolExperience).filter(
            and_(
                SchoolExperience.person_id == person_id,
                SchoolExperience.school_id == school_id
            )
        ).first()
        
        return existing_school_exp is not None
    finally:
        session.close()

def update_school_experience(person_id, school_id, **kwargs):
    session = Session()
    try:
        school_exp = session.query(SchoolExperience).filter(
            and_(
                SchoolExperience.person_id == person_id,
                SchoolExperience.school_id == school_id
            )
        ).first()
        if school_exp:
            for key, value in kwargs.items():
                if hasattr(school_exp, key):
                    setattr(school_exp, key, value)
                else:
                    raise ValueError(f"SchoolExperience object has no attribute '{key}'")
            session.commit()
            return True
        else:
            return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def upsert_school_experience(person_id, school_id, degree, field=None, grade=None, start_date=None, end_date=None, is_current=None):
    session = Session()
    try:
        # Prepare the insert statement
        insert_stmt = insert(SchoolExperience).values(
            person_id=person_id,
            school_id=school_id,
            degree=degree,
            field=field,
            grade=grade,
            start_date=start_date,
            end_date=end_date,
            is_current=is_current
        )

        # Prepare the "on conflict" part
        on_conflict_stmt = insert_stmt.on_conflict_do_update(
            index_elements=['person_id', 'school_id', 'degree'],
            set_={
                'field': insert_stmt.excluded.field,
                'grade': insert_stmt.excluded.grade,
                'start_date': insert_stmt.excluded.start_date,
                'end_date': insert_stmt.excluded.end_date,
                'is_current': insert_stmt.excluded.is_current
            }
        )

        # Execute the upsert
        session.execute(on_conflict_stmt)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error in upsert_school_experience: {e}")
        return False
    finally:
        session.close()

def delete_user_school_experience(person_id):
    session = Session()
    try:
        # Delete all school experiences for the given person_id
        session.query(SchoolExperience).filter(SchoolExperience.person_id == person_id).delete()
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error deleting school experiences: {e}")
        return False
    finally:
        session.close()
