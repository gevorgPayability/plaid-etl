import pandas as pd
import json
from pandas.io.json import json_normalize
import boto3


class PlaidJsonExtractor:

    def __init__(self, path, bucket_name):
        self.path = path
        self.bucket_name = bucket_name
        self.client = boto3.client('s3')
        self.data = self.read_s3_json()

    def read_s3_json(self):
        "Reads json from S3 as a local dictionary"
        json_stream = self.client.get_object(Bucket=self.bucket_name, Key=self.path)[
            'Body'].read().decode('utf-8')
        return json.loads(json_stream)['report']

    def extract_transactions(self):
        plaid_transaction_history = json_normalize(
            self.data, ['items', 'accounts', 'transactions'])
        return plaid_transaction_history

    def extract_historical_balances(self):
        historical_balances = json_normalize(self.data,  ['items', 'accounts', 'historical_balances'], meta=[
            ['items', 'accounts', 'account_id']])

        historical_balances = historical_balances.rename(columns={
            "items.accounts.account_id": "account_id"
        })

        return historical_balances

    def extract_accounts_info(self):
        items = self.data['items']
        results = []
        for item in items:
            item_info = {}

            for element in ['institution_name', 'institution_id', 'item_id']:
                item_info[element] = item.get(element, None)

            for account in item.get('accounts'):

                account_results = {}
                for element in ["account_id", "mask", "name", "official_name",
                                "type", "subtype"]:
                    account_results[element] = account.get(element, None)

                account_results.update(item_info)

                results.append(account_results)

        return json_normalize(results)


path = "plaid/asset_reports/date=2020-01-02/supplier_key=7f00f2d8-5709-45f6-b4d2-16c952045f1c/c00bc24c-8296-4925-81c4-f0d5029b9a14_2020-01-02T22:25:51Z.json"
plaid = PlaidJsonExtractor(path=path, bucket_name="payability-datalake")

accounts_info = plaid.extract_accounts_info()

accounts_info.columns

accounts_info.head()


# transactions = plaid.extract_transactions()
# historical_balances = plaid.extract_historical_balances()
#
#
# items = plaid.data["items"]
#
# type(items)
# type(items[0])
#
#
# items[0].keys()
# accounts = items[0]['accounts']
# len(accounts)
# account_1 = accounts[0]
# account_1.keys()
# len(items)
#
#
# extract_accounts_info()
