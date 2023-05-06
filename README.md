# jpg2kml
make a kml file from the geolocation of JPG's

Searches recursively through folders and returns all the jpg files, then grabs each geo position, then writing that data into a kml geolocation file.
IF any given jpg does not have a geotag, then it will calculate the center placement of all the other jpgs and place the jpg link there. 
