from decouple import config

from .services import gmail_authenticate

API_KEY = config('GOOGLE_API_KEY')

def get_new_mails(q):
    service = gmail_authenticate()
    results = service.users().messages().list(userId='me', q=q).execute()
    return results

def new_mail_detail(message_id):
    service = gmail_authenticate()
    results = service.users().messages().get(userId='me', id=message_id, format='metadata', metadataHeaders='from').execute()
    return results