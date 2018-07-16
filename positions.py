"""
Example to retrieve data from TD Ameritrade API
"""
import urllib.request
import base64

FIELDS = "positions"
with open("account_no.txt") as fObj:
    account_no = fObj.readlines()[0]
account_no = account_no.rstrip("\n")

URL = "https://api.tdameritrade.com/v1/accounts/{}?fields={}".format(account_no, FIELDS)
with open("oAuth_hash.txt") as fObj:
    oAuth_hash = fObj.readlines()[0]
oAuth_hash = oAuth_hash.rstrip("\n")

req = urllib.request.Request(URL)
req.add_header("Authorization", "Bearer {}".format(oAuth_hash).encode("utf-8"))

resp = urllib.request.urlopen(req)
print(resp.read())
