from .models import EmailAccount, StoredEmail


class EmailService:
    def search(self, account_id:int, query:str):
        if not account_id:
            return []
        emails = StoredEmail.objects.filter(account_id=account_id)
        if query:
            emails = emails.filter(subject__icontains=query) | emails.filter(body__icontains=query)
        return [
            {"subject": email.subject, "snippet": email.body[:220], "received_at": email.received_at.isoformat()}
            for email in emails.order_by("-received_at")[:20]
        ]

    def send(self, account_id:int, to:str, subject:str, body:str):
        return False
