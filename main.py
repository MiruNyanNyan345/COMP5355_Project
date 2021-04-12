import glob
import json
import os
import shutil
import sqlite3
import time
import datetime

import pandas as pd
from tqdm import tqdm
import selenium.common
from selenium.webdriver.firefox.options import Options
import selenium.webdriver
from mozprofile import FirefoxProfile

import webslist_crawler
import analysis

# top_200 = webslist_crawler.getTop200Websites()

top_200 = pd.read_excel("top240.xlsx")


def unixToDT(ts_epoch):
    try:
        return True, datetime.datetime.fromtimestamp(ts_epoch)
    except ValueError as e:
        print(e)
        return False, -1


def merge_cookies_dict(cookies_lst1, cookies_lst2):
    final_cookies_lst = []

    for c1 in cookies_lst1:
        repeated = False
        for c2 in cookies_lst2:
            if c1["name"] == c2["name"]:
                repeated = True
                break
        if not repeated:
            final_cookies_lst.append(c1)
    final_cookies_lst.extend(cookies_lst2)
    return final_cookies_lst


def get_cookies(web_addr):
    profile_conf_name = "/tmp/gdpr-cookies-analysis/gdpr-cookies-analysis.default/"
    FirefoxProfile(profile=profile_conf_name)

    profile = selenium.webdriver.FirefoxProfile(profile_conf_name)

    profile.set_preference("network.cookie.cookieBehavior", 0)
    profile.update_preferences()
    options = Options()
    options.headless = True
    driver = selenium.webdriver.Firefox(firefox_profile=profile, options=options,
                                        executable_path="/usr/local/bin/geckodriver")

    web = "https://" + web_addr
    # print("Website: {}".format(web))
    try:
        driver.get(url=web)
        selenium_cookies = driver.get_cookies()

        profile_repo = glob.glob('/var/folders/7y/kdk1h6ss42j5kb4mc30xdd9w0000gn/T/rust_mozprofile*')
        latest_profile_repo = max(profile_repo, key=os.path.getctime)

        # Check whether the profile_repo has reported
        # print(latest_profile_repo)

        db_source = latest_profile_repo + "/cookies.sqlite"
        db_destination = "/tmp/gdpr-cookies-analysis/gdpr-cookies-analysis.default/cookies.sqlite"

        shutil.copyfile(db_source, db_destination)

        con = sqlite3.connect(db_destination)
        cur = con.cursor()
        cur.execute("SELECT * FROM moz_cookies")
        rows = cur.fetchall()

        # show cookies name
        # print("")
        # for des in cur.description:
        #     print(des[0], end=", ")
        # print("")
        # print(rows)
        # print(selenium_cookies)

        sqlite3_cookies = []
        for cookie in rows:
            cookie_json = {"name": cookie[2], "value": cookie[3], "domain": cookie[4], "path": cookie[5],
                           "expiry": cookie[6], "secure": bool(cookie[9]), "httpOnly": bool(cookie[10])}
            sqlite3_cookies.append(cookie_json)

        con.close()

        # for cookie in selenium_cookies:
        #     print("First-Party Cookies ({}): {}".format(web_addr, cookie))
        # for cookie in sqlite3_cookies:
        #     print("First-Party Cookies ({}): {}".format(web_addr, cookie))

        for item in os.listdir(profile_conf_name):
            if item.endswith(".sqlite"):
                os.remove(os.path.join(profile_conf_name, item))

        driver.close()

        final_cookies = merge_cookies_dict(selenium_cookies, sqlite3_cookies)
        # print(final_cookies)
        # for cookie in final_cookies:
        #     print("Final Cookie: ({}): {}".format(web_addr, cookie))
        # print(final_cookies)
        print("")
    except Exception as e:
        print("Website: {}, Error: {}".format(web, e))
        return False, str(e)

    return True, final_cookies


def main():
    # top200_cookies = []
    top200_cookies_df = pd.DataFrame(columns=["website",
                                              "status",
                                              "name",
                                              "value",
                                              "path",
                                              "domain",
                                              "creation",
                                              "expiry",
                                              "cookieType",
                                              "cookieTotalSeconds",
                                              "secure",
                                              "httpOnly",
                                              "exception"])
    top200_grade_df = pd.DataFrame(columns=["website",
                                            "domainGrade",
                                            "httpOnlyGrade",
                                            "secureGrade",
                                            "expiryGrade",
                                            "avgGrade"])
    for web in tqdm(top_200["Root Domain"]):
        print("")
        print(web)
        status, results = get_cookies(web)
        if status:
            for result in results:
                composeDict = {}
                # composeDict.update({"website": web, "status": status, "creation": datetime.datetime.now().timestamp()})
                composeDict.update(result)
                if "expiry" in result.keys():
                    # if the cookie expiry data is out of range
                    # which means that cookie will be removed when the browser is closed
                    result, cookieExpSeconds = unixToDT(result["expiry"])
                    if result:
                        intervalSeconds = (cookieExpSeconds - datetime.datetime.now().replace(
                            microsecond=0)).total_seconds()
                        composeDict.update(
                            {"website": web, "status": status,
                             "creation": datetime.datetime.now().replace(microsecond=0),
                             "expiry": cookieExpSeconds,
                             "cookieType": "persistent",
                             "cookieTotalSeconds": intervalSeconds})
                    else:
                        # assume that cookie is session cookie
                        composeDict.update(
                            {"website": web, "status": status,
                             "creation": datetime.datetime.now().replace(microsecond=0),
                             "expiry": None, "cookieType": "session"})
                else:
                    composeDict.update(
                        {"website": web, "status": status, "creation": datetime.datetime.now().replace(microsecond=0),
                         "expiry": None, "cookieType": "session"})
                top200_cookies_df = top200_cookies_df.append(composeDict, ignore_index=True)
        else:
            top200_cookies_df = top200_cookies_df.append({"website": web,
                                                          "status": status,
                                                          "exception": results}, ignore_index=True)
            continue

        if top200_cookies_df.loc[top200_cookies_df['website'] == web].empty:
            top200_grade_df = top200_grade_df.append({"website": web,
                                                      "domainGrade": None,
                                                      "httpOnlyGrade": None,
                                                      "secureGrade": None,
                                                      "expiryGrade": None,
                                                      "avgGrade": None}, ignore_index=True)
        else:
            analysis_result = analysis.cookies_analysis(website=web,
                                                        web_rows=top200_cookies_df.loc[
                                                            top200_cookies_df['website'] == web])
            analysis_result.update({"website": web})
            top200_grade_df = top200_grade_df.append(analysis_result, ignore_index=True)

    top200_cookies_df.to_csv('top200_cookies.csv', index=False)
    top200_grade_df.to_csv('top200_grade.csv', index=False)

    # with open('top200_cookies.json', 'w') as file:
    #     json.dump(top200_cookies, file)


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print("Running Time: {}".format(end_time - start_time))
