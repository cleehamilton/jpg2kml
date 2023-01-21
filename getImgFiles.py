'''
Get Image files in dir
'''
import glob

def get_img_paths(search_path,ext,recursive):
    # search all files inside a specific folder
    if recursive == 0:
        target = search_path + '*' + ext
        res = glob.glob(target)
        for r in res:
            print(r)
    # Search all files/folders inside a specific folder
    if recursive == 1:
        target = search_path + '**\\*' + ext
        for file in glob.glob(target, recursive=True):
            print(file)
ext = ".jpg"



get_img_paths(r'C:\Users\kaff1n8t3d\Pictures\\', ext, 1)