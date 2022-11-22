import os
import shutil

if __name__ == '__main__':

    path = os.path.abspath("example/audios/16k")
    for file_name in os.listdir(path):
        # construct full file path
        file = path + "/" + file_name
        if os.path.isdir(file):
            print('Deleting file:', file)
            shutil.rmtree(file, ignore_errors=True)

            path2 = os.path.abspath(f"example/vad/{file_name}.lab")
            if os.path.exists(path2):
                os.remove(path2)

    path = os.path.abspath("example/fixed_vad")
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)

    path = os.path.abspath("exp")
    for file_name in os.listdir(path):
        # construct full file path
        file = path + "/" + file_name
        if os.path.isdir(file):
            print('Deleting file:', file)
            shutil.rmtree(file, ignore_errors=True)
        else:
            os.remove(file)
