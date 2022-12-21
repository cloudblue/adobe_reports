# -*- coding: utf-8 -*-
#
# Copyright (c) 2022, Carlos Anuarbe
# All rights reserved.
#

from reports import utils
from reports.assets import entrypoint

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


def test_assets_report(assets, listing, extra_context_callback, sync_client_factory, response_factory, pricelist_version, pricelist_points):
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
    list_to_assert = []
    for asset in assets:
        # need to be rebuilded for each asset
        client = sync_client_factory(responses)
        marketplace_params = utils.get_marketplace_params(client, asset, testing=True)
        if not marketplace_params:
            marketplace_params = dict.fromkeys(entrypoint.marketplace_headers)
        list_to_assert.append(utils.process_line(asset, entrypoint.asset_headers,
                                                 entrypoint.asset_params_headers, marketplace_params))
    assert len(list_to_assert) == len(assets)
