from bs4 import BeautifulSoup
import pandas as pd
import unicodedata
import geopandas as gpd
import requests

data = gpd.read_file('./ll_gda94/sde_shape/whole/VIC/VMLITE/layer/vmlite_postcode_polygon.shp')
postcode = {}

for i in list(data["POSTCODE"]):
    u = 'https://quickstats.censusdata.abs.gov.au/census_services/getproduct/census/2016/quickstat/POA' + \
        str(i) + '?opendocument'
    page = requests.get(u)
    soup = BeautifulSoup(page.text, 'html.parser')
    section = soup.find(id="summaryTableAP")
    if section and len(section.find_all('table')) >= 3:
        results = section.findNext('table').findNext('table').findNext("table")
        final = results.findNext("tr").findNext("tr").findNext(
            "tr").findNext("tr").findNext("tr").findNext("tr")
        stats = final.find_all("td")
        numCar = float(unicodedata.normalize("NFKD", stats[0].text.strip()))
        postcode[i] = numCar
        print("Number of car", numCar, "in suburb postcode", i)

result = pd.DataFrame(list(postcode.items()), columns = ["Postcode", 'Number of Car'])

result.to_csv("carNumber.csv", index = "Postcode")
