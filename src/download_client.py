import http.client


def download_file(
        remote_host: str,
        remote_path: str,
        local_path: str,
        remote_port: int = http.client.HTTPS_PORT):
    '''
    Download the file at https://<remote_host>/<remote_path>, and save it
    to <local_path>
    '''

    # Note the remote_port arg can technically be left out if it is the
    # standard https port (443), as HTTPSConnection uses that port by default
    conn = http.client.HTTPSConnection(remote_host, remote_port)
    conn.request('GET', remote_path)
    resp = conn.getresponse()
    data = resp.read()
    with open(local_path, 'wb') as fw:
        fw.write(data)


def download_file_example():
    '''
    Example: The following call downloads a jpeg file and saves it on this computer. 

    get jpeg from : https://img-prod-cms-rt-microsoft-com.akamaized.net/cms/api/am/imageFileData/RE4wwu9?ver=69d6
    save jpeg to  :  'C:\\Users\\some_user\\Downloads\\downloaded_image.jpeg'

    * DON'T include the leading 'https://' in the `remote_host` (the
      HTTPSConnection class used by the download_file method automatically
      prepends it)

    * DON'T include the trailing '/' in the `remote_host`

    * DO include the leading '/' in the `remote_path`
    '''

    download_file(
        'img-prod-cms-rt-microsoft-com.akamaized.net',
        '/cms/api/am/imageFileData/RE4wwu9?ver=69d6',
        'C:\\Users\\some_user\\Downloads\\downloaded_image.jpeg')
