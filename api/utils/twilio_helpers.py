from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from sqlalchemy.orm import Session
import api.models as models
from datetime import datetime
import os
from pytz import timezone
from typing import List, Optional, Dict


class TwilioClient:
    def __init__(
            self,
            account_sid: Optional[str] = None,
            auth_token: Optional[str] = None
    ):
        self.account_sid = account_sid or os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = auth_token or os.getenv("TWILIO_AUTH_TOKEN")
        self.client = Client(self.account_sid, self.auth_token)


class TwilioSMS(TwilioClient):
    def __init__(
            self,
            account_sid: Optional[str] = None,
            auth_token: Optional[str] = None
    ):
        super().__init__(account_sid, auth_token)
        self.phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        self.message_params = {}

    def set_recipient(self, to_number: str):
        self.message_params['to'] = to_number

    def set_message(self, message: str):
        self.message_params['body'] = message

    def set_media_urls(self, media_urls: List[str]):
        self.message_params['media_url'] = media_urls

    def set_scheduled_time(self, scheduled_time: datetime):
        if scheduled_time.tzinfo != timezone.utc:
            scheduled_time = scheduled_time.astimezone(timezone.utc)
        self.message_params['schedule_type'] = 'fixed'
        self.message_params['send_at'] = scheduled_time.isoformat()

    def send(self) -> str:
        self.message_params['from_'] = self.phone_number
        message = self.client.messages.create(**self.message_params)
        return message.sid


class TwilioVerify(TwilioClient):
    def __init__(
            self,
            account_sid: Optional[str] = None,
            auth_token: Optional[str] = None
    ):
        super().__init__(account_sid, auth_token)
        self.verify_service_sid = os.getenv("TWILIO_VERIFY_SERVICE_SID")

    def send_verification(self, to: str, channel: str) -> Dict:
        verification = self.client.verify.v2.services(
            self.verify_service_sid
        ).verifications.create(
            to=to,
            channel=channel
        )
        return {
            'sid': verification.sid,
            'status': verification.status
        }

    def check_verification(self, to: str, code: str) -> Dict:
        verification_check = self.client.verify.v2.services(
            self.verify_service_sid
        ).verification_checks \
            .create(
                to=to,
                code=code
            )
        return {
            'sid': verification_check.sid,
            'status': verification_check.status
        }


class SMSInteractionManager:
    def __init__(self, db: Session):
        self.db = db
        self.sms = TwilioSMS()

    async def send_and_update_interaction(
            self,
            phone_number: str,
            message: str,
            interaction_id: int
    ):
        try:
            self.sms.set_recipient(phone_number)
            self.sms.set_message(message)
            self.sms.send()

            self._update_interaction_status(interaction_id, 'sent')

        except TwilioRestException as e:
            self._update_interaction_status(
                interaction_id,
                'failed',
                str(e)
            )

        except Exception as e:
            self._update_interaction_status(
                interaction_id,
                'failed',
                f"An unexpected error occurred: {e}"
            )

    def _update_interaction_status(
            self,
            interaction_id: int,
            status: str,
            error_message: Optional[str] = None
    ):
        db_interaction = self.db.query(
            models.Interaction
        ).filter(
            models.Interaction.id == interaction_id
        ).first()
        if db_interaction:
            db_interaction.status = status
            if error_message:
                db_interaction.error_message = error_message
            self.db.commit()


# For backwards compatibility
def send_sms(
    to_number: str,
    message: str,
    from_number: str = os.getenv("TWILIO_PHONE_NUMBER"),
    media_urls: Optional[List[str]] = None,
    scheduled_time: Optional[datetime] = None
) -> str:
    sms = TwilioSMS()
    sms.set_recipient(to_number)
    sms.set_message(message)
    if media_urls:
        sms.set_media_urls(media_urls)
    if scheduled_time:
        sms.set_scheduled_time(scheduled_time)
    return sms.send()


# For backwards compatibility
async def send_sms_and_update_interaction(
    phone_number: str, message: str, interaction_id: int, db: Session
):
    manager = SMSInteractionManager(db)
    await manager.send_and_update_interaction(
        phone_number,
        message,
        interaction_id
    )


# New functions for verification
def send_verification(to: str, channel: str) -> Dict:
    verify = TwilioVerify()
    return verify.send_verification(to, channel)


def check_verification(to: str, code: str) -> Dict:
    verify = TwilioVerify()
    return verify.check_verification(to, code)
