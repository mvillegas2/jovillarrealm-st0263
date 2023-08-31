import os
import glob


def find_files(root, query):
    return [
        file.replace(root, "", 1)
        for file in glob.glob(os.path.join(root, query), recursive=True)
        if os.path.isfile(file)
    ]
def list_files(conf):
    return find_files(conf, "**")