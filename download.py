from __future__ import print_function
import os.path
import io
import subprocess
import pickle
from apiclient import errors
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from termcolor import colored
from googleapiclient.http import MediaIoBaseDownload
from alive_progress import config_handler,alive_bar
from yaspin import yaspin
from yaspin.spinners import Spinners

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
    print (colored('    __                         ______    __                            ______        ', 'magenta', None, ['bold', 'blink']))
    print (colored('   / /   __  __  _____        /_  __/   / /_   ____ _   ____          / ____/  ____ _', 'red', None, ['bold', 'blink']))
    print (colored('  / /   / / / / / ___/         / /     / __ \ / __ `/  / __ \        / /      / __ `/', 'yellow', None, ['bold', 'blink']))
    print (colored(' / /___/ /_/ / / /__          / /     / / / // /_/ /  / / / /       / /___   / /_/ / ', 'cyan', None, ['bold', 'blink']))
    print (colored('/_____/\__,_/  \___/         /_/     /_/ /_/ \__,_/  /_/ /_/        \____/   \__,_/  ', 'green', None, ['bold', 'blink']))
    print (colored('===================================================================================================================', 'white'))
    print (colored('                                         Phiên bản : ', 'yellow'), (1.0))
    print (colored('                                         Tác giả   : ', 'yellow'), colored('Vadu', 'green', None, ['underline', 'bold']), ('và google docs'))
    print (colored('                                         Github    : ', 'yellow'), ('https://github.com/udav-haui/google-drive-downloader.git'))
    
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """

    config_handler.set_global(length=30, spinner='balls_scrolling', bar='bubbles')

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        try:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        except FileNotFoundError:
            print (colored('Không thể xác thực và tạo file token.json,hãy kiểm tra file credentials.json xem có tồn tại không!', 'red'))
            exit()
    service = build('drive', 'v3', credentials=creds)

    try:
        pass
        print(colored('* Đường dẫn lưu. Mặc định là đường dẫn hiện tại', 'blue'))
        location = input("   - Đường dẫn: ")
        while not location:
            location = input("   - Đường dẫn: ")
        type(location)

        print(colored('* Folder/File ID: ','blue'))
        folder_id = input("   - ID  : ")
        while not folder_id:
            folder_id = input("   - ID  : ")
        type(folder_id)
    except EOFError:
        print("EOFError: Terminated!")
        exit()
    except KeyboardInterrupt:
        print("Terminated!")
        exit()
    if location[-1] != '/':
        location += '/'

    try:
        with yaspin(Spinners.clock, text=colored('BẮT ĐẦU LẤY TOÀN BỘ CÁC FILE TRONG THƯ MỤC ĐÃ NHẬP...', 'yellow'), color="yellow") as spinner:
            reloadData = False
            with open('listfile.data', 'rb') as filehandle:
                # read the data as binary data stream
                files = pickle.load(filehandle)
            try:
                if not files or len(files) == 0:
                    reloadData = True
                    files = getAllFilesRecursive(service, folder_id, location)
            except NameError:
                reloadData = True
                files = getAllFilesRecursive(service, folder_id, location)
            if reloadData == True:
                spinner.text = colored('Không có dữ liệu có sẵn, load lại dữ liệu và ghi vào file json', 'yellow')
                files = getAllFilesRecursive(service, folder_id, location)
                with open('listfile.data', 'wb') as filehandle:
                    # store the data as binary data stream
                    pickle.dump(files, filehandle)

            spinner.text = colored('ĐÃ LẤY ĐƯỢC TỔNG CỘNG {} FILE!'.format(colored(len(files), 'green')), 'yellow')
            spinner.ok("✅")
        print (colored(" >>>>> BẮT ĐẦU TẢI CÁC TỆP", 'yellow'))

        downloadedSuccessCount = 0
        with alive_bar(len(files)) as bar:
            for item in files:
                file_id = item[u'id']
                filename = item[u'name'] #no_accent_vietnamese(item[u'name'])
                savePath = item[u'save_path']
                # bar.text(filename)
                download_file(service, file_id, savePath, filename, bar)
                downloadedSuccessCount += 1
                bar()
    except KeyboardInterrupt: 
        print (colored("Bạn đã ngắt chương trình!!!", 'red'))
    except errors.HttpError as error:
        print ('An error occurred: {}'.format(error))
        exit()
    print (colored('Đã tải xuống hoàn tất {} tệp!'.format(downloadedSuccessCount), 'green'));
    
    # Map lại dấu xược chéo
    pathh = os.path.normpath(location)
    subprocess.Popen(f'explorer "{pathh}"')
    exit()
    # Call the Drive v3 API
    #results = service.files().list(pageSize=5, fields="nextPageToken, files(id, name)").execute()
    results = service.files().list(
            q="'{}' in parents".format(folder_id),
            fields='files(id, name, mimeType, size)').execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))

def getAllFilesRecursive(service, folder_id, location, folderName = None):
    listFiles = []
    if folderName: 
            location += folderName;
    location += '/'

    result = []
    files = service.files().list(q="'{}' in parents".format(folder_id),fields='files(id, name, mimeType, size)').execute()
    result.extend(files['files'])
    result = sorted(result, key=lambda k: k[u'name'])

    if not folderName:
        currentFolder = service.files().get(fileId=folder_id).execute()
    try: 
        if currentFolder[u'id']:
            folderName = currentFolder[u'name']
    # try catch currentFolder was be defined before
    except NameError:
        pass
    total = len(result)
    if total == 0:
        return listFiles
    for item in result:
        file_id = item[u'id']
        filename = item[u'name']
        mime_type = item[u'mimeType']
        # Nếu là folder thì chạy đệ quy tiếp
        if mime_type == 'application/vnd.google-apps.folder':
            listFiles += getAllFilesRecursive(service, file_id, location, filename)
            continue
        # Nếu file chưa đượC tải xuống
        elif not os.path.isfile('{}{}'.format(location, filename)):
            item[u'save_path'] = location
        else:
            remote_size = item[u'size']
            local_size = os.path.getsize('{}{}'.format(location, filename))
            # Nếu file đã tồn tại trên hệ thống thì next còn nếu tồn tại mà lại bị corrupt thì xoá và thêm vào list
            if (str(remote_size) == str(local_size)):
                # print (colored('File đã tồn tại!', 'magenta'))
                continue
            else:
                # print (colored('File trên máy đã bị hỏng', 'red'))
                os.remove('{}{}'.format(location, filename))
                item[u'save_path'] = location
        listFiles.append(item)
    return listFiles

def download_folder(service, folder_id, location, folderName = None):
    if folderName: 
        location += folderName;
    if not os.path.exists(location):
        os.makedirs(location)
    location += '/'

    result = []
    files = service.files().list(
            q="'{}' in parents".format(folder_id),
            fields='files(id, name, mimeType, size)').execute()
    result.extend(files['files'])
    result = sorted(result, key=lambda k: k[u'name'])

    if not folderName:
        currentFolder = service.files().get(fileId=folder_id).execute()
    
    try: 
        if currentFolder[u'id']:
            folderName = currentFolder[u'name']
    # try catch currentFolder was be defined before
    except NameError:
        pass
    total = len(result)
    if total == 0:
        print (colored('Thư mục trống!', 'red'))
        exit()
    else:
        print (colored('BẮT ĐẦU TẢI XUỐNG THƯ MỤC ->', 'yellow'), colored('{}'.format(folderName), 'green'))
    with alive_bar(total) as bar:
        for item in result:
            file_id = item[u'id']
            filename = item[u'name'] #no_accent_vietnamese(item[u'name'])
            mime_type = item[u'mimeType']
            # print ('- ', colored(filename, 'cyan'), colored(mime_type, 'cyan'), '({}/{})'.format(current, total))
            if mime_type == 'application/vnd.google-apps.folder':
                bar()
                download_folder(service, file_id, location, filename)
            elif not os.path.isfile('{}{}'.format(location, filename)):
                download_file(service, file_id, location, filename)
                bar.text(filename)
            else:
                remote_size = item[u'size']
                local_size = os.path.getsize('{}{}'.format(location, filename))
                if (str(remote_size) == str(local_size)):
                    print (colored('File đã tồn tại!', 'magenta'))
                else:
                    print (colored('File trên máy đã bị hỏng', 'red'))
                    os.remove('{}{}'.format(location, filename))
                    download_file(service, file_id, location, filename)
                bar()
            # current += 1
            # percent = float((current-1))/float(total)*100
            # print (colored('Đã hoàn thành {:.2f}%'.format(percent), 'green'))
        
def download_file(service, file_id, location, filename, bar = None):
    if not os.path.exists(location):
        os.makedirs(location)
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO('{}{}'.format(location, filename), 'wb')
    # chunk size = 10MB
    downloader = MediaIoBaseDownload(fh, request,chunksize=1024*1024*10)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        if status and bar:
            bar.text(filename + ': đã tải {}%'.format(int(status.progress() * 100)))

if __name__ == '__main__':
    main()