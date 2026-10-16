import json, pandas as pd

df = pd.DataFrame(json.load(open("orders.json")))
print("rows:", len(df), "| unique ids:", df.id.nunique())
print("\nstatus values:\n", df.status.value_counts())
print("\nregions:\n", df.region.value_counts())
print("\nproducts:\n", df["product"].value_counts())
print("\ncurrencies:\n", df.currency.value_counts())
print("\ncolumns:", list(df.columns))

# show one order id that appears more than once
dup = df[df.duplicated("id", keep=False)].sort_values(["id", "updated_at"])
print("\nexample duplicated orders:\n", dup.head(8).to_string())