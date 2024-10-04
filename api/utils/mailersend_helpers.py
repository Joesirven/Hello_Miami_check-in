from mailersend import emails
from typing import List, Dict, Optional
import os
import base64
from datetime import datetime, timedelta


def _datetime_to_unix_timestamp(dt: datetime) -> int:
    return int(dt.timestamp())


class BaseEmail:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("MAILERSEND_API_KEY")
        self.mailer = emails.NewEmail(self.api_key)
        self.mail_body = {}

    def set_sender(self, name: str, email: str):
        mail_from = {"name": name, "email": email}
        self.mailer.set_mail_from(mail_from, self.mail_body)

    def set_recipients(self, recipients: List[Dict[str, str]]):
        self.mailer.set_mail_to(recipients, self.mail_body)

    def set_subject(self, subject: str):
        self.mailer.set_subject(subject, self.mail_body)

    def send(self) -> Dict:
        response = self.mailer.send(self.mail_body)
        return response

    def set_send_at(self, send_time: datetime):
        current_time = datetime.now()
        max_delay = current_time + timedelta(hours=72)

        if send_time < current_time or send_time > max_delay:
            raise ValueError("Send time is out of allowed range")

        send_at = _datetime_to_unix_timestamp(send_time)

        self.mailer.set_send_at(
            send_at, self.mail_body)


class SimpleEmail(BaseEmail):
    def set_content(self, content: str):
        self.mailer.set_plaintext_content(content, self.mail_body)


class HTMLEmail(BaseEmail):
    def set_content(self, html_content: str, text_content: str):
        self.mailer.set_html_content(html_content, self.mail_body)
        self.mailer.set_plaintext_content(text_content, self.mail_body)


class EmailWithAttachment(BaseEmail):
    def add_attachment(self, file_path: str):
        with open(file_path, "rb") as file:
            filename = os.path.basename(file_path)
            content = base64.b64encode(file.read()).decode("utf-8")
            self.mailer.add_attachment(content, filename, self.mail_body)


class HTMLEmailWithAttachment(HTMLEmail, EmailWithAttachment):
    pass


class SimpleEmailWithAttachment(SimpleEmail, EmailWithAttachment):
    pass


class TemplateEmail(BaseEmail):
    def set_template(self, template_id: str, variables: List[Dict]):
        self.mailer.set_template_id(template_id, self.mail_body)
        self.mailer.set_variables(variables, self.mail_body)


class EmailReader:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("MAILERSEND_API_KEY")
        # Initialize email reading functionality here

    def get_messages(self, page: int = 1, limit: int = 25) -> Dict:
        # Implement message retrieval logic here
        pass

    def get_message_by_id(self, message_id: str) -> Dict:
        # Implement single message retrieval logic here
        pass
