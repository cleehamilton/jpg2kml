'''
.jpg to KML
'''
# intro opening
#Menu list
'''input('How would you like to convert image locations to KML?')
1.) A single image? 
    -->input('What is the file path of the image?')
2.) All images inside a folder?
    -->input('What is the folder path to begin search?'')
3.) Recursively through files?
    -->input('What is the top level folder path to begin search?')

return -->menuRes = list({menuChoice},{second answer})
'''
SearchPath = input('Where are the pictures? (needs trailing "\")\n')
jobName = input('What should we call this session?\n')
''' Get Image files in dir  '''
import glob
def get_img_paths(search_path,ext,recursive):
    # search all files inside a specific folder
    JPGfiles = [] #output var
    if recursive == 0:
        target = search_path + '*' + ext
        res = glob.glob(target)
        for r in res:
            #print(r) #update this for next step.
            JPGfiles.append((r))
    # Search all files/folders inside a specific folder
    if recursive == 1:
        target = search_path + '**\\*' + ext
        for r in glob.glob(target, recursive=True):
            #print(r)#update this for next step.
            JPGfiles.append((r))
    return JPGfiles

''' get Coords from Files '''
import exif
from exif import Image
#img_path = 'test.jpg'

def decimal_coords(coords, ref):
    decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
    if ref == "S" or ref == "W":
        decimal_degrees = -decimal_degrees
    return decimal_degrees

def image_coordinates(img_paths):
    errMsg = ""
    index = 0
    data = []
    while index < len(img_paths):
        img_path = img_paths[index]
        with open(img_path, 'rb') as src:
            img = Image(src)
            fullPath = src.name
            splChr = "\\"
            match = fullPath.rsplit(splChr,1)
            fileName = match[1]
            coords = ()
            msg=""
            #print(fileName)
            if img.has_exif:
                try:
                    img.gps_longitude
                    coords = (decimal_coords(img.gps_longitude,img.gps_longitude_ref),decimal_coords(img.gps_latitude,img.gps_latitude_ref))
                except AttributeError:
                    msg = f"The image {fileName} does not have coordinate data"
            else:
                errMsg = f"The image {fileName} does not have EXIF data."
                msg = f"The image {fileName} does not have EXIF data."
            imgData = list()
            imgData = (fileName,fullPath,img.datetime_original,coords,msg)
            data.append(imgData)
            index += 1
            
    return errMsg,data


#Seach files
ext = ".jpg" #EXIF data only exisit in jpegs
print('------------------------Output-------------------------')
img_paths = get_img_paths(SearchPath, ext, 0)
#print(img_paths)
#get Coords

img_data = image_coordinates(img_paths)
#print(img_data)

#write KML
''' Write KML prebody section '''

kmlHeader = f'<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2"><Document><name>{jobName}.kml</name><open>1</open>'
#print(kmlHeader)

''' Get Average Coord data for images without data '''
cnt = 0
lat = 0
long = 0
for i in img_data[1]:
    if not i[3] :
        j=""
    else:
        lat += i[3][1]
        long += i[3][0]
        cnt += 1
if cnt != 0:
    avglat = lat/cnt
    avglong = long/cnt
    unrefdcoords = (avglong,avglat)
#print(f"avg is {unrefdcoords}")


''' Write KML PlaceMark Tags'''
placemark = []
count = 1
for each in img_data[1]:
    if not each[3]:
        plmrkCoord = unrefdcoords
    else:
        plmrkCoord = each[3]
    if not each[4]:
        plmrkMsg = ""
    else:#<TimeStamp><when>{each[2]}</when></TimeStamp>image of {each[0]}. {plmrkMsg}
        plmrkMsg = f'{each[4]}, an average position was applied to this image.'
    plmrk = f'<Placemark><name>{each[0]}</name>\
<LookAt><latitude>{plmrkCoord[1]}</latitude><longitude>{plmrkCoord[0]}</longitude><range>1000</range><tilt>8.3</tilt><heading>0</heading></LookAt>\
<description><![CDATA[<img style="max-width:500px;" src="file:///{each[1]}" />]]></description>\
<Point id="{count}"><extrude>0</extrude><altitudeMode>clampToGround</altitudeMode><coordinates>{plmrkCoord[0]},{plmrkCoord[1]}</coordinates><!-- lon,lat[,alt] --></Point></Placemark>'
    placemark.append(plmrk)
    count += 1
    del plmrkCoord
#print(placemark)

''' Write KML postbody section '''
kmlFooter = "</Document></kml>"
#print(kmlFooter)
print(kmlHeader)
for n in placemark:
    print(n)
print(kmlFooter)
kmlCode = f"{kmlHeader}{placemark}{kmlFooter}"
#Write File
file2write = f"{jobName}.kml"
f = open(file2write,"w")
f.write(kmlCode)
f.close()
