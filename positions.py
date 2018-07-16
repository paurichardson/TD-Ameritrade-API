"""
Example to retrieve data from TD Ameritrade API

Brent Maranzano
July 15, 2018
MIT LICENSE
"""
import urllib.request

FIELDS = "positions"
with open("account_no.txt") as fObj:
    account_no = fObj.readlines()[0]
account_no = account_no.rstrip("\n")
URL = "https://api.tdameritrade.com/v1/accounts/{}?fields={}".format(account_no, FIELDS)
req = urllib.request.Request(URL)

with open("oAuth_hash.txt") as fObj:
    oAuth_hash = fObj.readlines()[0]
oAuth_hash = oAuth_hash.rstrip("\n")
req.add_header("Authorization", "Bearer {}".format(oAuth_hash).encode("utf-8"))

resp = urllib.request.urlopen(req)

print(resp.read())
