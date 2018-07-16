"""
Example to retrieve data from TD Ameritrade API
"""
import urllib.request
from datetime import datetime, timedelta
from pdb import set_trace

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

    def __set_request(self, url):
        """Set the request based on the base url plus the supplied url.
        """
        base_url = "https://api.tdameritrade.com/v1/accounts/{}".format(self.account_no)
        url = base_url + url
        print(url)
        request = urllib.request.Request(url)
        request.add_header("Authorization", "Bearer {}".format(self.oauth_hash).encode("utf-8"))
        return request

    def get_account_info(self, fields="positions"):
        """Get account information.
        """
        url = "?fields={}".format(fields)
        request = self.__set_request(url)
        response = urllib.request.urlopen(request)
        self.message = response.read()

    def get_orders(self, max_results=50, from_date=None, to_date=None, order_status=None):
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
        request = self.__set_request(url)
        response = urllib.request.urlopen(request)
        self.message = response.read()

def test():
    """Run tests.
    """
    app = TDAmeritrade(filename_account="account_no.txt", filename_oauth="oAuth_hash.txt")
    app.get_account_info()
    app.get_orders()
    print(app.message)

if __name__ == "__main__":
    test()
