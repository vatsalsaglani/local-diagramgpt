import os

FALLBACK_FILE_PATH = "./resources/fallback.png"


def find_file_contains(root_dir, query):
    query = query.lower()
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if query in filename.lower():
                return os.path.join(dirpath, filename)
    return FALLBACK_FILE_PATH
