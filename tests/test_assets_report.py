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
    "status": 'active',
    "commitment_status": "all assets"
}


def test_assets_generate(sync_client_factory, response_factory, progress,
                           listing, pricelist_version, pricelist_points, assets):
    responses = [
        response_factory(
            query=ASSETS_QUERY,
            count=1
        ),
        response_factory(
            query=ASSETS_QUERY,
            value=assets,
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
    ]

    client = sync_client_factory(responses)

    result = entrypoint.generate(client, input_data, progress)
    assert len(list(result)) == 1  # number of assets on active_assets.json



def test_assets_generate_empty_assets(sync_client_factory, response_factory, progress):
    responses = [
        response_factory(
            query=ASSETS_QUERY,
            count=0
        ),
        response_factory(
            query=ASSETS_QUERY,
            value=[],
        ),
    ]

    client = sync_client_factory(responses)
    result = entrypoint.generate(client, input_data, progress)
    assert len(list(result)) == 1  # Empty label


def test_assets_generate_listing_not_exist(sync_client_factory, response_factory, progress,
                                           assets):
    responses = [
        response_factory(
            query=ASSETS_QUERY,
            count=1
        ),
        response_factory(
            query=ASSETS_QUERY,
            value=assets,
        ),
        response_factory(
            query=LISTING_QUERY,
            value=[],
        ),
    ]

    client = sync_client_factory(responses)
    result = entrypoint.generate(client, input_data, progress)
    assert len(list(result)) == 1  # empty assets at marketplace_headers cells


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



def test_assets_generate_with_3yc(sync_client_factory, response_factory, progress,
                           listing, pricelist_version, pricelist_points, assets):
    responses = [
        response_factory(
            query=ASSETS_QUERY,
            count=1
        ),
        response_factory(
            query=ASSETS_QUERY,
            value=assets,
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
    ]

    input_data_local = {
        "date": {
            "after": "2022-12-1T00:00:00",
            "before": "2022-12-15T00:00:00",
        },
        "product": {
            "all": False,
            "choices": ['PRD-207-752-513'],
        },
        "status": 'active',
        "commitment_status": "3yc"
    }

    client = sync_client_factory(responses)

    result = entrypoint.generate(client, input_data_local, progress)
    assert len(list(result)) == 0  # number of assets on active_assets.json