# TsuNotMe
If a tsunami hit San Francisco, where would you go? TsuNotMe helps find an escape route to the closest safe destination.

![screenshot](https://github.com/BFangs/TsuNotMe/tree/master/static/img/screenshot.png)
## Features
Search using an elevation threshold, a starting location, a desired time frame, and a mode of travel. The closest destination over the elevation threshold will be selected from the database and a route will be displayed on the map. Login to save and view search history.
### Tech Stack
**Backend:** Python, Flask, SQLAlchemy, PostgreSQL  
**Frontend:** Javascript, jQuery, HTML5, CSS3, Bootstrap  
**Libraries:** GDAL, NumPy  
**API:** Google Maps
### Requirements
My app runs using Bay area elevation data that I processed and populated into a Postgres database. I downloaded the elevation dataset from the [USGS website](https://www.sciencebase.gov/catalog/item/581d224ee4b08da350d547ca). There are many different options available and out of them I chose a raster tile of the National Elevation Dataset at a 1/3 arc-second resolution. This resource provides metadata files containing latitude/longitude bounding coordinates as well as row/column counts for the raster tile. The data can be read as a NumPy array using the GDAL library and processed using the loading functions in my model. Note: PyPI package for GDAL would not install correctly on linux so install can be time consuming.
### Data Model
The total area was broken down into 11,881 tiles and the local maxima (high elevation points) within each tile array were loaded into the database creating a one to many relationship between the tiles table and the points table. When a user starts a new search the tiles table is queried with a range surrounding the start location which then radiates outwards until a suitable point is found.
### Future
I'm excited to work on deploying this version. Some of the features I'd like to work on next are:
* Creating user groups to allow family destination searches
* Displaying multiple end points for users to choose between
* Including business information around destinations
* Expanding supported area
* Analyzing route difficulty for walking or biking (slope)

#### About the Developer
Boya is a recent graduate of Hackbright Academy, a San Francisco-based accelerated full-stack software development program for women. Prior to that, she graduated from college with a degree in biology and then spent time working in biotech. She was involved in DNA sequencing services and streamlined prep kit protocols for Next Generation Sequencing. She is excited about building her skills as a full-stack software engineer and is interested in problem solving on a different platform. In her spare time, Boya can be found exploring local parks with her dog and contemplating the spontaneous appearances of sand.

[Check Boya out on LinkedIn!](https://www.linkedin.com/in/boyafang/)
