from sqlalchemy import (
    Boolean,
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    urn_id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255))
    alumni = Column(Boolean, default=False)
    job_experiences = relationship("JobExperience", back_populates="user")
    school_experiences = relationship("SchoolExperience", back_populates="user")

    def __repr__(self):
        return f"<User(urn_id='{self.urn_id}', name='{self.name}', location='{self.location}', alumni='{self.alumni}')>"

class Company(Base):
    __tablename__ = 'company'

    id = Column(Integer, primary_key=True)
    urn = Column(String(50), unique=True)
    name = Column(String(255), nullable=False)
    job_experiences = relationship("JobExperience", back_populates="company")

    def __repr__(self):
        return f"<Company(id={self.id}, urn='{self.urn}', name='{self.name}')>"

class JobExperience(Base):
    __tablename__ = 'jobexp'

    person_id = Column(String(50), ForeignKey('users.urn_id'), primary_key=True)
    company_id = Column(Integer, ForeignKey('company.id'), primary_key=True)
    job_title = Column(String(255), nullable=False, primary_key=True)
    location = Column(String(255))
    start_date = Column(Date, nullable=False, primary_key=True)
    end_date = Column(Date)
    is_current = Column(Boolean, nullable=False)

    user = relationship("User", back_populates="job_experiences")
    company = relationship("Company", back_populates="job_experiences")

    def __repr__(self):
        return f"<JobExperience(person_id='{self.person_id}', company_id={self.company_id}, job_title='{self.job_title}', start_date='{self.start_date}')>"

class School(Base):
    __tablename__ = 'school'

    id = Column(Integer, primary_key=True)
    urn = Column(String(100), unique=True)
    name = Column(String(255), nullable=False)
    school_experiences = relationship("SchoolExperience", back_populates="school")

    def __repr__(self):
        return f"<School(id={self.id}, urn='{self.urn}', name='{self.name}')>"

class SchoolExperience(Base):
    __tablename__ = 'schoolexp'

    person_id = Column(String(50), ForeignKey('users.urn_id'), primary_key=True)
    school_id = Column(Integer, ForeignKey('school.id'), primary_key=True)
    degree = Column(String(255), nullable=False, default='NOTSET', primary_key=True)
    field = Column(String(255))
    grade = Column(Float)
    start_date = Column(Date)
    end_date = Column(Date)
    is_current = Column(Boolean)

    __table_args__ = (UniqueConstraint('person_id', 'school_id', 'degree', name='schoolexp_uniq'), )

    user = relationship("User", back_populates="school_experiences")
    school = relationship("School", back_populates="school_experiences")

    def __repr__(self):
        return f"<SchoolExperience(person_id='{self.person_id}', school_id={self.school_id}, degree='{self.degree}', field='{self.field}')>"
