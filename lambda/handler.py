import json
import os
from decimal import Decimal
from urllib.parse import unquote_plus

import boto3

from processor import process_csv

ENDPOINT = os.environ.get("AWS_ENDPOINT_URL")
s3 = boto3.client("s3", endpoint_url=ENDPOINT)
dynamodb = boto3.resource("dynamodb", endpoint_url=ENDPOINT)
table = dynamodb.Table(os.environ["TABLE_NAME"])


def handler(event, context):
    for record in event["Records"]:
        body = json.loads(record["body"])

        # Skip the automatic S3 test event
        if "Records" not in body:
            continue

        for s3_record in body["Records"]:
            bucket = s3_record["s3"]["bucket"]["name"]
            key = unquote_plus(s3_record["s3"]["object"]["key"])

            try:
                obj = s3.get_object(Bucket=bucket, Key=key)
                text = obj["Body"].read().decode("utf-8")
                result = process_csv(text)
                table.put_item(Item={
                    "file_name": key,
                    "status": "SUCCESS",
                    "total_products_sold": result["total_products_sold"],
                    "total_revenue": Decimal(str(result["total_revenue"])),
                    "highest_quantity_product": result["highest_quantity_product"],
                })
            except Exception as e:
                table.put_item(Item={
                    "file_name": key,
                    "status": "FAILED",
                    "error": str(e),
                })
                raise
