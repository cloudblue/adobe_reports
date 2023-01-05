# -*- coding: utf-8 -*-
#
# Copyright (c) 2022, Carlos Anuarbe
# All rights reserved.
#

from reports.assets import entrypoint
from reports import api_calls

# queries
ASSETS_QUERY = 'and(ge(events.created.at,2022-12-1T00:00:00),le(events.created.at,2022-12-15T00:00:00),in(product.id,' \
               '(PRD-207-752-513)),eq(status,active))'
LISTING_QUERY = 'and(eq(marketplace.id,MP-65669),eq(product.id,PRD-207-752-513),eq(status,listed))'
PRICELIST_VERSION_QUERY = 'and(eq(pricelist.id,PL-667-945-709),eq(status,active))'
PRICELIST_POINTS_QUERY = 'eq(status,filled)'

# input_data as passed to generate
input_data = {
    "date": {
        "after": "2022-12-1T00:00:00",
        "before": "2022-12-15T00:00:00",
    },
    "product": {
        "all": False,
        "choices": ['PRD-207-752-513'],
    },
    "status": 'active'
}


def test_assets_generate(sync_client_factory, response_factory, progress,
                           listing, pricelist_version, pricelist_points, assets):
    responses = [
        response_factory(
            query=ASSETS_QUERY,
            count=10
        ),
        response_factory(
            query=ASSETS_QUERY,
            value=assets,
            count=10,
        ),
        response_factory(
            query=LISTING_QUERY,
            value=listing,
            count=10,
        ),
        response_factory(
            query=PRICELIST_VERSION_QUERY,
            value=pricelist_version,
            count=10,
        ),
        response_factory(
            query=PRICELIST_POINTS_QUERY,
            value=pricelist_points,
            count=10,
        ),
    ]

    client = sync_client_factory(responses)

    result = entrypoint.generate(client, input_data, progress)
    assert len(list(result)) == 5  # number of items on ff_request.json with quantity>0 and type!='PPU'


def test_assets_report(assets, listing, extra_context_callback, sync_client_factory, response_factory,
                       pricelist_version, pricelist_points):
    responses = [
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
    ]
    client_assets = sync_client_factory([
        response_factory(
            query=ASSETS_QUERY,
            value=assets,
        ),
    ])

    assets = api_calls.request_assets(client_assets, input_data)

    list_to_assert = []
    for asset in assets:
        # client need to be built for each asset
        client = sync_client_factory(responses)
        marketplace_params = entrypoint._get_marketplace_params(client, asset)
        if not marketplace_params:
            marketplace_params = dict.fromkeys(entrypoint.marketplace_headers)
        list_to_assert.append(entrypoint._process_line(asset, marketplace_params))
    assert len(list_to_assert) == assets.count()


def test_listing_not_exist(sync_client_factory, response_factory, assets):
    client = sync_client_factory([
        response_factory(
            query=LISTING_QUERY,
            value=[],
        )
    ])
    assert not entrypoint._get_marketplace_params(client, assets[0])


def test_price_list_not_exist(sync_client_factory, response_factory, assets, listing):
    client = sync_client_factory([
        response_factory(
            query=LISTING_QUERY,
            value=listing,
        ),
        response_factory(
            query=PRICELIST_VERSION_QUERY,
            value=[],
        ),
        response_factory(
            query=PRICELIST_POINTS_QUERY,
            value=[],
        ),
    ])
    assert not entrypoint._get_marketplace_params(client, assets[0])