"""
Example to retrieve data from TD Ameritrade API
"""
import urllib.request
from datetime import datetime, timedelta
from pdb import set_trace
import json


def dump_message(fn):
    """Dump the message to file.
    Useful for debugging the message parser.
    """
    def wrapper(self, url):
        fn(self, url)
        with open("message.txt", mode='w') as file_obj:
            file_obj.writelines(json.dumps(self.message))

    return  wrapper

class TDAmeritrade:
    """Class to create http urls to conform to the TDAmeritrade API.
    """
    def __init__(self, filename_account, filename_oauth):
        """Get account information.
        """
        self.account_no = self.get_account_number(filename_account)
        self.oauth_hash = self.get_oauth_hash(filename_oauth)

        self.message = None

    @staticmethod
    def get_account_number(filename):
        """Open and read the file containing the account number.
        """
        with open(filename) as file_obj:
            account_no = file_obj.readlines()[0]
        account_no = account_no.rstrip("\n")
        return account_no

    @staticmethod
    def get_oauth_hash(filename):
        """Open and read the file containing the OAuth.
        """
        with open(filename) as file_obj:
            oauth_hash = file_obj.readlines()[0]
        oauth_hash = oauth_hash.rstrip("\n")
        return oauth_hash

    #@dump_message
    def _send_request(self, url, data=None):
        """Send the request based on the base url plus the supplied url.
        """
        base_url = "https://api.tdameritrade.com/v1/accounts/{}".format(self.account_no)
        url = base_url + url
        print(url)
        request = urllib.request.Request(url)
        request.add_header("Authorization", "Bearer {}".format(self.oauth_hash).encode("utf-8"))
        if data is None:
            response = urllib.request.urlopen(request)
        else:
            response = urllib.request.urlopen(request, data=data)
        self.message = json.loads(response.read().decode("utf-8"))

    def _account_info(self, fields="positions,orders"):
        """Get account information.
        """
        url = "?fields={}".format(fields)
        self._send_request(url)

    def _orders(self, max_results=100, from_date=None, to_date=None, order_status="WORKING"):
        """Get order information.
        order_status (str): Most likely FILLED | WORKING
        """
        order_status=None
        if to_date is None:
            to_date = datetime.strftime(datetime.today(), format="%Y-%m-%d")
        if from_date is None:
            from_date = datetime.strftime(datetime.today() - timedelta(35), format="%Y-%m-%d")
        if order_status is None:
            url = "/orders?maxResults={}&fromEnteredTime={}&toEnteredTime={}"\
                .format(max_results, from_date, to_date)
        else:
            url = "/orders?maxResults={}&fromEnteredTime={}&toEnteredTime={}&status={}"\
                .format(max_results, from_date, to_date, order_status)
        self._send_request(url)

    def _transactions(self, trans_type="TRADE", from_date=None, to_date=None, symbol="SPYG"):
        """Get transactions.
        """
        if to_date is None:
            to_date = datetime.strftime(datetime.today(), format="%Y-%m-%d")
        if from_date is None:
            from_date = datetime.strftime(datetime.today() - timedelta(35), format="%Y-%m-%d")
        if symbol is None:
            url = "/transactions?type={}&startDate={}&endDate={}"\
                    .format(trans_type, from_date, to_date)
        else:
            url = "/transactions?type={}&symbol={}&startDate={}&endDate={}"\
                    .format(trans_type, symbol, from_date, to_date)
        self._send_request(url)

    def _watchlist(self, id="1148189253"):
        """Get watchlist. Defaults to CommissionFree.
        """
        url = "/watchlists/{}".format(id)
        self._send_request(url)

    def get_recent_orders(self):
        """Get orders that were filled in the last 35 days. This is to
        comply with the 30 day hold criteria.
        """
        to_date = datetime.strftime(datetime.today(), format="%Y-%m-%d")
        from_date = datetime.strftime(datetime.today() - timedelta(35), format="%Y-%m-%d")
        self._orders(max_results=100, from_date=from_date, to_date=to_date, order_status="FILLED")
        orders = list()
        for order in self.message:
            orders.append(order["orderLegCollection"][0]["instrument"]["symbol"])
        return orders

    def get_recent_transactions(self):
        """Get orders that were filled in the last 35 days. This is to
        comply with the 30 day hold criteria.
        """
        to_date = datetime.strftime(datetime.today(), format="%Y-%m-%d")
        from_date = datetime.strftime(datetime.today() - timedelta(35), format="%Y-%m-%d")
        for sym in ["SPYG", "SPYV"]: #free_etfs:
            self._transactions(trans_type="BUY_ONLY", from_date=from_date,
                               to_date=to_date, symbol=sym)
        transactions = list()
        for trans in self.message:
            transactions.append({
                "date": trans["transactionDate"],
                "fee": trans["fees"]["commission"],
                "symbol": trans["transactionItem"]["instrument"]["symbol"]
            })
        return transactions

    def commission_free(self):
        id = "1148189253"
        self._watchlist(id=id)
        symbols = list()
        for itm in self.message["watchlistItems"]:
            symbols.append(itm["instrument"]["symbol"])
        return symbols

    def create_order(self, symbol=None, price=None, quantity=0):
        url = "/savedorders"
        data = \
            { "complexOrderStrategyType": "NONE",
                  "orderType": "LIMIT",
                  "session": "NORMAL",
                  "price": "6.45",
                  "duration": "DAY",
                  "orderStrategyType": "SINGLE",
                  "orderLegCollection": [
                      {
                          "instruction": "BUY",
                          "quantity": 1,
                          "instrument": {
                              "symbol": "AAPL",
                              "assetType": "EQUITY"
                          }
                      }
                  ]
            }

        data = json.dumps(data).encode()
        set_trace()
        self._send_request(url, data=data)


def test():
    """Run tests.
    """
    app = TDAmeritrade(filename_account="account_no.txt", filename_oauth="oAuth_hash.txt")
    #app._account_info()
    #app._orders()
    #app._transactions(symbol="AAPL")
    #app._watchlist()
    app.create_order()
    #set_trace()
    #print(app.message)
    #print(app.commission_free())
    #print(app.get_recent_transactions())
    #print(app.get_recent_orders())

if __name__ == "__main__":
    test()
