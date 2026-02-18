# -*- coding: utf-8 -*-
#
# Copyright (c) 2022, Carlos Anuarbe
# All rights reserved.
#
import copy
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

    result = list(entrypoint.generate(client, parameters, progress))
    assert len(result) == 6  # number of items on ff_request.json

    # Verify Hub ID and Hub Name are in the result (columns 27 and 28, index starting at 0)
    # The columns are added before Provider ID.
    # Provider ID was at index 27 before, now it is at index 29.
    # Hub ID at index 27, Hub Name at index 28.
    assert result[0][27] == 'HB-0309-9389'
    assert result[0][28] == 'IMC DEMOS'


def test_requests_generate_skip_excluded_hubs(sync_client_factory, response_factory, progress, asset, ff_requests):
    # Mock a request with an excluded Hub ID (e.g., HB-4043-4841)
    excluded_request = copy.deepcopy(ff_requests[0])
    excluded_request['asset']['connection']['hub']['id'] = 'HB-4043-4841'
    excluded_request['asset']['connection']['type'] = 'production'

    responses = [
        response_factory(
            query=REQUEST_QUERY,
            count=1
        ),
        response_factory(
            query=REQUEST_QUERY,
            value=[excluded_request],
        ),
    ]
    client = sync_client_factory(responses)

    result = list(entrypoint.generate(client, parameters, progress))
    # It should skip all items in this request, so result should be empty
    assert len(result) == 0


def test_get_param_value():
    value = reports.utils.get_param_value([], "test")
    assert value == '-'
