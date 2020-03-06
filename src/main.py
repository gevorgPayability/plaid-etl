from utils import PlaidJsonExtractor, get_secret
import pandas_gbq
import json
from google.oauth2 import service_account


def lambda_handler(event, context):

    key = event['key']
    command = event['command']
    env = event.get('env', 'prod')

    secret = get_secret('/bigqueryexport-183608/ml')
    bq_json_info = json.loads(secret['json'])
    credentials = service_account.Credentials.from_service_account_info(
        bq_json_info)

    plaid = PlaidJsonExtractor(path=key, bucket_name="payability-datalake")

    data = plaid.run_extraction(command)
    output_table_name = plaid.get_output_table(command, env)

    pandas_gbq.to_gbq(data, output_table_name,
                      if_exists='append', credentials=credentials)


if __name__ == "__main__":
    event = dict(
        key="plaid/asset_reports/date=2020-01-02/supplier_key=7f00f2d8-5709-45f6-b4d2-16c952045f1c/c00bc24c-8296-4925-81c4-f0d5029b9a14_2020-01-02T22:25:51Z.json",
        command="extract_transactions",
        env='dev'
    )
    lambda_handler(event, context=2)
