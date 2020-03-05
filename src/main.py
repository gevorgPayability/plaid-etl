from utils import PlaidJsonExtractor
import pandas_gbq


def lambda_handler(event, context):

    key = event['key']
    command = event['command']

    plaid = PlaidJsonExtractor(path=key, bucket_name="payability-datalake")

    source = plaid.get_output_table(command)

    print(source)


if __name__ == "__main__":
    event = dict(
        key="plaid/asset_reports/date=2020-01-02/supplier_key=7f00f2d8-5709-45f6-b4d2-16c952045f1c/c00bc24c-8296-4925-81c4-f0d5029b9a14_2020-01-02T22:25:51Z.json",
        command="extract_transactions"
    )
    lambda_handler(event, context=2)
