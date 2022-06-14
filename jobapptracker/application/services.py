import requests, re, os.path, pickle

from bs4 import BeautifulSoup

from django.http import JsonResponse
from django.core.exceptions import ValidationError
from settings import credentials

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient import errors
from email.message import EmailMessage


def linkedin_job_scrape(url):
    # url = "https://www.linkedin.com/jobs/view/2882566805/?alternateChannel=search&refId=oeuThlhJUGw6MCN%2Fx3qkfw%3D%3D&trackingId=j48fIHAW5AAT6qQxLYiY8A%3D%3D&trk=d_flagship3_job_details"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    job_info = soup.title.contents[0]
    info_dic = {
        'company': re.search('.*(?= hiring)', job_info).group(0),
        'position': re.search('(?<= hiring ).*(?= in)', job_info).group(0),
        'location': re.search('(?<=in ).*(?= \|)', job_info).group(0)
    }

    return info_dic

def gmail_authenticate():
    creds = None
    SCOPES = ['https://mail.google.com/']
    # the file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # if there are no (valid) credentials availablle, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            credential_file = os.path.join(os.path.dirname(__file__), '../settings/client_secret.json')
            flow = InstalledAppFlow.from_client_secrets_file(credential_file, SCOPES)
            creds = flow.run_local_server(port=1234)
        # save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)