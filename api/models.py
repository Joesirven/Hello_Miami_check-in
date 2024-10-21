from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional, List
import enum


# Enum Definitions
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


class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"


class OTPStatus(enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"


# SQLModel Definitions
class UserBase(SQLModel):
    email: str
    password: str
    role: UserRole


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class ContactBase(SQLModel):
    name: str
    phone_number: str
    email: str


class Contact(ContactBase, table=True):
    contact_id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("UTC")))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("UTC")), sa_column_kwargs={"onupdate": datetime.now(ZoneInfo("UTC"))})
    interactions: List["Interaction"] = Relationship(back_populates="contact")
    messages: List["Message"] = Relationship(back_populates="contact")
    otps: List["OTP"] = Relationship(back_populates="contact")
    blasts: List["Blast"] = Relationship(back_populates="recipients", link_model="BlastRecipient")


class InteractionBase(SQLModel):
    contact_id: int
    message: str
    direction: MessageDirection


class Interaction(InteractionBase, table=True):
    interaction_id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("UTC")), sa_column_kwargs={"onupdate": datetime.now(ZoneInfo("UTC"))})
    status: Status = Field(default=Status.PENDING)
    error_message: Optional[str] = None
    contact: "Contact" = Relationship(back_populates="interactions")


class MessageBase(SQLModel):
    contact_id: int
    blast_id: Optional[int] = None
    type: MessageType
    direction: MessageDirection
    content: str
    html_content: Optional[str] = None
    subject: Optional[str] = None
    scheduled_time: Optional[datetime] = None


class Message(MessageBase, table=True):
    message_id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("UTC")), sa_column_kwargs={"onupdate": datetime.now(ZoneInfo("UTC"))})
    status: Status = Field(default=Status.PENDING)
    contact: "Contact" = Relationship(back_populates="messages")
    blast: "Blast" = Relationship(back_populates="messages")


class BlastBase(SQLModel):
    name: str
    type: MessageType
    content: str
    html_content: Optional[str] = None
    subject: Optional[str] = None
    media_urls: Optional[str] = None
    scheduled_time: Optional[datetime] = None


class Blast(BlastBase, table=True):
    blast_id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("UTC")))
    status: Status = Field(default=Status.PENDING)
    messages: List["Message"] = Relationship(back_populates="blast")
    recipients: List["Contact"] = Relationship(back_populates="blasts", link_model="BlastRecipient")
    blast_recipients: List["BlastRecipient"] = Relationship(back_populates="blast")


class BlastRecipient(SQLModel, table=True):
    blast_id: int = Field(foreign_key="blast.blast_id", primary_key=True)
    contact_id: int = Field(foreign_key="contact.contact_id", primary_key=True)
    blast: "Blast" = Relationship(back_populates="blast_recipients")
    contact: "Contact" = Relationship(back_populates="blasts")


class OTPBase(SQLModel):
    contact_id: int
    channel: str


class OTP(OTPBase, table=True):
    otp_id: Optional[int] = Field(default=None, primary_key=True)
    status: OTPStatus = Field(default=OTPStatus.PENDING)
    created_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("UTC")))
    verification_sid: str
    contact: "Contact" = Relationship(back_populates="otps")


class OTPVerify(SQLModel):
    contact_id: int
    code: str
