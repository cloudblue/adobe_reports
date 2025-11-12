# Adobe Approved Requests Report

## Overview

This report creates a comprehensive Excel file with detailed information about all approved Adobe subscription requests processed through CloudBlue Connect. The report includes 53 columns covering request details, subscription information, pricing data, flex discounts, commitment terms, and more.

**Report Type**: Request-based  
**Output Format**: Excel (XLSX)  
**Data Source**: CloudBlue Connect API  
**Total Columns**: 53

---

## Available Parameters

The report can be filtered using the following parameters:

### Date Range
- **Request Creation Date Range** - Filter requests by creation date (from/to)

### Filters
- **Product** - Filter by specific Adobe product(s)
- **Marketplace** - Filter by marketplace(s)
- **Environment** - Filter by connection type (production, test, preview)
- **Request Type** - Filter by request type:
  - Purchase
  - Change
  - Suspend
  - Resume
  - Cancel
  - Adjustment
  - Renewal

---

## Report Columns (53 Total)

### Request & Subscription Identification (Columns 1-5)
1. **Request ID** - CloudBlue Connect request identifier (e.g., PR-1895-0864-1238-001)
2. **Assignee ID** - ID of the user assigned to the request (e.g., UR-841-574-187)
3. **Assignee Name** - Name of the assigned user
4. **Connect Subscription ID** - CloudBlue subscription ID (e.g., AS-1895-0864-1238)
5. **End Customer Subscription ID** - External subscription identifier

### Adobe Order Details (Columns 6-10)
6. **Action** - Request action (Purchase, Change, Cancel, etc.)
7. **Adobe Order #** - Adobe order number from VIP/ETLA portal
8. **Adobe Transfer ID #** - Adobe transfer identifier (if applicable)
9. **VIP #** - Adobe VIP (Value Incentive Plan) number
10. **Adobe Cloud Program ID** - Adobe cloud program or customer identifier

### Pricing & Discount Information (Columns 11-13)
11. **Pricing SKU Level (Volume Discount level)** - Formatted discount level (e.g., "Level 1", "Level 2", "TLP Level 1")
12. **Discount Group Licenses** - Raw discount group code for licenses (e.g., "01A12", "02A", "010")
13. **Discount Group Consumables** - Raw discount group code for consumables (e.g., "T1A12", "T5A12", "TBA12")

### Product Information (Columns 14-19)
14. **Product Description** - Full product name/description
15. **Part Number** - Adobe SKU/MPN (e.g., 65322648CA)
16. **Unit of Measure** - Item type/licensing model (User, Transactions, Per Server, Units, etc.)
17. **Product Period** - Billing period (Monthly, Yearly, etc.)
18. **Cumulative Seat** - Total quantity/seat count
19. **Order Delta** - Quantity change (+/- seats)

### Adobe Flex Discounts (Columns 20-23)
20. **Discounted MPN** - MPN(s) receiving flex discounts (comma-separated if multiple)
21. **Discounted Adobe Order Id** - Adobe order ID(s) for discounted items
22. **Adobe Discount Id** - Adobe discount identifier(s)
23. **Adobe Discount Code** - Adobe discount code(s) applied

### Partner & Customer Information (Columns 24-27)
24. **Reseller ID** - Reseller/distributor ID
25. **Reseller Name** - Reseller/distributor name
26. **End Customer Name** - End customer company name
27. **End Customer External ID** - Customer external identifier

### Provider & Marketplace (Columns 28-30)
28. **Provider ID** - Provider identifier
29. **Provider Name** - Provider name
30. **Marketplace** - Marketplace name

### Product & Status (Columns 31-33)
31. **Product ID** - CloudBlue product identifier
32. **Product Name** - Product name in CloudBlue
33. **Subscription Status** - Current subscription status

### Date Information (Columns 34-38)
34. **Anniversary Date** - Subscription anniversary/renewal date
35. **Adobe Renewal Date** - Adobe renewal date from parameters
36. **Effective Date** - Request effective date
37. **Prorata (days)** - Days between effective date and renewal date
38. **Creation Date** - Request creation timestamp

