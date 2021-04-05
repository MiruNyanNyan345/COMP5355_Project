import scrapy
import pandas as pd
import ssl
import urllib3
import requests


def getTop200Websites():
    ranking_web_url = "https://moz.com/top500"

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    html = requests.get(url=ranking_web_url, verify=False)

    df = pd.read_html(html.content)

    # dataframe[0] is ranking table
    table = df[0]

    # get top 250 websites from table
    top200_websites = table[:10]

    top200_websites.to_csv('top200.csv', index=False)

    return top200_websites
