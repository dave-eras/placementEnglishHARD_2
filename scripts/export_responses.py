import os
from pathlib import Path

import boto3
import pandas as pd


def main() -> None:
    table_name = os.environ.get("DYNAMODB_TABLE", "language_test_responses_v15")
    region_name = os.environ.get("AWS_REGION", "eu-west-3")

    table = boto3.resource("dynamodb", region_name=region_name).Table(table_name)
    items = []
    response = table.scan()
    items.extend(response.get("Items", []))

    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response.get("Items", []))

    output_path = Path("responses.xlsx")
    pd.DataFrame(items).to_excel(output_path, index=False)
    print(f"Exported {len(items)} responses to {output_path}")


if __name__ == "__main__":
    main()
