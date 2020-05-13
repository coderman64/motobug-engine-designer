from shutil import copy2
import os

def copytree(src,dst):
    for root, dirs, files in os.walk(src):
        if not os.path.isdir(root):
            os.mkdirs(root)
        for each_file in files:
            rel_path = root.replace(src,"").lstrip(os.sep)
            dest_path = os.path.join(dst,rel_path, each_file)
            if not os.path.isdir(os.path.dirname(dest_path)):
                os.makedirs(os.path.dirname(dest_path))
            copy2(os.path.join(root,each_file),dest_path)