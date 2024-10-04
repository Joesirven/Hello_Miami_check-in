from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Enum,
    Text,
    ARRAY
)
from sqlalchemy.orm import relationship
from datetime import datetime
from zoneinfo import ZoneInfo
import enum
from api.db.database import Base


class MessageType(enum.Enum):
    EMAIL = "email"
    SMS = "sms"


class MessageDirection(enum.Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class Status(enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"


class Contact(Base):
    __tablename__ = "contacts"

    contact_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone_number = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(ZoneInfo("UTC"))
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(ZoneInfo("UTC")),
        onupdate=lambda: datetime.now(ZoneInfo("UTC"))
    )
    interactions = relationship("Interaction", back_populates="contact")
    messages = relationship("Message", back_populates="contact")
    otps = relationship("OTP", back_populates="contact")
    blasts = relationship(
        "Blast",
        secondary="blast_recipients",
        back_populates="recipients",
        overlaps="blasts_recipients"
    )
    blasts_recipients = relationship(
        "BlastRecipient",
        back_populates="contact",
        overlaps="blasts"
    )


class Interaction(Base):
    __tablename__ = "interactions"

    interaction_id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.contact_id"), index=True)
    message = Column(String)
    direction = Column(String)
    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(ZoneInfo("UTC"))
    )
    status = Column(Enum(Status), default=Status.PENDING)
    error_message = Column(String, nullable=True)

    contact = relationship("Contact", back_populates="interactions")


class Message(Base):
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.contact_id"), index=True)
    blast_id = Column(
        Integer,
        ForeignKey("blasts.blast_id"),
        nullable=True,
        index=True
    )
    type = Column(Enum(MessageType))
    direction = Column(Enum(MessageDirection))
    content = Column(Text)  # Use Text for longer content, supports emojis
    html_content = Column(Text, nullable=True)  # For HTML emails
    subject = Column(String, nullable=True)  # For emails
    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(ZoneInfo("UTC"))
    )
    status = Column(Enum(Status), default=Status.PENDING)
    scheduled_time = Column(DateTime(timezone=True), nullable=True)

    contact = relationship("Contact", back_populates="messages")
    blast = relationship("Blast", back_populates="messages")


class Blast(Base):
    __tablename__ = "blasts"

    blast_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    type = Column(Enum(MessageType))
    content = Column(Text)  # Plain text content
    html_content = Column(Text, nullable=True)  # HTML content for email blasts
    subject = Column(String, nullable=True)  # For email blasts
    media_urls = Column(ARRAY(String), nullable=True)  # New field for media
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(ZoneInfo("UTC"))
    )
    status = Column(Enum(Status), default=Status.PENDING)
    scheduled_time = Column(DateTime(timezone=True), nullable=True)

    messages = relationship("Message", back_populates="blast")
    recipients = relationship(
        "Contact",
        secondary="blast_recipients",
        back_populates="blasts",
        overlaps="blasts_recipients"
    )
    blast_recipients = relationship(
        "BlastRecipient",
        back_populates="blast",
        overlaps="recipients"
    )


class BlastRecipient(Base):
    __tablename__ = "blast_recipients"

    blast_id = Column(
        Integer,
        ForeignKey("blasts.blast_id"),
        primary_key=True
    )
    contact_id = Column(
        Integer,
        ForeignKey("contacts.contact_id"),
        primary_key=True
    )

    blast = relationship(
        "Blast",
        back_populates="blast_recipients",
        overlaps="recipients"
    )
    contact = relationship(
        "Contact",
        back_populates="blasts_recipients",
        overlaps="blasts"
    )


class OTPStatus(enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"


class OTP(Base):
    __tablename__ = "otps"

    otp_id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.contact_id"), index=True)
    channel = Column(String)  # e.g., "sms", "email", "whatsapp"
    status = Column(Enum(OTPStatus), default=OTPStatus.PENDING)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(ZoneInfo("UTC"))
    )
    verification_sid = Column(String)  # Twilio's verification SID

    contact = relationship("Contact", back_populates="otps")
