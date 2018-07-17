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

    @dump_message
    def _send_request(self, url):
        """Send the request based on the base url plus the supplied url.
        """
        base_url = "https://api.tdameritrade.com/v1/accounts/{}".format(self.account_no)
        url = base_url + url
        print(url)
        request = urllib.request.Request(url)
        request.add_header("Authorization", "Bearer {}".format(self.oauth_hash).encode("utf-8"))
        response = urllib.request.urlopen(request)
        self.message = json.loads(response.read().decode("utf-8"))

    def _account_info(self, fields="positions,orders"):
        """Get account information.
        """
        url = "?fields={}".format(fields)
        self._send_request(url)

    def _orders(self, max_results=100, from_date=None, to_date=None, order_status="FILLED"):
        """Get order information.
        """
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

    def get_month_filled(self):
        """Get the filled positions within the last 30 days.
        """
        to_date = datetime.strftime(datetime.today(), format="%Y-%m-%d")
        from_date = datetime.strftime(datetime.today() - timedelta(35), format="%Y-%m-%d")
        self._orders(max_results=100, from_date=from_date, to_date=to_date, order_status="FILLED")
        orders = self.message
        symbols = list()
        for order in orders:
            symbols.append(order["orderLegCollection"][0]["instrument"]["symbol"])
        return symbols

def test():
    """Run tests.
    """
    app = TDAmeritrade(filename_account="account_no.txt", filename_oauth="oAuth_hash.txt")
    #app._account_info()
    #app._orders()
    print(app.get_month_filled())

if __name__ == "__main__":
    test()
