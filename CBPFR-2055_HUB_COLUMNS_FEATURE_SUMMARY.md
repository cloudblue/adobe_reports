# CBPFR-2055: Hub ID and Hub Name on Adobe Approved Requests Report

**Feature branch:** `feature/CBPFR-2055`  
**Report:** Adobe Approved Requests  
**Document purpose:** Summary of requirements and implementation for Jira documentation and release notes.

---

## 1. Overview

This feature adds Connect HUB identification to the **Adobe Approved Requests** report by exposing **Hub Id** and **Hub Name** per approved request, and excludes a defined set of production hubs from the report output. A related fix prevents report failure when a product/marketplace has no pricelist (e.g. not listed).

---

## 2. Business Requirements

### 2.1 New columns

| Requirement | Description |
|-------------|-------------|
| **Hub Id** | Connect Hub ID for the request’s asset connection. Source: `asset.connection.hub.id`. |
| **Hub Name** | Connect Hub name for the request’s asset connection. Source: `asset.connection.hub.name`. |
| **Placement** | Both columns appear **immediately after** the column **"End Customer External ID"** (before Provider ID and Provider Name). |
| **Empty/missing hub** | If hub information is missing or empty: **Hub Id** shows the same placeholder used elsewhere in the report (`-`). **Hub Name** shows the same value as the **Provider Name** column for consistency. |
| **Hub name is None** | If hub name is the value `None` or the string `"None"`, **Hub Name** shows the same value as the **Provider Name** column for consistency. |

### 2.2 Production hub exclusion

| Requirement | Description |
|-------------|-------------|
| **Scope** | Apply only in **Production** environment (`asset.connection.type == 'production'`). No exclusion for **Test** or **Preview**. |
| **Excluded Hub IDs** | Approved requests whose `asset.connection.hub.id` is one of the following must **not** appear in the report: `HB-4043-4841`, `HB-1042-0462`, `HB-9379-5319`, `HB-8855-1470`. |
| **Behavior** | Excluded requests are skipped entirely (no rows yielded for that request). |

### 2.3 Data source (reference)

Hub data is taken from the Purchase Request (PR) payload available at report execution, under:

- `request['asset']['connection']['hub']['id']`
- `request['asset']['connection']['hub']['name']`

Example structure:

```json
"connection": {
  "hub": {
    "id": "HB-3050-0939",
    "name": "commerce-dev.platform.cloudblue.io"
  },
  "provider": { "id": "...", "name": "..." }
}
```

---

## 3. Technical Implementation Summary

### 3.1 Report column order (excerpt)

Columns are emitted in this order (excerpt around the new fields):

- … **End Customer External ID** → **Hub Id** → **Hub Name** → **Provider ID** → **Provider Name** → …

Total number of columns in the report increased by **2** (e.g. from 53 to 55).

### 3.2 Logic

- **Hub Id:** From `connection.hub.id`; if missing or empty, use placeholder `-`.
- **Hub Name:** From `connection.hub.name`; if missing, empty, or is `None`/the string `"None"`, use `connection.provider.name` (same as Provider Name column).
- **Exclusion:** For each request, if `connection.type == 'production'` and `hub.id` is in the excluded set, the request is skipped (no rows generated).
- **Template:** The Excel template must include headers **"Hub Id"** and **"Hub Name"** in the same position (after **End Customer External ID**) so that exported data aligns with the columns.

### 3.3 Defensive fix (pricelist)

- **Issue:** The report could fail with `KeyError: 'pricelist'` when the listing for a product/marketplace has no `pricelist` (e.g. not listed).
- **Change:** In `get_financials_from_product_per_marketplace`, all access to the listing’s pricelist uses safe access (e.g. `(listing or {}).get('pricelist')`, and `pricelist.get('id')` when applicable) so that missing or incomplete listing/pricelist does not raise an error.
- **Result:** When there is no pricelist, financial columns (Cost, Reseller Cost, MSRP) are empty/default for those rows; the report completes successfully.

---

## 4. Files Changed

| File | Change |
|------|--------|
| **`reports/requests/entrypoint.py`** | Added `EXCLUDED_PRODUCTION_HUB_IDS`; per-request check to skip production requests with excluded hub ID; added **Hub Id** and **Hub Name** to the yielded row tuple after End Customer External ID. |
| **`reports/utils.py`** | Added `get_hub_id(connection)` and `get_hub_name(connection)`; hardened `get_financials_from_product_per_marketplace` to use `.get('pricelist')` and avoid `KeyError` when pricelist is missing. |
| **`reports/requests/templates/xlsx/template.xlsx`** | Manual update: add two columns **Hub Id** and **Hub Name** after **End Customer External ID** (user-maintained). |
| **`tests/test_request_report.py`** | Updated expected row length (e.g. 55 columns); assertions for Hub Id and Hub Name at correct indices; test for production hub exclusion (`test_requests_generate_excludes_production_hubs`); adjusted indices for columns after the new ones. |
| **`tests/test_utils.py`** | Added `test_get_hub_id` and `test_get_hub_name` for the new helpers. |

---

## 5. Acceptance Criteria

- [ ] **Hub Id** and **Hub Name** columns appear in the Adobe Approved Requests report immediately after **End Customer External ID**.
- [ ] **Hub Id** shows the Connect Hub ID when present; otherwise shows `-`.
- [ ] **Hub Name** shows the Connect Hub name when present; otherwise (missing, empty, or `None`/`"None"`) shows the same value as **Provider Name**.
- [ ] In **Production**, requests with hub ID in `{ HB-4043-4841, HB-1042-0462, HB-9379-5319, HB-8855-1470 }` do **not** appear in the report.
- [ ] In **Test** and **Preview**, no hub-based exclusion is applied; all approved requests (per existing filters) appear as before.
- [ ] Report runs to completion when some product/marketplace combinations have no pricelist (no `KeyError: 'pricelist'`).
- [ ] Existing unit and report tests pass (e.g. `tests/test_request_report.py`, `tests/test_utils.py`).

---

## 6. Jira-Friendly Summary (short)

**Title:** Add Hub ID and Hub Name to Adobe Approved Requests report and exclude specific production hubs  

**Description (short):**  
- Add two columns to the Adobe Approved Requests report: **Hub Id** and **Hub Name**, placed after **End Customer External ID**, sourced from `asset.connection.hub`.  
- When hub is missing/empty: Hub Id = `-`, Hub Name = Provider Name.  
- In Production only, exclude approved requests for hubs: HB-4043-4841, HB-1042-0462, HB-9379-5319, HB-8855-1470.  
- Fix report crash when listing has no pricelist (safe access in `get_financials_from_product_per_marketplace`).  

**Branch:** `feature/CBPFR-2055`

---

## 7. Version / Release Note Snippet

**Adobe Reports – Hub columns and production hub exclusion (CBPFR-2055)**

- **Adobe Approved Requests:** New columns **Hub Id** and **Hub Name** (after End Customer External ID). Hub Name falls back to Provider Name when hub data is missing.
- **Production:** Requests from hubs HB-4043-4841, HB-1042-0462, HB-9379-5319, and HB-8855-1470 are excluded from the report; Test and Preview unchanged.
- **Stability:** Report no longer fails with `KeyError: 'pricelist'` when a product/marketplace has no pricelist.
