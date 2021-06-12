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
        final = results.findNext("tr").findNext("tr").findNext("tr")
        title = final.findNext("th")
        title = unicodedata.normalize("NFKD", title.text.strip())
        stats = final.find_all("td")
        weekly_income = unicodedata.normalize("NFKD", stats[0].text.strip("$"))
        weekly_income = int(''.join(weekly_income.split(',')))
        postcode[i] = weekly_income
        print(title, weekly_income, "in suburb postcode", i)

result = pd.DataFrame(list(postcode.items()), columns = ["Postcode", 'Weekly Income'])

result.to_csv("weeklyIncome.csv", index = "Postcode")
