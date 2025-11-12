# -*- coding: utf-8 -*-
#
# Copyright (c) 2022, Carlos Anuarbe
# All rights reserved.
#

from reports.requests import entrypoint

# queries
LISTING_QUERY = 'and(eq(marketplace.id,MP-65669),eq(product.id,PRD-207-752-513),eq(status,listed))'
PRICELIST_VERSION_QUERY = 'and(eq(pricelist.id,PL-667-945-709),eq(status,active))'
PRICELIST_POINTS_QUERY = 'eq(status,filled)'
REQUEST_QUERY = 'and(eq(status,approved),ge(created,2021-01-01T00:00:00),le(created,2021-12-01T00:00:00),' \
                'in(asset.connection.type,(production)))'
ASSET_QUERY = 'eq(id,AS-1895-0864-1238)'

# input_data as passed to generate
parameters = {
    "date": {
        "after": "2021-01-01T00:00:00",
        "before": "2021-12-01T00:00:00",
    },
    "product": {
        "all": True,
        "choices": [],
    },
    "marketplace": {
        "all": True,
        "choices": [],
    },
    "rr_type": {
        "all": True,
        "choices": [],
    },
    "connexion_type": {
        "all": False,
        "choices": ["production"],
    },
}


def test_requests_generate(sync_client_factory, response_factory, progress,
                           listing, pricelist_version, pricelist_points, asset, ff_requests):
    responses = [
        response_factory(
            query=REQUEST_QUERY,
            count=1
        ),
        response_factory(
            query=REQUEST_QUERY,
            value=ff_requests,
        ),
        response_factory(
            query=LISTING_QUERY,
            value=listing,
        ),
        response_factory(
            query=PRICELIST_VERSION_QUERY,
            value=pricelist_version,
        ),
        response_factory(
            query=PRICELIST_POINTS_QUERY,
            value=pricelist_points,
        ),
        response_factory(
            query=ASSET_QUERY,
            value=asset,
        ),
    ]
    client = sync_client_factory(responses)

    result = list(entrypoint.generate(client, parameters, progress))
    
    # Verify number of rows (items with non-empty delta)
    assert len(result) == 6  # number of items on ff_request.json
    
    # Verify each row has 53 columns (46 original + 4 flex discount + 2 discount group + 1 UoM)
    for row in result:
        assert len(row) == 53
    
    # Verify basic data in first row
    first_row = result[0]
    assert first_row[0] == 'PR-1895-0864-1238-001'  # Request ID
    assert first_row[1] == 'UR-841-574-187'  # Assignee ID
    assert first_row[2] == 'Marc Serrat'  # Assignee Name
    assert first_row[3] == 'AS-1895-0864-1238'  # Connect Subscription ID
    assert first_row[11] == '01A12'  # Discount Group Licenses (position 12)
    assert first_row[12] == 'T1A12'  # Discount Group Consumables (position 13)
    assert first_row[14] == 'MPN-R-001'  # Part Number (position 15)
    assert first_row[15] == 'Units'  # Unit of Measure (position 16)
    assert first_row[16] == 'Monthly'  # Product Period (position 17, shifted by +1)
    
    # Verify discount data for specific items
    # Item with MPN-R-002 should have one discount
    item_002 = [row for row in result if row[14] == 'MPN-R-002'][0]
    assert item_002[19] == 'MPN-R-002'  # Discounted MPN (shifted from 18 to 19)
    assert item_002[20] == 'P9201150234'  # Discounted Adobe Order Id (shifted from 19 to 20)
    assert item_002[21] == '12345678-1234-1234-1234-123456789abc'  # Adobe Discount Id (shifted from 20 to 21)
    assert item_002[22] == 'ADOBE_PROMOTION_Q1'  # Adobe Discount Code (shifted from 21 to 22)
    
    # Item with MPN-R-005 should have two discounts (concatenated)
    item_005 = [row for row in result if row[14] == 'MPN-R-005'][0]
    assert item_005[19] == 'MPN-R-005,MPN-R-005'  # Discounted MPN (shifted from 18 to 19)
    assert item_005[20] == 'P9201150234,P9201150234'  # Discounted Adobe Order Id (shifted from 19 to 20)
    assert item_005[21] == '87654321-4321-4321-4321-cba987654321,11111111-2222-3333-4444-555555555555'
    assert item_005[22] == 'ADOBE_DISCOUNT_SPECIAL,ADOBE_EXTRA_SAVINGS'
    
    # Item with MPN-R-001 should have no discount (show '-')
    item_001 = [row for row in result if row[14] == 'MPN-R-001'][0]
    assert item_001[19] == '-'  # Discounted MPN (shifted from 18 to 19)
    assert item_001[20] == '-'  # Discounted Adobe Order Id (shifted from 19 to 20)
    assert item_001[21] == '-'  # Adobe Discount Id (shifted from 20 to 21)
    assert item_001[22] == '-'  # Adobe Discount Code (shifted from 21 to 22)
    
    # Verify new columns (commitment, renewal date, etc.)
    assert item_001[34] == '2021-11-23'  # Adobe Renewal Date (shifted from 33 to 34)
    assert item_001[36] == 365  # Prorata (days) (shifted from 35 to 36)
    assert item_001[46] == 'COMMITTED'  # commitment (shifted from 45 to 46)
    assert item_001[47] == '2023-11-23'  # commitment start date (shifted from 46 to 47)
    assert item_001[48] == '2026-11-23'  # commitment end date (shifted from 47 to 48)
    assert item_001[49] == '-'  # recommitment (shifted from 48 to 49)
    assert item_001[50] == '-'  # recommitment start date (shifted from 49 to 50)
    assert item_001[51] == '-'  # recommitment end date (shifted from 50 to 51)
    assert item_001[52] == 'EXT-REF-12345'  # external reference id (shifted from 51 to 52)
