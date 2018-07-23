"""
Example to retrieve data from TD Ameritrade API
"""
import urllib.request
import time
import json
from datetime import datetime, timedelta
from pdb import set_trace
import numpy as np
import pandas as pd


def dump_message(fn):
    """Dump the message to file.
    Useful for debugging the message parser.
    """
    def wrapper(self, url, data=None):
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

    @dump_message
    def _send_request(self, url, data=None):
        """Send the request based on the base url plus the supplied url.
        """
        base_url = "https://api.tdameritrade.com/v1/"
        url = base_url + url
        print(url)
        request = urllib.request.Request(url)
        request.add_header("Authorization", "Bearer {}".format(self.oauth_hash).encode("utf-8"))
        if data is None:
            response = urllib.request.urlopen(request)
            self.message = json.loads(response.read().decode("utf-8"))
        else:
            request.add_header("Content-Type", "application/json; charset=utf-8")
            data = json.dumps(data).encode("utf-8")
            request.add_header("Content-Length", len(data))
            response = urllib.request.urlopen(request, data=data)

    def _account_info(self, fields="positions,orders"):
        """Get account information.
        """
        url = "accounts/{}?fields={}".format(self.account_no, fields)
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
            url = "orders?accountId={}&maxResults={}&fromEnteredTime={}&toEnteredTime={}"\
                .format(self.account_no, max_results, from_date, to_date)
        else:
            url = "orders?accountID={}&maxResults={}&fromEnteredTime={}&toEnteredTime={}&status={}"\
                .format(self.account_no, max_results, from_date, to_date, order_status)
        self._send_request(url)

    def _transactions(self, trans_type="TRADE", from_date=None, to_date=None, symbol="SPYG"):
        """Get transactions.
        """
        if to_date is None:
            to_date = datetime.strftime(datetime.today(), format="%Y-%m-%d")
        if from_date is None:
            from_date = datetime.strftime(datetime.today() - timedelta(35), format="%Y-%m-%d")
        if symbol is None:
            url = "accounts/{}/transactions?type={}&startDate={}&endDate={}"\
                    .format(self.account_no, trans_type, from_date, to_date)
        else:
            url = "accounts/{}/transactions?type={}&symbol={}&startDate={}&endDate={}"\
                    .format(self.account_no, trans_type, symbol, from_date, to_date)
        self._send_request(url)

    def get_watchlists(self):
        """Get all watchlists in account.
        """
        url = "accounts/{}/watchlists".format(self.account_no)

    def get_watchlist(self, id="1148189253"):
        """Get watchlist. Defaults to CommissionFree.
        """
        url = "accounts/{}/watchlists/{}".format(self.account_no, id)
        self._send_request(url)

    def get_refresh_token(self):
        """Get a refresh token.
        see: https://developer.tdameritrade.com/content/simple-auth-local-apps
        see: https://developer.tdameritrade.com/authentication/apis/post/token-0
        """

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

    def get_commission_free_etfs(self):
        """Get a list of the commission free ETFs from
        a watchlist.
        """
        id = "1148189253"
        self.get_watchlist(id=id)
        symbols = list()
        for itm in self.message["watchlistItems"]:
            symbols.append(itm["instrument"]["symbol"])
        return symbols

    def create_saved_order(self, symbol=None, price=None, quantity=0, instruction=None):
        """Create a saved order.
        Args
        instruction (str): "BUY" | "SELL"
        """
        url = "accounts/{}/savedorders".format(self.account_no)
        data = {\
            "orderType": "LIMIT",
            "session": "NORMAL",
            "price": price,
            "duration": "DAY",
            "orderStrategyType": "SINGLE",
            "orderLegCollection": [
                {
                    "instruction": instruction,
                    "quantity": quantity,
                    "instrument": {
                        "symbol": symbol,
                        "assetType": "EQUITY"
                    }
                }
            ]
        }
        self._send_request(url, data=data)

    def place_order(self, symbol=None, price=None, quantity=0, instruction=None):
        """Create a saved order.
        Args
        instruction (str): "BUY" | "SELL"
        """
        url = "accounts/{}/orders".format(self.account_no)
        data = {\
            "orderType": "LIMIT",
            "session": "NORMAL",
            "price": price,
            "duration": "DAY",
            "orderStrategyType": "SINGLE",
            "orderLegCollection": [
                {
                    "instruction": instruction,
                    "quantity": quantity,
                    "instrument": {
                        "symbol": symbol,
                        "assetType": "EQUITY"
                    }
                }
            ]
        }
        self._send_request(url, data=data)

    def get_price_history(self, symbol=None, period_type="month", period="3", frequency_type="daily",\
            frequency=1, end_date=int(time.time()*1000), start_date=None, extended_hours="true"):
        """Get the price history.
        """
        if start_date is None:
            url = "marketdata/{}/pricehistory?periodType={}&period={}&frequencyType={}&frequency={}&endDate={}&needExtendedHoursData={}"\
                .format(symbol, period_type, period, frequency_type, frequency, end_date, extended_hours)
        else:
            url = "marketdata/{}/pricehistory?periodType={}&&frequencyType={}&frequency={}&endDate={}&startDate={}&needExtendedHoursData={}"\
                .format(symbol, period_type, frequency_type, frequency, end_date, start_date, extended_hours)
        self._send_request(url)
        data = np.array([[datetime.fromtimestamp(t["datetime"]/1000.).date,
                          t["open"], t["high"], t["low"], t["close"], t["volume"]]
                         for t in self.message["candles"]])
        data = pd.DataFrame(index=data[:, 0],
                            columns=["open", "high", "low", "close", "volume"],
                            data=data[:, 1:])
        return data

    def get_quotes(self, symbols=None):
        """Get price quotes
        """
        symbol_url = "%2C".join(symbols)
        url = "marketdata/quotes?symbol={}".format(symbol_url)
        self._send_request(url)

def test():
    """Run tests.
    """
    app = TDAmeritrade(filename_account="account_no.txt", filename_oauth="oAuth_hash.txt")
    #app._account_info()
    #app._orders()
    #app._transactions(symbol="SPYG")
    #app.get_watchlist()
    #print(app.get_commission_free_etfs())
    #print(app.get_recent_transactions())
    #print(app.get_recent_orders())
    #app.create_saved_order(symbol="SPYG", price=1, quantity=1, instruction="BUY")
    print(app.get_price_history(symbol="SPYV"))
    #app.get_quotes(["SPYV", "SPYG"])
    #app.place_order(symbol="SPYG", price=1, quantity=1, instruction="BUY")
    #print(app.message)

if __name__ == "__main__":
    test()
