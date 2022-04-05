from header import *
import glob
import os

def main():
    def delete_files(dir):
        for root, dir_list, file_list in os.walk(dir):
            for file_name in file_list:
                if file_name.split('.')[-1] not in media_ext:
                    os.remove(os.path.join(root, file_name))

    def delete_empty_dirs(dir):
        for file in os.listdir(dir):
            file_path = os.path.join(dir, file)
            if os.path.isdir(file_path) and len(os.listdir(file_path)) == 0:
                os.rmdir(file_path)

    with open("filenames", "r") as f:
        for filename in f:
            possible_work_dir = os.path.join(settings['download_dir'], filename.strip())
            work_dir_list = glob.glob(possible_work_dir+"*")
            for work_dir in work_dir_list:
                if work_dir.endswith(".aria2"): continue
                delete_files(work_dir)
                delete_empty_dirs(work_dir)

if __name__ == "__main__":
    main()