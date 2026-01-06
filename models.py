from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class CognitiveSession(Base):
    __tablename__ = "cognitive_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    input_data = Column(Text)
    output_data = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")

class ConsciousnessMetrics(Base):
    __tablename__ = "consciousness_metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    phi_value = Column(Float)
    consciousness_level = Column(Float)
    workspace_capacity = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")