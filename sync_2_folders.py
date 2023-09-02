import argparse
import os
import hashlib
import shutil
import time


def get_file_hash(file_path): # function to get the hash value of a file
    buf_size = 32768
    sha_hash = hashlib.sha1()
    with open(file_path, "rb") as f:
        while True:
            data = f.read(buf_size)
            if not data:
                break
            sha_hash.update(data)

    return sha_hash.hexdigest()


def sync_folders(source_folder, replica_folder, log_file): #function to synchronise folder
    for root, dirs, files in os.walk(source_folder): # copy/modify files/directory from source to replica
        for file_name in files: # check for all files in the source folder
            if not file_name.startswith('.'):

                source_file_path = os.path.join(root, file_name)
                relative_path = os.path.relpath(source_file_path, source_folder)
                replica_file_path = os.path.join(replica_folder, relative_path)

                if not os.path.exists(replica_file_path): # check if source file exists in replica folder
                    os.makedirs(os.path.dirname(replica_file_path), exist_ok=True)
                    shutil.copy2(source_file_path, replica_file_path)
                    log_entry = f"COPIED NEW FILE: {relative_path}"
                    print(log_entry)
                    log_to_file(log_file, log_entry)

                if get_file_hash(source_file_path) != get_file_hash(replica_file_path): # check if source or replica file is modified
                    os.makedirs(os.path.dirname(replica_file_path), exist_ok=True)
                    shutil.copy2(source_file_path, replica_file_path)
                    log_entry = f"COPIED MODIFIED FILE: {relative_path}"
                    print(log_entry)
                    log_to_file(log_file, log_entry)

        for dir_name in dirs: #check for all directories in the source folder
            source_dir_path = os.path.join(root, dir_name)
            relative_path = os.path.relpath(source_dir_path, source_folder)
            replica_dir_path = os.path.join(replica_folder, relative_path)

            if not os.path.exists(replica_dir_path): # check if the source directoy exists in replica folder
                os.makedirs(replica_dir_path, exist_ok=True)
                log_entry = f"COPIED NEW DIRECTORY: {relative_path}"
                print(log_entry)
                log_to_file(log_file, log_entry)

    for root, dirs, files in os.walk(replica_folder): #to delete files/directory in replica folder

        for file_name in files: # check all files in replica folder
            if not file_name.startswith('.'): #to ignore system related files

                replica_file_path = os.path.join(root, file_name)
                relative_path = os.path.relpath(replica_file_path, replica_folder)
                source_file_path = os.path.join(source_folder, relative_path)

                if not os.path.exists(source_file_path): # check if source file deleted 
                    os.remove(replica_file_path)
                    log_entry = f"REMOVED FILE: {relative_path}"
                    print(log_entry)
                    log_to_file(log_file, log_entry)

        for dir_name in dirs:
            replica_dir_path = os.path.join(root, dir_name)
            relative_path = os.path.relpath(replica_dir_path, replica_folder)
            source_dir_path = os.path.join(source_folder, relative_path)

            if not os.path.exists(source_dir_path): # check if source directory is deleted 
                shutil.rmtree(replica_dir_path)
                log_entry = f"REMOVED DIRECTORY: {relative_path}"
                print(log_entry)
                log_to_file(log_file, log_entry)


def log_to_file(log_file, log_entry): # function to log entries
    with open(log_file, "a") as f:
        f.write(f"{time.ctime()}: {log_entry}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source_folder", help="Path to the source folder")
    parser.add_argument("replica_folder", help="Path to the replica folder")
    parser.add_argument("sync_interval", type=int, help="Sync interval in seconds")
    parser.add_argument("log_file", help="Path to the log file")
    args = parser.parse_args()

    while True: # execute sync_folder with time interval
        sync_folders(args.source_folder, args.replica_folder, args.log_file)
        time.sleep(args.sync_interval)
