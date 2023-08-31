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

if __name__ == "__main__":
    from conf import configure
    conf = configure()
    print(find_files(conf["SUBDIR"], "**"))
    print(list_files(conf["SUBDIR"]))