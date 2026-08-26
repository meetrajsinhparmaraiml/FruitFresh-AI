import uuid
import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()


class ScanStatus(str, enum.Enum):
    OK = "OK"
    UNCERTAIN = "UNCERTAIN"
    FAILED = "FAILED"


class IssueSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Scan(Base):
    __tablename__ = "scans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fruit_type = Column(String(32), nullable=False)
    status = Column(SAEnum(ScanStatus), nullable=False, default=ScanStatus.OK)
    image_uri = Column(String(256), nullable=True)
    bbox_x1 = Column(Float, nullable=True)
    bbox_y1 = Column(Float, nullable=True)
    bbox_x2 = Column(Float, nullable=True)
    bbox_y2 = Column(Float, nullable=True)
    detection_confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    result = relationship("ScanResult", back_populates="scan", uselist=False, cascade="all, delete-orphan")
    issues = relationship("DetectedIssueRecord", back_populates="scan", cascade="all, delete-orphan")


class ScanResult(Base):
    __tablename__ = "scan_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(String(36), ForeignKey("scans.id"), nullable=False, unique=True)
    score = Column(Integer, nullable=True)
    label = Column(String(64), nullable=True)
    analysis = Column(Text, nullable=False)
    model_version = Column(String(32), nullable=False, default="cv_baseline_v1")
    rules_version = Column(String(32), nullable=False, default="rules_v1")

    scan = relationship("Scan", back_populates="result")


class DetectedIssueRecord(Base):
    __tablename__ = "detected_issues"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(String(36), ForeignKey("scans.id"), nullable=False)
    issue_type = Column(String(64), nullable=False)
    severity = Column(SAEnum(IssueSeverity), nullable=False)
    confidence = Column(Float, nullable=False)

    scan = relationship("Scan", back_populates="issues")
