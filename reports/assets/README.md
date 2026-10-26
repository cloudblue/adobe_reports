# Report Assets

This report creates an Excel file with details about assets with scope parameters

# Available parameters

Assets can be parametrized by:

* Product
* Asset creation date range
* Three years commitment
* Asset Status

# Columns

* Asset ID, Asset Status, External ID, Product ID, Provider ID, Provider Name, Marketplace ID, Marketplace Name
* Contract ID, Contract Name, Reseller ID, Reseller External ID, Reseller Name, Created At
* Customer ID, Customer External ID, Customer Name
* External Reference ID, Seamless Move, Auto Renewal Status, Discount Group, Discount Level Consumables, Action,
  Renewal Date, Purchase Type
* Adobe Customer ID, Adobe VIP Number, Adobe User Email, Adobe Subscription Details
* 3YC Y/N, Commitment, 3YC Committed Licenses, 3YC Committed Consumables, Commitment Start Date, Commitment End Date
* 3YC Recommitment Y/N, 3YC Recommitted Licenses, 3YC Recommitted Consumables, Recommitment, Recommitment Start Date,
  Recommitment End Date
* Seats (sum of the asset items quantity)

Financial columns (Currency, Cost, Reseller Cost, MSRP and USD values) were removed: the price list
source they were calculated from is obsolete.

Command to create report: ccli report execute assets -d .