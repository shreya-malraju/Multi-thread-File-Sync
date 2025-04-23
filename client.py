import base64
import os
import argparse
import logging
from xmlrpc.client import ServerProxy
from os.path import exists


format = "CLIENT:%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

proxy = ServerProxy('http://localhost:3000', verbose=False)
dir_root = os.path.dirname(os.path.abspath(__file__))
client_dir = os.path.join(dir_root, "Client_docs")


def client_side_docs():
        client_files = []
        for root, directories, files in os.walk(client_dir, topdown=False):
            for f in files:
                file_path = os.path.join(root, f)
                base_path = file_path[file_path.rindex('Client_docs')+len("Client_docs/"):]
                client_files.append(base_path)
        return client_files
    

def meta_data(root, f , is_a_dir):
    obj_file = {
        'c_timestamp': os.path.getctime(os.path.join(root, f)),
        'timestamp': os.path.getmtime(os.path.join(root, f)),
        'is_a_dir': is_a_dir,
        'file_path': os.path.join(root, f),
        'size': os.path.getsize(os.path.join(root, f))
    }
    return obj_file


def obtain_data(path, obj_file):
    if obj_file['is_a_dir']:
        return obj_file
    else:        
        temp = open(path, "rb")
        d = temp.read()
        temp.close()
        obj_file['content'] = base64.b64encode(d)
        return obj_file


def create_new_file(content, path):
    try:
        path = os.path.join(client_dir, path)    
        if (not os.path.exists(path)):
            os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as temp:
            temp.write(base64.b64decode(content.data))    
        return True
    except Exception as ex:
        logging.info(f"Exception occured {ex}")
        return False


if __name__ == '__main__':
    p = argparse.ArgumentParser()

    p.add_argument("-l", "--list", type=str, nargs=1, metavar=('target'))
    p.add_argument("-r", "--rename", type=str, nargs=2,metavar=('old_name', 'new_name'))
    p.add_argument("-d", "--download", type=str, nargs=2,metavar=('source', 'dest'))
    p.add_argument("-del", "--delete", type=str, nargs=1,metavar=('target'))
    p.add_argument("-u", "--upload", type=str, nargs=2,metavar=('source', 'dest'))
    
    arguments = p.parse_args()

    
    if arguments.list is not None:
        tg = arguments.list[0]
        if tg == "server":
            s_file_list = proxy.dir_list()
            logging.info(s_file_list)
        elif tg == "client":
            client_files = client_side_docs()
            logging.info(client_files)
        else:
            logging.info("CHECK PATH")

    elif arguments.upload is not None:
        s, d = arguments.upload[0], arguments.upload[1]
        comp_path_source = os.path.join(client_dir, s)
        if exists(comp_path_source):
            source_obj = meta_data(dir_root, comp_path_source, False)
            file_source= obtain_data(comp_path_source,source_obj)
            isUploadSuccessful = proxy.upload(file_source, d)
            if isUploadSuccessful:
                print("FILE UPLOADED SUCCESSFULLY")
            else:
                print("ERROR: PATH")
        else:
            logging.info("GIVEN FILE UNAVAILABLE")
        
    elif arguments.download is not None:
        s, d = arguments.download[0], arguments.download[1]
        temp = proxy.download(s)
        if(temp == 'DownloadException'):
            logging.info("GIVEN FILE UNAVAILABLE")
        else:
            if(create_new_file(temp, d)):
                logging.info("FILE DOWNLOADED SUCCESSFULLY")

    elif arguments.rename is not None:
        previous_file_name, latest_file_name = arguments.rename[0], arguments.rename[1]
        if proxy.rename(previous_file_name, latest_file_name):
            logging.info("FILE RENAMED SUCCESSFULLY")
        else:
            logging.info("GIVEN FILE UNAVAILABLE")

    elif arguments.delete is not None:
        t = arguments.delete[0]
        if proxy.delete(t):        
            logging.info("FILE DELETED SUCCESSFULLY")
        else:
            logging.info("GIVEN FILE UNAVAILABLE")

    