# Checking GDPR Compliant Use of Cookies

## COMP-5355 Cyber Security and Application Project
### Project Requirement
* Visit the top 200 websites
* Check whether they claim to be GDPR compliant
* If yes, use the browser development tools or develop a browser plugin to identify how the website uses cookies 
* Check whether website really follows GDPR to handle cookies. 

## What can this program provides?
* Collecting top 240 websites from MOZ (https://moz.com/top500)
* Automatically analyzing the content of cookies that the website used
  * Selenium
  * Firefox Web Driver
  * Sqlite 3
    * To retrieve some of the cookies that cannot be found by Selenium from the cookies database in the Firefox web driver
* Grading each of the website according to whether the website is following the rules of GDPR to set the cookies on their website

## How to use it?
⭐️ Recommended to use MacOS
### Top-n Website Collection
1. Open "website_crawler.py" and 
2. Change "top200_websites = table[:240]" the number to the number of most popular website that you want to analyze.
3. Open terminal and go into the corresponding path
4. Type "python3.7 website_crawler.py"

### Cookies Analyzing
1. Open terminal and go into the corresponding path
2. Type "python3.7 main.py"
