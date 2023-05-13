'''
.jpg to KML
'''
import os
# intro opening

''' Menu system '''
def chkSlash(file_path):
    if file_path[-1] != "\\":
        path = f"{file_path}\\"
    else:
        path = file_path
    return path

def menu():
    return int(input(" How would you like to convert image locations to KML?\n\
 1.) A single image?\n\
 2.) All images inside a folder?\n\
 3.) All Images inside all folders? (recursively)\n\
                     \n\
 9.) Exit Application\n"))

def submenu(menuChoice):
    submenuchoice =[menuChoice]
    
    if submenuchoice[0] == 1:
        print('\n With this option you can choose a specific JPEG image to convert the GNSS data into a KML data point.')
        filePath = input(' 1.) a.) What is the file path of the image?\n or C to Cancel and start over...\n ')
    elif submenuchoice[0] == 2:
        print('\n With this option you can choose a folder of JPEG images to convert the GNSS data into a KML data map.')
        filePath = input(' 2.) a.) What is the folder path to begin search?\n or C to Cancel and start over...\n  ')
        filePath = chkSlash(filePath)
    elif submenuchoice[0] == 3:
        print('\n With this option you can choose a top level folder and seach that folder along with all the folders inside of it and convert the GNSS data into a KML data map.')
        filePath = input(' 3.) a.) What is the top level folder path to begin search?\n or C to Cancel and start over...\n  ')
        filePath = chkSlash(filePath)
    else:
        filePath = "Error"
    submenuchoice.append(filePath)
    return submenuchoice

def menuExe():
    loop = 1
    while loop == 1:
        choiceList = submenu(menu())
        if choiceList[1] == "C" or choiceList[1] == "c":
            print('------- Canceled-------\n')
            loop == 1
        elif choiceList[0] == 9 or choiceList[0] == 1 or choiceList[0] == 2 or choiceList[0] == 3:
            loop = 0
        else:
            loop = 1
    return choiceList

def checkChoice(list):
    #print(list)
    chkPath = list[1].rstrip("\\")
    #print(chkPath)
    chkPath = chkPath.rstrip(".jpg")
    #print(chkPath)
    Path = chkPath.partition("\\")[0]
    #PathName = chkPath.partition("\\")[1]
    PathName = chkPath[chkPath.rfind("\\")+1:]
    #print(f"{Path}, {PathName}")
    chkPath = chkPath.rstrip(PathName)
    return Path, PathName,chkPath ##Menu 1 gets stuck on double ".jpg"

''' Get Image files in dir  '''
def get_img_paths(menuChoice,search_path,ext):
    #print(f"get_img_paths() {menuChoice}")
    import glob
    # search all files inside a specific folder
    JPGfiles = [] #output var
    if menuChoice == 1:#One Image
        target = search_path
        JPGfiles.append(target)
    elif menuChoice == 2:#Search one Folder
        target = search_path + '*' + ext
        res = glob.glob(target)
        for r in res:
            #print(r) #update this for next step.
            JPGfiles.append((r))
    elif menuChoice == 3:# Search all files/folders inside a specific folder
        target = search_path + '**\\*' + ext
        for r in glob.glob(target, recursive=True):
            #print(r)#update this for next step.
            JPGfiles.append((r))
    #print(JPGfiles)
    return JPGfiles

''' get Coords from Files '''
def decimal_coords(coords, ref):
    
    decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
    if ref == "S" or ref == "W":
        decimal_degrees = -decimal_degrees
    return decimal_degrees

def image_coordinates(img_paths):
    import exif
    from exif import Image
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

'''write KML code'''
def writeKMLcode(img_data,FilePath):
    ''' Create the File name and path vars '''
    ''' Write KML prebody section '''
    jobName = f"{FilePath[1]}-Picture placement" #From Folder Name UPDATE THIS
    kmlHeader = f'<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2"><Document><name>{jobName}.kml</name><open>1</open>'


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
    <description><![CDATA[<img style="max-width:400px;" src="file:///{each[1]}" />]]></description>\
    <Point id="{count}"><extrude>0</extrude><altitudeMode>clampToGround</altitudeMode><coordinates>{plmrkCoord[0]},{plmrkCoord[1]}</coordinates><!-- lon,lat[,alt] --></Point></Placemark>'
        placemark.append(plmrk)
        count += 1
        del plmrkCoord
    kB = ""
    kmlBody = kB.join(placemark)
    ''' Write KML postbody section '''
    kmlFooter = "</Document></kml>"
    
    kmlCode = f'{kmlHeader}{kmlBody}{kmlFooter}'
    return kmlCode,FilePath

''' write kml file '''
def writeKMLfile(choice,kmlCode,PATH):
    if choice[0] == 1:
        file_path = PATH[2]
    else:
        file_path = f"{PATH[2]}{PATH[1]}"
    file = f"{file_path}\{kmlCode[1][1]}.kml"
    f = open(file,"w")
    f.write(kmlCode[0])
    f.close()
    filePath = os.path.abspath(file)
    return filePath

def exit_Script(filePath):
    #print(filePath)
    exitScript = f"JPG image(S) have been written to a KML file here: {filePath}."
    print(exitScript)
    
if __name__ == "__main__":
    #menu - get choice type and then path
    choice = menuExe() #[choice number, Path entered]
    #print(f"choice: {choice}")
    PATH = checkChoice(choice)
    #print(f"PATH: {PATH}")
    #Seach files
    img_paths = get_img_paths(choice[0],choice[1],".jpg")#EXIF data only exisit in jpegs
    #print(img_paths)
    #get Coords
    img_data = image_coordinates(img_paths)
    #write KML
    code = writeKMLcode(img_data,PATH)
    exit_Script(writeKMLfile(choice,code,PATH))
    input("Press any Key to Exit.")