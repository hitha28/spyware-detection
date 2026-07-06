from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # apk | exe | network
    status = Column(String, default="pending")  # pending | done | failed
    static_score = Column(Float, nullable=True)
    ml_score = Column(Float, nullable=True)
    final_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    indicators = relationship("Indicator", back_populates="scan")
    reports = relationship("Report", back_populates="scan")


class Indicator(Base):
    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    source = Column(String, nullable=False)  # yara | hash | apk | pe | ml
    description = Column(Text, nullable=False)
    severity = Column(String, nullable=False)  # low | medium | high | critical

    scan = relationship("Scan", back_populates="indicators")


class MLModel(Base):
    __tablename__ = "ml_models"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    trained_at = Column(DateTime(timezone=True), server_default=func.now())


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    summary = Column(Text, nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    scan = relationship("Scan", back_populates="reports")