import csv
import io
import json


def process_csv(text):
    reader = csv.DictReader(io.StringIO(text))
    total_quantity = 0
    total_revenue = 0
    top_product = None
    top_quantity = -1

    for row in reader:
        quantity = int(row["Quantity"])
        price = float(row["Price"])
        total_quantity += quantity
        total_revenue += quantity * price
        if quantity > top_quantity:
            top_quantity = quantity
            top_product = row["Product"]

    if top_product is None:
        raise ValueError('CSV contains no data rows')

    return {
        "total_products_sold": total_quantity,
        "total_revenue": total_revenue,
        "highest_quantity_product": top_product,
    }


if __name__ == "__main__":
    with open("sample-data/monthly_sales.csv") as f:
        print(json.dumps(process_csv(f.read()), indent=2))

