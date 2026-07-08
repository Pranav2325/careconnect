# This file defines the structure of our database tables using SQLAlchemy

from sqlalchemy import Column,Integer,String,ForeignKey,DateTime,Boolean,Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

# Base is the parent class all our tables inherit from
# This lets SQLAlchemy know "these classes represent database tables"
Base= declarative_base()

class Family(Base):
    __tablename__="families"
    id=Column(Integer,primary_key=True)
    name=Column(String,nullable=False)
    created_at=Column(DateTime,default=datetime.utcnow)
    
    # One family can have many users and many patients
    users=relationship("User",back_populates="family")
    patients=relationship("Patient",back_populates="family")
    
class User(Base):
    __tablename__="users"
    
    id = Column(Integer, primary_key=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="member")  # e.g. "admin", "member"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    family = relationship("Family", back_populates="users")
    
class Patient(Base):
    __tablename__="patients"
    
    id = Column(Integer, primary_key=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=True)
    blood_group = Column(String, nullable=True)
    conditions = Column(Text, nullable=True)  # e.g. "Diabetes, BP, Heart condition"
    allergies = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    family = relationship("Family", back_populates="patients")
    medicines = relationship("Medicine", back_populates="patient")
    doctors = relationship("Doctor", back_populates="patient")
    
class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    name = Column(String, nullable=False)
    specialization = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    hospital = Column(String, nullable=True)

    patient = relationship("Patient", back_populates="doctors")
    medicines = relationship("Medicine", back_populates="prescribed_by_doctor")   

class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=True)
    name = Column(String, nullable=False)
    dosage = Column(String, nullable=True)  # e.g. "500mg"
    timing = Column(String, nullable=True)  # e.g. "Morning, Night after food"
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="medicines")
    prescribed_by_doctor = relationship("Doctor", back_populates="medicines") 

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    sources = Column(Text, nullable=True)  # comma separated filenames
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient")
    
class Vital(Base):
    __tablename__="vitals"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    vital_type = Column(String, nullable=False)
    value = Column(String, nullable=False)
    value_secondary = Column(String, nullable=True)  # for BP diastolic
    unit = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient")