# comp20008-2021sm1a2

Group members: 
- Dao Le Tran - 1133601
- Truong Giang Hoang - 1166323
- Tuan Anh Chau - 1166394
- Xuan Bach Phan - 1166353

Notes: cd to the folder containing this project and copy the below command line to the terminal to run.

1. All the modules for this project:
    - numpy
    - pandas
    - geopandas
    - matplotlib
    - shapely
    - sys
    - random
    - scipy
    - bs4
    - unicodedata
    - requests

2. Materials:
    - material folder: csv of transportation stops taken from AURIN: portal.aurin.org.au
    - ll_gda94 folder: shape file for Victoria suburbs services.land.vic.gov.au
    - scraping data from: quickstats.censusdata.abs.gov.au

3. Scraping data:
    Running srape:

py scrapeCar.py

py scrapeIncome.py

py scrapePopulation.py

4. Running code for the project:
    a. Plotting the map of stop points and heatmap for number of stops

py numStopsHeatMap.py train trainStopsHeatMap.png 5

py numStopsHeatMap.py tram tramStopsHeatMap.png 5

py numStopsHeatMap.py bus busStopsHeatMap.png 1

    b. Plotting heatmap for information:

py heatmapCar.py heatmapCar.png

py heatmapIncome.py heatmapIncome.png

py heatmapPopulation.py heatmapPopulation.png

py heatmapPopuDens.py heatmapPopuDens.png

    c. Plotting information with respect to each suburb

        Scatter plot of average distance to a stop and number of household car

py scatterDistanceCar.py tram tramScatterDistanceCar.png

py scatterDistanceCar.py train trainScatterDistanceCar.png

py scatterDistanceCar.py bus busScatterDistanceCar.png

        Scatter plot of average distance to a stop and average income

py scatterDistanceIncome.py tram tramScatterDistanceIncome.png

py scatterDistanceIncome.py train trainScatterDistanceIncome.png

py scatterDistanceIncome.py bus busScatterDistanceIncome.png

        Scatter plot of average distance to a stop and population density

        Note: We will fit the data to a y=a+b/x line, the fit line will be printed to the terminal 

py scatterDistancePopu.py tram tramscatterDistancePopu.png

py scatterDistancePopu.py train trainscatterDistancePopu.png

py scatterDistancePopu.py bus busScatterDistancePopu.png

        Scatter plot of number of stop and population
        Note: We will fit the data to a y=a+b*x line, the fit line will be printed to the terminal 

py scatterStopPopulation.py tram tramScatterStopPopulation.png

py scatterStopPopulation.py train trainScatterStopPopulation.png

py scatterStopPopulation.py bus busScatterStopPopulation.png
