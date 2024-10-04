from sqlalchemy.orm import Session
from api import models, schemas
from api.utils.twilio_helpers import TwilioSMS, TwilioVerify
from api.utils.mailersend_helpers import HTMLEmail, SimpleEmail
from typing import List, Optional
import asyncio


class BlastManager:
    def __init__(self, db: Session):
        self.db = db

    async def create_blast(self, blast: schemas.BlastCreate) -> models.Blast:
        db_blast = models.Blast(**blast.model_dump(exclude={"recipient_ids"}))

        for recipient_id in blast.recipient_ids:
            recipient = await self.db.query(models.Contact).filter(
                models.Contact.contact_id == recipient_id
            ).first()
            if recipient:
                db_blast.recipients.append(recipient)

        self.db.add(db_blast)
        await self.db.commit()
        await self.db.refresh(db_blast)
        return db_blast

    async def send_blast(self, blast_id: int):
        blast = self.db.query(
            models.Blast
        ).filter(
            models.Blast.blast_id == blast_id
        ).first()
        if not blast:
            return None

        if blast.type == models.MessageType.SMS:
            await self._send_sms_blast(blast)
        elif blast.type == models.MessageType.EMAIL:
            await self._send_email_blast(blast)
        else:
            raise ValueError(f"Unsupported message type: {blast.type}")

        blast.status = models.Status.SENT
        self.db.commit()
        return blast

    async def _send_sms_blast(self, blast: models.Blast):
        sms = TwilioSMS()
        tasks = []
        for recipient in blast.recipients:
            sms.set_recipient(recipient.phone_number)
            sms.set_message(blast.content)
            if blast.media_urls:
                sms.set_media_urls(blast.media_urls)
            if blast.scheduled_time:
                sms.set_scheduled_time(blast.scheduled_time)
            tasks.append(asyncio.create_task(
                self._send_sms(
                    sms,
                    recipient,
                    blast
                )
            )
            )
        await asyncio.gather(*tasks)

    async def _send_sms(
            self,
            sms: TwilioSMS,
            recipient: models.Contact,
            blast: models.Blast
    ):
        try:
            message_sid = sms.send()
            self._create_message(
                recipient,
                blast,
                models.Status.SENT,
                message_sid
            )
        except Exception as e:
            self._create_message(
                recipient,
                blast,
                models.Status.FAILED,
                str(e)
            )

    async def _send_email_blast(self, blast: models.Blast):
        tasks = []
        for recipient in blast.recipients:
            if blast.html_content:
                email = HTMLEmail()
                email.set_content(blast.html_content, blast.content)
            else:
                email = SimpleEmail()
                email.set_content(blast.content)
            email.set_subject(blast.subject)
            email.set_recipients([{"email": recipient.email}])
            if blast.scheduled_time:
                email.set_send_at(blast.scheduled_time)
            tasks.append(asyncio.create_task(
                self._send_email(
                    email,
                    recipient,
                    blast
                )
            )
            )
        await asyncio.gather(*tasks)

    async def _send_email(
            self,
            email: HTMLEmail | SimpleEmail,
            recipient: models.Contact,
            blast: models.Blast
    ):
        try:
            response = email.send()
            self._create_message(
                recipient,
                blast,
                models.Status.SENT,
                response.get('id')
            )
        except Exception as e:
            self._create_message(
                recipient,
                blast,
                models.Status.FAILED, str(e))

    def _create_message(
            self,
            recipient: models.Contact,
            blast: models.Blast,
            status: models.Status,
            message_id: str
    ):
        message = models.Message(
            contact_id=recipient.contact_id,
            blast_id=blast.blast_id,
            type=blast.type,
            direction=models.MessageDirection.OUTBOUND,
            content=blast.content,
            html_content=blast.html_content,
            subject=blast.subject,
            status=status,
            scheduled_time=blast.scheduled_time
        )
        self.db.add(message)
        self.db.commit()

    def get_blasts(
            self,
            skip: int = 0,
            limit: int = 100
    ) -> List[models.Blast]:
        return self.db.query(models.Blast).offset(skip).limit(limit).all()

    def get_blast(self, blast_id: int) -> Optional[models.Blast]:
        return self.db.query(models.Blast).filter(
            models.Blast.blast_id == blast_id
        ).first()

    def update_blast(
            self,
            blast_id: int,
            blast: schemas.BlastUpdate
    ) -> Optional[models.Blast]:
        db_blast = self.get_blast(blast_id)
        if db_blast:
            for key, value in blast.dict(exclude_unset=True).items():
                setattr(db_blast, key, value)
            self.db.commit()
            self.db.refresh(db_blast)
        return db_blast

    def delete_blast(self, blast_id: int) -> Optional[models.Blast]:
        db_blast = self.get_blast(blast_id)
        if db_blast:
            self.db.delete(db_blast)
            self.db.commit()
        return db_blast

    async def send_otp(self, contact_id: int, channel: str = "sms"):
        contact = await self.db.query(models.Contact).filter(
            models.Contact.contact_id == contact_id
        ).first()
        if not contact:
            raise ValueError("Contact not found")

        verify = TwilioVerify()
        result = verify.send_verification(contact.phone_number, channel)

        otp = models.OTP(
            contact_id=contact.contact_id,
            channel=channel,
            status=models.OTPStatus.PENDING,
            verification_sid=result['sid']
        )
        self.db.add(otp)
        self.db.commit()
        return otp

    async def verify_otp(self, contact_id: int, code: str):
        otp = self.db.query(models.OTP).filter(
            models.OTP.contact_id == contact_id,
            models.OTP.status == models.OTPStatus.PENDING
        ).order_by(models.OTP.created_at.desc()).first()

        if not otp:
            raise ValueError("No pending OTP found for this contact")

        verify = TwilioVerify()
        result = verify.check_verification(otp.contact.phone_number, code)

        if result['status'] == 'approved':
            otp.status = models.OTPStatus.VERIFIED
        else:
            otp.status = models.OTPStatus.FAILED

        self.db.commit()
        return otp


# For backwards compatibility and ease of use
async def create_blast(
        db: Session,
        blast: schemas.BlastCreate
) -> models.Blast:
    manager = BlastManager(db)
    return await manager.create_blast(blast)


async def send_blast(db: Session, blast_id: int):
    manager = BlastManager(db)
    return await manager.send_blast(blast_id)


def get_blasts(
        db: Session,
        skip: int = 0,
        limit: int = 100
) -> List[models.Blast]:
    manager = BlastManager(db)
    return manager.get_blasts(skip, limit)


def get_blast(db: Session, blast_id: int) -> Optional[models.Blast]:
    manager = BlastManager(db)
    return manager.get_blast(blast_id)


def update_blast(
        db: Session,
        blast_id: int,
        blast: schemas.BlastUpdate
) -> Optional[models.Blast]:
    manager = BlastManager(db)
    return manager.update_blast(blast_id, blast)


def delete_blast(db: Session, blast_id: int) -> Optional[models.Blast]:
    manager = BlastManager(db)
    return manager.delete_blast(blast_id)


async def send_otp(db: Session, contact_id: int, channel: str = "sms"):
    manager = BlastManager(db)
    return await manager.send_otp(contact_id, channel)


async def verify_otp(db: Session, contact_id: int, code: str):
    manager = BlastManager(db)
    return await manager.verify_otp(contact_id, code)
