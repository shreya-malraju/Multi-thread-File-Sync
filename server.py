
from xmlrpc.server import SimpleXMLRPCServer
import logging
from socketserver import ThreadingMixIn
import base64
import shutil
import logging
import os

root = os.path.dirname(os.path.abspath(__file__))
path_server = os.path.join(root, "Server_docs")
path_client = os.path.join(root, "Client_docs")

format = "SERVER:%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")


class File_Server_Class:

    def dir_list(self):
        list_of_files = []
        for root, directories, files in os.walk(path_server, topdown=False):
            for f in files:
                location_of_file = os.path.join(root, f)
                logging.info("location_of_file="+location_of_file)
                base = location_of_file[location_of_file.rindex('Server_docs')+len("Server_docs/"):]
                list_of_files.append(base)
        return list_of_files


    def download(self, path):
        try:
            s = os.path.join(path_server, path)
            c = self.obtain_data(s)
            return c
        except Exception as e:
            return "EXCEPTION CAUGHT WHILE DOWNLOADING FILE"
    
    def rename(self, previous_file_name, latest_file_name):
        try:
            server_previous_rename = os.path.join(path_server, previous_file_name)
            server_latest_rename = os.path.join(path_server, latest_file_name)
            client_previous_rename = os.path.join(path_client, previous_file_name)
            client_latest_rename = os.path.join(path_client, latest_file_name)
            logging.info(f"RENAME REQUEST FROM {client_previous_rename} to {client_latest_rename}")
            os.rename(server_previous_rename,server_latest_rename)
            os.rename(client_previous_rename,client_latest_rename)
            logging.info("FILE RENAMED SUCCESSFULLY")
            return True
        except OSError as e:
            logging.info(e)
            return False

    def upload(self, obj_file, path):
        try:
            tg="Client_docs"
            if tg in path:                
                path_to_be_uploaded = path.split("Client_docs/", 1)[1]
                upload_fullpath = os.path.join(path_server, path_to_be_uploaded)                
            else:
                upload_fullpath = os.path.join(path_server, path)
            if (obj_file['is_a_dir']) and (not os.path.exists(upload_fullpath)):
                os.makedirs(upload_fullpath)
                return False
            elif obj_file['is_a_dir']:
                return False
            self.create_new_file(obj_file, upload_fullpath)
            return True
        except Exception as e:
            logging.info("FILE UPLOAD ERROR")
            return False

    def cleanup(self):        
        for f in os.listdir(path_server):
            location_of_file = os.path.join(path_server, f)
            try:
                if os.path.isfile(location_of_file) or os.path.islink(location_of_file):
                    os.unlink(location_of_file)
                elif os.path.isdir(location_of_file):
                    shutil.rmtree(location_of_file)
            except Exception as e:
                logging.info("ERROR: UNABLE TO DELETE FILE")
                return False
        return True                

    def delete(self, path):
        try:
            s="Client_docs"
            if(s in path):
                del_path = path.split("Client_docs/", 1)[1]
            else:
                del_path = path
            full_del_path = os.path.join(path_server, del_path)   
            if os.path.isfile(full_del_path):
                os.remove(full_del_path)
            else:           
                shutil.rmtree(full_del_path)
            return True
        except OSError as e:
            logging.info("Error: UNABLE TO DELETE FILE")
            return False

    def create_new_file(self, obj_file, upload_fullpath):
        b = upload_fullpath[:upload_fullpath.rindex('/')]
        content = obj_file['content']
        if (not os.path.exists(b)):
            os.makedirs(os.path.dirname(upload_fullpath), exist_ok=True)

        with open(upload_fullpath, 'wb') as t:
            t.write(base64.b64decode(content.data))
        return True

    def obtain_data(self, path):
        t = open(path, "rb")
        d = t.read()
        t.close()
        return base64.b64encode(d)
    
class SimpleThreadedXMLRPCServer(ThreadingMixIn,SimpleXMLRPCServer):
    pass

s = SimpleThreadedXMLRPCServer(('localhost', 3000), logRequests=True, allow_none=True)

s.register_instance(File_Server_Class())

if __name__ == '__main__':

    try:
        logging.info('SERVER STARTED WORKING')
        s.serve_forever()
    except KeyboardInterrupt:
        logging.info('SERVER EXITTED DUE TO KEYBOARD INTERRUPT')
