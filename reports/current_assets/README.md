# Report Current Assets

This report creates an Excel file with the current state of the Adobe subscriptions (assets), with one row per
asset item. There is no date range: the asset status is the status the asset has at the moment the report runs.

Items with quantity 0 are skipped. Production assets on the hubs excluded by the Approved Requests report are
excluded as well.

# Available parameters

Assets can be parametrized by:

* Product
* Marketplace
* Asset Status (current)
* Environment
* Three years commitment

# Columns

* Asset ID, Asset Status, End Customer Subscription ID, Product ID, Product Name
* Provider ID, Provider Name, Hub ID, Hub Name, Marketplace ID, Marketplace Name, Connection Type
* Reseller ID, Reseller External ID, Reseller Name, Customer ID, Customer External ID, Customer Name, Created At
* Adobe Customer ID, Adobe VIP Number, Adobe User Email, Discount Group Licenses, Discount Group Consumables
* Renewal Date, Auto Renewal Status, 3YC Status, 3YC Start Date, 3YC End Date, 3YC Recommitment Status,
  External Reference ID
* Item Name, MPN, Current Quantity, Unit of Measure, Item Type, Billing Period
* Exported At

Command to create report: ccli report execute current_assets -d .