### Request Details (Columns 39-40)
39. **Connect Order Type** - Request type (Purchase, Change, etc.)
40. **Adobe User Email** - Adobe user email address

### Financial Information (Columns 41-44)
41. **Currency** - Currency code (USD, EUR, etc.)
42. **Cost** - Provider cost
43. **Reseller Cost** - Reseller/distributor cost
44. **MSRP** - Manufacturer's suggested retail price

### Connection & Export (Columns 45-46)
45. **Connection Type** - Environment type (Production, Test, Preview)
46. **Exported At** - Report generation timestamp

### Commitment Information (Columns 47-52)
47. **commitment** - Commitment status (COMMITTED, NOT_COMMITTED, etc.)
48. **commitment start date** - Start date of commitment period
49. **commitment end date** - End date of commitment period
50. **recommitment** - Recommitment status
51. **recommitment start date** - Start date of recommitment period
52. **recommitment end date** - End date of recommitment period

### External References (Column 53)
53. **external reference id** - External reference identifier

---

## Key Features

### 1. Adobe Flex Discounts Support
The report includes comprehensive support for Adobe Flex Discounts:
- Extracts discount data from the `cb_flex_discounts_applied` parameter
- Matches discounts to specific line items by MPN and Adobe Order ID
- Handles multiple discounts per item (concatenated with commas)
- Shows "-" when no discounts are applied

### 2. Discount Group Information
Provides both formatted and raw discount group data:
- **Formatted** (Column 11): Human-readable levels (e.g., "Level 1", "TLP Level 2")
- **Raw Licenses** (Column 12): Unformatted code for licenses (e.g., "01A12")
- **Raw Consumables** (Column 13): Unformatted code for consumables (e.g., "T1A12")

### 3. Unit of Measure
Indicates how each product is licensed or billed:
- **User** - Per-user licenses (Creative Cloud, Acrobat, etc.)
- **Transactions** - Transaction-based (Adobe Sign)
- **Per Server** - Server-based licensing
- **Units** - Generic unit measurement
- **Credits** - Credit-based consumption (Adobe Stock)

### 4. Prorata Calculation
Automatically calculates the number of days between the effective date and renewal date:
- Useful for mid-cycle purchases and changes
- Helps with proration calculations
- Returns "-" if dates are missing

### 5. Commitment Tracking
Tracks Adobe commitment terms:
- Initial commitment status and dates
- Recommitment status and dates
- Supports multi-year agreements

### 6. Assignee Information
Tracks request ownership:
- Assignee ID and name
- Helps with workflow management and accountability

---

## Use Cases

### Financial Analysis
- Track costs, reseller pricing, and MSRP across products
- Analyze discount effectiveness (flex discounts + volume discounts)
- Calculate proration for mid-cycle changes
- Monitor pricing levels and discount groups

### License Management
- Track seat counts and delta changes
- Monitor license types (User, Transaction, etc.)
- Identify growth trends by product
- Manage license optimization

### Compliance & Auditing
- Verify Adobe order numbers and VIP information
- Track commitment periods and terms
- Audit discount applications
- Review request assignments and approval chains

### Partner Management
- Analyze reseller/distributor activity
- Track customer portfolio by partner
- Monitor marketplace distribution
- Review partner pricing and margins

### Product Mix Analysis
- Identify most popular products and SKUs
- Track product periods (monthly vs yearly)
- Analyze unit of measure distribution
- Monitor product adoption trends

---

## Execution Commands

### Using Connect CLI

```bash
# Execute report with default parameters
ccli report execute requests -d .

# Execute with specific date range
ccli report execute requests \
  --param date_from=2024-01-01 \
  --param date_to=2024-12-31 \
  -d .

# Execute for specific product
ccli report execute requests \
  --param product=PRD-123-456-789 \
  -d .

# Execute for specific marketplace
ccli report execute requests \
  --param marketplace=MP-12345 \
  -d .

# Execute for specific request types
ccli report execute requests \
  --param rr_type=purchase,change \
  -d .
```

