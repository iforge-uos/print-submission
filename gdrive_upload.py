import mimetypes
from progress_bar import The_Bar
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build, MediaFileUpload
import os
from tqdm import tqdm


def run(fileName,short, window, Config):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    DIRNAME = os.path.dirname(__file__) #Don't ask, it works
    creds = ServiceAccountCredentials._from_parsed_json_keyfile(Config["jason"], scope)
    DRIVE = build('drive','v3',credentials=creds)
    mimetypes.add_type("text/plain", ".gcode") #gets rid of mime error withot regedit
    filename = fileName #'code.gcode' #Just seen this and i cant for love nor money figure out what i was thinking
    # mimeType = 'text/plain' #Fairly sure this is no longer needed
    if ".gcode" in fileName:
        mime = 'text/plain'
    else:
        # mime = 'application/sla'
        mime = 'application/vnd.ms-pki.stl'


    media_body = MediaFileUpload(filename, mimetype=mime, chunksize=1024*256, resumable=True)
    body = {
        'name': short,
        # 'mimeType': 'text/plain', #Fairly sure this isnt needed
        "parents": [Config["FolderID"]]
            }
    pbar = tqdm(total=100)
    window.ProgressBar = The_Bar()
    window.ProgressBar.setConfig(Config)
    window.ProgressBar.initUi()
    window.ProgressBar.show()
    request = DRIVE.files().create(supportsTeamDrives=True,body=body, media_body=media_body)
    response = None
    lastvalue = 0
    while response is None:
        Config["app"].processEvents()
        status, response = request.next_chunk()
        if status:
            percent=status.progress() * 100
            pbar.n = percent
            pbar.refresh()

            # delta = percent - lastvalue
            # pbar.update(delta)
            # lastvalue = percent
            # print ("Uploaded %.2f%%" % (percent))
            window.ProgressBar.update(percent)
            Config["app"].processEvents()
    pbar.n = 100
    pbar.refresh()
    print("file uploaded")
    window.ProgressBar.update(100)

    global id
    id = str(response['id'])
    print("ID is "+ id)
    window.ProgressBar.hide()
    return(1,id)
