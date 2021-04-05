import numpy as np
import datetime
import math
import dateutil.relativedelta


# def unixToDT(ts_epoch):
#     return datetime.datetime.fromtimestamp(ts_epoch)

# def expiry_analysis(creation_lst, expiry_lst):
#     # Cookies can expire. A cookie with no expiration date specified will expire when the browser is closed.
#     # These are often called session cookies because they are removed after the browser session ends
#     creations = [unixToDT(c) for c in creation_lst]
#     print(creations)
#     expires = []
#     for e in expiry_lst:
#         if not math.isnan(e):
#             expires.append(unixToDT(e))
#         else:
#             expires.append(0)
#
#     cookie_exp = []
#     for c, e in zip(creations, expires):
#         if e != 0:
#             rd = dateutil.relativedelta.relativedelta(e, c)
#             cookie_exp.append({"type": "persistent",
#                                "year": rd.years, "month": rd.months, "days": rd.days,
#                                "hours": rd.hours, "minutes": rd.minutes, "seconds": rd.seconds})
#         else:
#             cookie_exp.append({"type": "session"})
#
#     score_lst = []
#     for exp in cookie_exp:
#         if exp["type"] == "session":
#             score_lst.append(1)
#         elif exp["type"] == "persistent":
#             if exp["year"] > 0:
#                 score_lst.append(0)
#             else:
#                 score_lst.append(0.5)
#     return np.mean(score_lst)

def expiry_analysis(cookie_type, cookie_total_seconds):
    score_lst = []
    for cookie, totalSeconds in zip(cookie_type, cookie_total_seconds):
        if cookie == "session":
            score_lst.append(1)
        else:
            # According to the ePrivacy Directive, they should not last longer than 12 months
            totalSeconds = round(totalSeconds)
            # expiry in or longer 365 days
            if totalSeconds >= 31536000:
                score_lst.append(0)
            # expiry between a year and a half-year
            elif 31536000 > totalSeconds >= 15778463:
                score_lst.append(0.25)
            # expiry between a half-year and a month
            elif 15778463 > totalSeconds >= 2629743.83:
                score_lst.append(0.5)
            # expiry between a month and a day
            elif 2629743.83 > totalSeconds >= 86400:
                score_lst.append(0.75)
            # expiry less than one day
            elif 86400 > totalSeconds:
                score_lst.append(1)

    return np.mean(score_lst)


def same_domain_analysis(website, domains_lst):
    same_domain = 0
    for domain in domains_lst:
        if set(website.split('.')).intersection(set(domain.split('.'))):
            same_domain += 1
    return same_domain / len(domains_lst)


def httpOnly_analysis(https_lst):
    return sum(https_lst) / len(https_lst)


def secure_analysis(secure_lst):
    return sum(secure_lst) / len(secure_lst)


def cookie_grade(analysis):
    if analysis >= 0.75:
        grade = "A"
    elif 0.75 > analysis >= 0.5:
        grade = "B"
    elif 0.5 > analysis >= 0.25:
        grade = "C"
    else:
        grade = "F"
    return grade


def cookies_analysis(website, web_rows):
    df = web_rows
    domain_score = same_domain_analysis(website=website, domains_lst=df["domain"].values)
    httpOnly_score = httpOnly_analysis(https_lst=df["httpOnly"].values)
    secure_score = secure_analysis(secure_lst=df["secure"].values)
    expiry_score = expiry_analysis(cookie_type=df["cookieType"].values,
                                   cookie_total_seconds=df["cookieTotalSeconds"].values)

    domain_Grade = cookie_grade(domain_score)
    httpOnly_Grade = cookie_grade(httpOnly_score)
    secure_Grade = cookie_grade(secure_score)
    expiry_Grade = cookie_grade(expiry_score)
    average_Grade = cookie_grade(np.mean([domain_score, httpOnly_score, secure_score, expiry_score]))

    return {"domainGrade": domain_Grade,
            "httpOnlyGrade": httpOnly_Grade,
            "secureGrade": secure_Grade,
            "expiryGrade": expiry_Grade,
            "avgGrade": average_Grade}
