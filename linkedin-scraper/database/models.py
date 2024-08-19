from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    urn_id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    alumni = Column(Boolean, default=False)
    job_experiences = relationship("JobExperience", back_populates="user")

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

    id = Column(Integer, primary_key=True)
    person_id = Column(String(50), ForeignKey('users.urn_id'))
    company_id = Column(Integer, ForeignKey('company.id'))
    job_title = Column(String(255))
    location = Column(String(255))
    start_date = Column(Date)
    end_date = Column(Date)
    is_current = Column(Boolean)

    user = relationship("User", back_populates="job_experiences")
    company = relationship("Company", back_populates="job_experiences")

    def __repr__(self):
        return f"<JobExperience(id={self.id}, person_id='{self.person_id}', company_id={self.company_id}, job_title='{self.job_title}')>"
