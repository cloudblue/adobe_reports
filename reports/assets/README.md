# Report assets_report

This reports retrieves the headers present in entrypoint.py and shows them in a xlsx file.
In case that some header is not present at connect request it will show as blank,
if the currency api (forexapi) fails the USD columns will be 0.

Actually this reports is built for Adobe, but it can work on other products.

Command to create report: ccli report execute assets -d .