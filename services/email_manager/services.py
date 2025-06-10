# stub: real logic would IMAP/SMTP + embeddings
class EmailService:
    def search(self, account_id:int, query:str):
        return [{"subject":"Stub mail","snippet":"This is a stub."}]

    def send(self, account_id:int, to:str, subject:str, body:str):
        return True
