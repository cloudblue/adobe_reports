# Report Assets

This report creates an Excel file with details about assets with scope parameters

# Available parameters

Assets can be parametrized by:

* Product
* Request creation date range
* Asset Status

# Columns

* Asset ID
* Asset Status
* External ID, Product ID, Provider ID, Provider Name, Marketplace, Marketplace Name, Contract ID, Contract Name
* Reseller ID, Reseller External ID, Reseller Name, Created At, Customer ID, Customer External ID, Customer Name
* Seamless Move, Discount Group, Action, Renewal Date, Purchase Type
* Adobe Customer ID, Adobe Vip Number, Adobe User Email, 
* Currency, Cost, Reseller Cost, MSRP, Seats, USD Cost, USD Reseller Cost, USD MSRP

Command to create report: ccli report execute assets -d .