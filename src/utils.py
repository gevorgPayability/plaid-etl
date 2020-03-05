import json
from pandas.io.json import json_normalize
import boto3


class PlaidJsonExtractor:

    settings = {
        'extract_transactions': 'plaid.transactions',
        'extract_historical_balances': 'plaid.historical_balances',
        'extract_accounts_info': 'plaid.accounts_info',

    }

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

    def run_extraction(self, command):
        "Dynamically run method"
        assert command in list(self.settings.keys()
                               ), f"Command {command} is not allowed"

        runner = getattr(self, command, None)
        assert callable(runner), "Command '%s' is invalid" % command

        data = runner()

        return data

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

    def get_output_table(self, command):
        assert command in list(self.settings.keys())

        return self.settings.get(command)
