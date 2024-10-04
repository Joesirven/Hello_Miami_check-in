from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from enum import Enum


class MessageType(Enum):
    SMS = "sms"
    EMAIL = "email"


class MessageDirection(Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class InteractionStatus(Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"


class MessageStatus(Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"


class ContactBase(BaseModel):
    name: str
    phone_number: str


class ContactCreate(ContactBase):
    pass


class Contact(ContactBase):
    contact_id: int

    class Config:
        from_attributes = True


class ContactUpdate(ContactBase):
    name: Optional[str] = None
    phone_number: Optional[str] = None


class InteractionBase(BaseModel):
    contact_id: int
    message: str
    direction: MessageDirection


class InteractionCreate(InteractionBase):
    pass


class Interaction(InteractionBase):
    interaction_id: int
    timestamp: datetime
    status: InteractionStatus
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class MessageBase(BaseModel):
    contact_id: int
    blast_id: Optional[int] = None
    type: MessageType
    direction: MessageDirection
    content: str
    subject: Optional[str] = None
    html_content: Optional[str] = None
    media_urls: Optional[List[str]] = None
    scheduled_time: Optional[datetime] = None


class MessageCreate(MessageBase):
    pass


class Message(MessageBase):
    message_id: int
    scheduled_time: Optional[datetime] = None
    status: MessageStatus

    class Config:
        from_attributes = True


class BlastBase(BaseModel):
    name: str
    type: MessageType
    content: str
    html_content: Optional[str] = None
    subject: Optional[str] = None
    media_urls: Optional[List[str]] = None
    scheduled_time: Optional[datetime] = None


class BlastCreate(BlastBase):
    recipient_ids: List[int]


class Blast(BlastBase):
    blast_id: int
    created_at: datetime
    status: InteractionStatus

    class Config:
        from_attributes = True


class BlastUpdate(BlastBase):
    name: Optional[str] = None
    content: Optional[str] = None
    html_content: Optional[str] = None
    subject: Optional[str] = None
    media_urls: Optional[List[str]] = None
    scheduled_time: Optional[datetime] = None
    status: Optional[InteractionStatus] = None


class BlastDelete(BaseModel):
    id: int


class BlastSchedule(BaseModel):
    id: int
    scheduled_time: datetime


class BlastCancel(BaseModel):
    id: int


class OTPStatus(Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"


class OTPBase(BaseModel):
    contact_id: int
    channel: str


class OTPCreate(OTPBase):
    pass


class OTP(OTPBase):
    otp_id: int
    status: OTPStatus
    created_at: datetime
    verification_sid: str

    class Config:
        from_attributes = True


class OTPVerify(BaseModel):
    contact_id: int
    code: str
