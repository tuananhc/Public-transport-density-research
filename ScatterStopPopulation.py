from UsefulMethods import distance
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import sys
from sklearn.linear_model import LinearRegression

import warnings
warnings.filterwarnings("ignore")

LONGLATTOM = 111000
# read the shape file of Victoria suburb
victoria_map = gpd.read_file('./ll_gda94/sde_shape/whole/VIC/VMLITE/layer/vmlite_postcode_polygon.shp')
victoria_map = victoria_map.to_crs(epsg=4326)

# read the population dataset
population_dict = pd.read_csv("populationPerPostcode.csv").set_index('Postcode').to_dict()
# function to get population for a postcode
def getPopulation(postcode):
    try:
        temp = population_dict['Population'][int(postcode)]
    except:
        temp = np.NaN
    return temp

# take the position of bus stops since we limited our region
transport_pd = pd.read_csv('material/metro_' + sys.argv[1]  + '.csv', encoding = 'ISO-8859-1')
allpoint = []
for index, row in transport_pd.iterrows():
    allpoint.append(Point(row[" LONGITUDE"], row[" LATITUDE"]))

# count the number of stops in polygon
def counter(polygon):
    total = 0
    for point in allpoint:
        if point.within(polygon):
            total += 1
    return total

# take the stops within a polygon
def takeInnerStop(polygon, allpoint):
    inner = []
    for point in allpoint:
        if point.within(polygon):
            inner.append(point)
    return inner

# take the centroid of Melbourne CBD
melbournePolygon = victoria_map.loc[victoria_map['POSTCODE']=='3000'].set_index('POSTCODE')
melbournePolygon = melbournePolygon.loc['3000', 'geometry']
melbourneCentroid = melbournePolygon.centroid
# calculate distance to the centroid
def distanceToCentroid(polygon):
    return distance(polygon.centroid.x, polygon.centroid.y, melbourneCentroid.x, melbourneCentroid.y)

# limit our region
victoria_map['counter'] = victoria_map['geometry'].apply(counter)
victoria_map = victoria_map[victoria_map['counter']>0]
victoria_map['distanceToCentroid'] = victoria_map['geometry'].apply(distanceToCentroid)
temp = victoria_map[victoria_map['counter'] > 0]['distanceToCentroid'].max()
victoria_map = victoria_map[victoria_map['distanceToCentroid']<=temp]
victoria_map['centroidX'] = victoria_map['geometry'].centroid.x
victoria_map['centroidY'] = victoria_map['geometry'].centroid.y
xMax = victoria_map[victoria_map['counter'] > 0]['centroidX'].max()
xMin = victoria_map[victoria_map['counter'] > 0]['centroidX'].min()
yMax = victoria_map[victoria_map['counter'] > 0]['centroidY'].max()
yMin = victoria_map[victoria_map['counter'] > 0]['centroidY'].min()
victoria_map = victoria_map[victoria_map['centroidX']<=xMax]
victoria_map = victoria_map[victoria_map['centroidX']>=xMin]
victoria_map = victoria_map[victoria_map['centroidY']<=yMax]
victoria_map = victoria_map[victoria_map['centroidY']>=yMin]

# Calculate the data for plotting
victoria_map['population'] = victoria_map['POSTCODE'].apply(getPopulation)
victoria_map = victoria_map[victoria_map['population'].notnull()]

for index, row in victoria_map.iterrows():
    plt.scatter(row["population"], row["counter"], c ='b')

plt.savefig('./output/' + sys.argv[2], dpi=1200)

plt.title("Scatter plot of population with number of " + sys.argv[1] + " stops in a suburb")
plt.xlabel("Population")
plt.ylabel("Number of stops")

plt.savefig('./output/' + sys.argv[2], dpi=1200)

x = []
y = []
# Plot the data and save figure
for index, row in victoria_map.iterrows():
    plt.scatter(row["population"], row["counter"], c ='b')
    x.append([row["population"]])
    y.append(row["counter"])

reg = LinearRegression().fit(x, y)

xline = np.linspace(victoria_map["population"].min(), victoria_map["population"].max())
yline = reg.intercept_ + reg.coef_[0]*xline
plt.plot(xline, yline)

print("Linear Line: number of stops = " + str(reg.intercept_) + " + " + str(reg.coef_[0]) + "*population")
print("r2 = " + str(reg.score(x,y)))

plt.title("Scatter plot of population with number of " + sys.argv[1] + " stops in a suburb")
plt.xlabel("Population")
plt.ylabel("Number of stops")

plt.savefig('./output/fitted' + sys.argv[2], dpi=1200)