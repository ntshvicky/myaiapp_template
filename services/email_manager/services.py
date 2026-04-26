"""
Email service — IMAP read + SMTP send, with AI helpers.
"""
import imaplib
import smtplib
import email as email_lib
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from .models import EmailAccount


def _decode_str(value, default=""):
    if value is None:
        return default
    parts = decode_header(value)
    decoded = []
    for text, enc in parts:
        if isinstance(text, bytes):
            decoded.append(text.decode(enc or "utf-8", errors="replace"))
        else:
            decoded.append(text)
    return "".join(decoded)


class IMAPClient:
    """Thin IMAP wrapper around imaplib."""

    def __init__(self, account: EmailAccount):
        self.account = account

    def _connect(self):
        if self.account.imap_use_ssl:
            conn = imaplib.IMAP4_SSL(self.account.imap_host, self.account.imap_port)
        else:
            conn = imaplib.IMAP4(self.account.imap_host, self.account.imap_port)
        conn.login(self.account.username, self.account.password)
        return conn

    def test_connection(self):
        """Return (True, "") or (False, error_message)."""
        try:
            conn = self._connect()
            conn.logout()
            return True, ""
        except Exception as exc:
            return False, str(exc)

    def list_folders(self):
        """Return list of mailbox folder names."""
        try:
            conn = self._connect()
            _, folder_list = conn.list()
            conn.logout()
            folders = []
            for item in folder_list:
                if isinstance(item, bytes):
                    parts = item.decode().split('"/"')
                    name = parts[-1].strip().strip('"')
                    folders.append(name)
            return folders
        except Exception:
            return ["INBOX", "Sent", "Drafts", "Trash"]

    def fetch_emails(self, folder="INBOX", limit=30, search_criteria="ALL"):
        """Fetch email summaries from a folder."""
        try:
            conn = self._connect()
            conn.select(f'"{folder}"' if " " in folder else folder, readonly=True)
            _, message_ids = conn.search(None, search_criteria)
            ids = message_ids[0].split()
            ids = ids[-limit:][::-1]  # newest first
            emails = []
            for uid in ids:
                _, msg_data = conn.fetch(uid, "(RFC822.HEADER FLAGS)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email_lib.message_from_bytes(response_part[1])
                        flags_raw = response_part[0].decode() if isinstance(response_part[0], bytes) else ""
                        is_read = "\\Seen" in flags_raw
                        emails.append({
                            "uid": uid.decode(),
                            "subject": _decode_str(msg.get("Subject"), "(No subject)"),
                            "from": _decode_str(msg.get("From"), ""),
                            "date": msg.get("Date", ""),
                            "read": is_read,
                        })
            conn.logout()
            return emails
        except Exception as exc:
            return []

    def fetch_email_body(self, uid, folder="INBOX"):
        """Fetch full email body by UID."""
        try:
            conn = self._connect()
            sel = f'"{folder}"' if " " in folder else folder
            conn.select(sel, readonly=False)
            conn.store(str(uid).encode(), "+FLAGS", "\\Seen")
            _, msg_data = conn.fetch(str(uid).encode(), "(RFC822)")
            conn.logout()
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email_lib.message_from_bytes(response_part[1])
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            ct = part.get_content_type()
                            disp = str(part.get("Content-Disposition", ""))
                            if ct == "text/html" and "attachment" not in disp:
                                body = part.get_payload(decode=True).decode("utf-8", errors="replace")
                                break
                            elif ct == "text/plain" and "attachment" not in disp and not body:
                                body = part.get_payload(decode=True).decode("utf-8", errors="replace")
                    else:
                        payload = msg.get_payload(decode=True)
                        body = payload.decode("utf-8", errors="replace") if payload else ""
                    return {
                        "uid": uid,
                        "subject": _decode_str(msg.get("Subject"), "(No subject)"),
                        "from": _decode_str(msg.get("From"), ""),
                        "to": _decode_str(msg.get("To"), ""),
                        "date": msg.get("Date", ""),
                        "body": body,
                    }
        except Exception as exc:
            return {"error": str(exc)}
        return {"error": "No message data"}

    def search_emails(self, query, folder="INBOX"):
        """Search emails by subject or from."""
        try:
            criteria = f'OR SUBJECT "{query}" FROM "{query}"'
            return self.fetch_emails(folder=folder, limit=50, search_criteria=criteria)
        except Exception:
            return []


class SMTPClient:
    """Thin SMTP wrapper."""

    def __init__(self, account: EmailAccount):
        self.account = account

    def send(self, to: str, subject: str, body: str, html: bool = False):
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = (
                f"{self.account.display_name} <{self.account.email}>"
                if self.account.display_name
                else self.account.email
            )
            msg["To"] = to
            mime_type = "html" if html else "plain"
            msg.attach(MIMEText(body, mime_type, "utf-8"))

            if self.account.smtp_use_tls:
                server = smtplib.SMTP(self.account.smtp_host, self.account.smtp_port)
                server.ehlo()
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.account.smtp_host, self.account.smtp_port)

            server.login(self.account.username, self.account.password)
            server.sendmail(self.account.email, [to], msg.as_string())
            server.quit()
            return True, ""
        except Exception as exc:
            return False, str(exc)
