# -*- coding: utf-8 -*-
#
# Copyright (c) 2022, Carlos Anuarbe
# All rights reserved.
#

from reports import utils
from reports.assets import entrypoint
from reports import api_calls

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
            query='and(eq(marketplace.id,MP-65669),eq(product.id,PRD-207-752-513),eq(status,listed))',
            value=[listing],
        ),
        response_factory(
            query='and(eq(pricelist.id,PL-667-945-709),eq(status,active))',
            value=[pricelist_version],
        ),
        response_factory(
            query='eq(status,filled)',
            value=[pricelist_points],
        ),
    ]
    client_assets = sync_client_factory([
        response_factory(
            query='and(ge(events.created.at,2022-12-1T00:00:00),le(events.created.at,2022-12-15T00:00:00),'
                  'in(product.id,(PRD-207-752-513)),eq(status,active))',
            value=[assets],
        ),
    ])

    assets = api_calls.request_assets(client_assets, input_data)[0]

    list_to_assert = []
    for asset in assets:
        # client need to be rebuilded for each asset
        client = sync_client_factory(responses)
        marketplace_params = utils.get_marketplace_params(client, asset, testing=True)
        if not marketplace_params:
            marketplace_params = dict.fromkeys(entrypoint.marketplace_headers)
        list_to_assert.append(utils.process_line(asset, entrypoint.asset_headers,
                                                 entrypoint.asset_params_headers, marketplace_params))
    assert len(list_to_assert) == len(assets)


def test_api_calls(sync_client_factory, response_factory, assets, listing, pricelist_version):
    responses = [
        response_factory(
            query='and(ge(events.created.at,2022-12-1T00:00:00),le(events.created.at,2022-12-15T00:00:00),'
                  'in(product.id,(PRD-207-752-513)),eq(status,active))',
            value=True,
        ),
        response_factory(
            query='and(eq(marketplace.id,MP-65669),eq(product.id,PRD-207-752-513),eq(status,listed))',
            value=True,
        ),
        response_factory(
            query='and(eq(pricelist.id,PL-667-945-709),eq(status,active))',
            value=True,
        ),
        response_factory(
            query='eq(status,filled)',
            value=True,
        ),
    ]
    client = sync_client_factory(responses)
    assert api_calls.request_assets(client, input_data)
    assert api_calls.request_listing(client, assets[0]['marketplace']['id'], assets[0]['product']['id'])
    assert api_calls.request_price_list(client, listing['pricelist']['id'])
    assert api_calls.request_price_list_version_points(client, pricelist_version['id'], testing=True)
