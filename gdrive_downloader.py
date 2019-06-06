import io

from googleapiclient import discovery
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from httplib2 import Http
from oauth2client import file, client, tools


# code from google-api tutorial
def authorise():
    obj = lambda: None
    lmao = {"auth_host_name": 'localhost', 'noauth_local_webserver': 'store_true', 'auth_host_port': [8080, 8090],
            'logging_level': 'ERROR'}
    for k, v in lmao.items():
        setattr(obj, k, v)

    # authorization boilerplate code
    SCOPES = 'https://www.googleapis.com/auth/drive.readonly'
    store = file.Storage('my_personal_authorisation_token.json')
    creds = store.get()
    # The following will give you a link if token.json does not exist, the link allows the user to give this app permission
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('wa_worker_google_credentials.json', SCOPES)
        creds = tools.run_flow(flow, store, obj)
    return creds


def try_other_format(func):
    def decorated(*args, **kwargs):
        credentials = authorise()
        kwargs.update({'credentials': credentials})
        try:
            func(*args, **kwargs)
        except HttpError as e:
            print(e)
            mimeType = input('Please enter mime type of document you want to download.\n '
                             'Default is application/zip\n'
                             'Choose from here:\n '
                             'https://developers.google.com/drive/api/v3/manage-downloads\n')
            kwargs.update({
                'mimeType': mimeType,
                'is_document': True
            })
            decorated(*args, **kwargs)

    return decorated


@try_other_format
def download(credentials, file_id, filename='file_I_just_downloaded', is_document=False, mimeType='application/zip'):
    DRIVE = discovery.build('drive', 'v3', http=credentials.authorize(Http()))
    # if you get the shareable link, the link contains this id, replace the file_id below

    if is_document:
        request = DRIVE.files().export_media(fileId=file_id,
                                             mimeType=mimeType)
    else:
        request = DRIVE.files().get_media(fileId=file_id)

    # replace the filename and extension in the first field below
    fh = io.FileIO(f'{filename}.zip', mode='w')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    print("Download finished")


if __name__ == '__main__':
    file_id = input('Input link to file you want to download(GDrive): ')
    assert file_id.startswith('https://drive.google.com/open?id=')
    file_id = file_id.replace('https://drive.google.com/open?id=', '').replace(' ', '')
    assert file_id, 'Please enter file_id in the script'

    download(file_id=file_id)
