# -*- coding: utf-8 -*-
#
# Copyright (c) 2022, Carlos Anuarbe
# All rights reserved.
#
import reports.utils
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
    "commitment_status": "all assets"
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

    result = entrypoint.generate(client, parameters, progress)
    assert len(list(result)) == 6  # number of items on ff_request.json


def test_get_param_value():
    value = reports.utils.get_param_value([], "test")
    assert value == '-'