### Using Docker Environment

```bash
# Navigate to the project directory
cd /home/connect/adobe_reports

# Execute the report
ccli report execute requests -d .
```

---

## Data Quality Notes

### Expected Values
- All columns should populate for complete requests
- "-" indicates missing or not applicable data
- Flex discount columns show "-" when no discounts are applied
- Commitment fields show "-" when no commitment exists

### Common Scenarios
- **New Purchases**: Order Delta shows positive numbers
- **Cancellations**: Order Delta shows negative numbers
- **Changes**: May show both positive and negative deltas
- **Flex Discounts**: Only populated when discounts are applied to specific items
- **Commitments**: Only populated for customers with commitment agreements

---

## Technical Details

### Data Sources
- **Request Data**: CloudBlue Connect Requests API
- **Asset Data**: CloudBlue Connect Assets API
- **Financial Data**: CloudBlue Connect Products/Pricelist API
- **Parameters**: Asset fulfillment and configuration parameters

### Special Processing
1. **Flex Discounts**: Parsed from `cb_flex_discounts_applied` object parameter
2. **Prorata**: Calculated from effective date and renewal date
3. **Pricing Level**: Transformed from raw discount group code
4. **Unit of Measure**: Extracted from item type field
5. **Dates**: Normalized and formatted consistently

### Performance Considerations
- Large date ranges may take longer to process
- Report includes API calls per request and asset
- Filtering by product/marketplace improves performance
- Consider running reports for specific periods (monthly/quarterly)

---

## Related Documentation

- **IMPLEMENTATION_COMPLETE.md** - Complete implementation history and technical details
- **FLEX_DISCOUNTS_IMPLEMENTATION.md** - Detailed flex discounts implementation
- **PRORATA_FIX_FINAL.md** - Prorata calculation implementation and fixes
- **DISCOUNT_GROUP_COLUMN_ADDED.md** - Discount group licenses column details
- **DISCOUNT_GROUP_CONSUMABLES_COLUMN.md** - Discount group consumables column details
- **UNIT_OF_MEASURE_COLUMN.md** - Unit of measure column implementation
- **PRICING_SKU_LEVEL_EXPLANATION.md** - Pricing level calculation logic

---

## Version History

**Current Version**: 1.4  
**Last Updated**: November 2025  
**Total Columns**: 53  
**Status**: Production-ready

**Recent Changes**:
- ✅ Added Adobe Flex Discounts support (4 columns)
- ✅ Restored missing columns from v1.3.1 (11 columns)
- ✅ Added Discount Group Licenses column (raw value)
- ✅ Added Discount Group Consumables column (raw value)
- ✅ Added Unit of Measure column (item type)
- ✅ Fixed Prorata calculation for various date formats
- ✅ Updated test coverage for all new features

---

## Support & Troubleshooting

### Common Issues

**Missing Flex Discount Data**
- Verify `cb_flex_discounts_applied` parameter exists on asset
- Check that MPN and Adobe Order ID match between discount and line item
- Confirm discount data structure is correct (JSON with 'discounts' array)

**Prorata Shows "-"**
- Verify effective date and renewal date are populated
- Check date formats are valid ISO 8601 or YYYY-MM-DD
- Ensure dates are not in the future

**Discount Group Shows "-"**
- Verify `discount_group` or `discount_group_consumables` parameter exists
- Check parameter is at the asset level (fulfillment parameters)
- Confirm parameter value is not empty

**Unit of Measure Shows "-"**
- Verify item has a `type` field in the request data
- Check item structure is complete
- May indicate incomplete data sync from Adobe

### Getting Help
For technical support or questions about this report:
1. Check the related documentation files
2. Review test cases in `tests/test_request_report.py`
3. Examine sample data in `tests/ff_requests.json`
4. Contact CloudBlue Connect support

---

**Report ID**: `requests`  
**Report Name**: Adobe Approved Requests  
**Maintained by**: CloudBlue Adobe Reports Team