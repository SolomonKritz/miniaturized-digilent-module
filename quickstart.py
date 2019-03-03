from __future__ import print_function
import pickle
import time
import os.path
from apiclient.http import MediaFileUpload
from apiclient.errors import HttpError
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Absolute path name where data is collected beginning with a forward slash
# FILENAME = '/Desktop/digilentFiles/waveforms/samples/py/Data.csv'
FILENAME = '/Users/Evan/Documents/umd/Spring2019/google_shared_drive_api/test.csv'
FILE_ID = '1-BRQv2TDzlL0xEs_RV7mLP1gDlOt713fOD586uinUCM'

def authorize():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def create_google_datasheet(service):
    metadata={'name': 'Data.csv',
              'mimeType': 'application/vnd.google-apps.spreadsheet'
    }
    media = MediaFileUpload(FILENAME,
                        mimetype='text/csv',
                        resumable=True)

    try:
        results = service.files().create(fields='id', body=metadata,
        media_body=media).execute()
    except HttpError, error:
        return create_google_datasheet(service)

    if results:
        print('Uploaded %s' % 'Data.csv')

    return results['id']

def update_data(service, file_id):
    metadata={'name': 'Data.csv',
              'mimeType': 'application/vnd.google-apps.spreadsheet'
    }
    media = MediaFileUpload(FILENAME,
                        mimetype='text/csv',
                        resumable=True)
    try:
        res = service.files().update(fileId=file_id, body=metadata,
        media_body=media).execute()
    except HttpError, error:
        update_data(service, file_id)

    if res:
        print('Updated %s' % 'Data.csv')

def get_data(service, file_id):
    try:
        res = service.files().export(fileId=file_id, mimeType='text/csv').execute()
    except HttpError, error:
        get_data(service, file_id)

    if res:
        print('Retrieved %s' % 'Data.csv')
        print(res)

def main():
    """ Authorize the drive to be accessed and run the Google Drive api service. """
    creds = authorize();
    service = build('drive', 'v3', credentials=creds)

    """ Create the initial datasheet to store data on. """
    # file_id = create_google_datasheet(service)

    """ Write to said datasheet continuously every 5 seconds. """
    while(True):
        update_data(service, FILE_ID)
        time.sleep(5)

    """ Retrieve content from written datasheet """
    # get_data(service, FILE_ID)

if __name__ == '__main__':
    main()
