'''
https://medium.com/spatial-data-science/how-to-extract-gps-coordinates-from-images-in-python-e66e542af354
'''
import exif
from exif import Image
img_path = 'test.jpg'

def decimal_coords(coords, ref):
    decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
    if ref == "S" or ref == "W":
        decimal_degrees = -decimal_degrees
    return decimal_degrees

def image_coordinates(img_path):
    errMsg = ""
    with open(img_path, 'rb') as src:
        img = Image(src)
        if img.has_exif:
            try:
                img.gps_longitude
                coords = (decimal_coords(img.gps_latitude,img.gps_latitude_ref),decimal_coords(img.gps_longitude,img.gps_longitude_ref))
            except AttributeError:
                print('No Coordinates')
        else:
            errMsg += 'The Image has no EXIF information'
        imgData = list()
        imgData = [src.name,img.datetime_original,coords]
    return errMsg,imgData


print(image_coordinates(img_path))