# -*- coding: utf-8 -*-
#
# Copyright (c) 2022, Carlos Anuarbe
# All rights reserved.
#

import requests
from reports import utils
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
        marketplace_params = utils.get_marketplace_params(client, asset)
        if not marketplace_params:
            marketplace_params = dict.fromkeys(entrypoint.marketplace_headers)
        list_to_assert.append(utils.process_line(asset, entrypoint.asset_headers,
                                                 entrypoint.asset_params_headers, marketplace_params))
    assert len(list_to_assert) == assets.count()


def test_listing_not_exist(sync_client_factory, response_factory, assets):
    client = sync_client_factory([
        response_factory(
            query=LISTING_QUERY,
            value=[],
        )
    ])
    assert not utils.get_marketplace_params(client, assets[0])


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
    assert not utils.get_marketplace_params(client, assets[0])


def test_api_calls(sync_client_factory, response_factory, assets, listing, pricelist_version):
    responses = [
        response_factory(
            query='and(ge(events.created.at,2022-12-1T00:00:00),le(events.created.at,2022-12-15T00:00:00),'
                  'in(product.id,(PRD-207-752-513)))',
            value=True,
        ),
        response_factory(
            query=LISTING_QUERY,
            value=True,
        ),
        response_factory(
            query=PRICELIST_VERSION_QUERY,
            value=True,
        ),
        response_factory(
            query=PRICELIST_POINTS_QUERY,
            value=True,
        ),
    ]
    client = sync_client_factory(responses)
    input_data['status'] = ''
    assert api_calls.request_assets(client, input_data)
    assert api_calls.request_listing(client, assets[0]['marketplace']['id'], assets[0]['product']['id'])
    assert api_calls.request_price_list(client, listing[0]['pricelist']['id'])
    assert api_calls.request_price_list_version_points(client, pricelist_version[0]['id'])


def test_same_currency(pricelist_version):
    assert utils.get_currency_and_change(pricelist_version[1])['change'] == 1.0


def test_get_financials_and_seats(assets):
    items = assets[0]['items']
    price_list_financials = {}
    utils._get_financials_and_seats(items, price_list_financials)


def test_forexapi_server_error(requests_mock, pricelist_version):
    requests_mock.get(utils.FOREXAPI_URL, status_code=500)
    exchange = utils.get_currency_and_change(pricelist_version[0])
    assert exchange['change'] == 0.0


def test_forexapi_exception(requests_mock, pricelist_version):
    requests_mock.get(utils.FOREXAPI_URL, exc=requests.exceptions.ConnectTimeout)
    exchange = utils.get_currency_and_change(pricelist_version[0])
    print(exchange)
    assert exchange['change'] == 0.0
