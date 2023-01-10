# -*- coding: utf-8 -*-
#
# Copyright (c) 2022, Carlos Anuarbe
# All rights reserved.
#

import requests
from reports import utils
from reports import api_calls

# queries
LISTING_QUERY = 'and(eq(marketplace.id,MP-65669),eq(product.id,PRD-207-752-513),eq(status,listed))'
PRICELIST_VERSION_QUERY = 'and(eq(pricelist.id,PL-667-945-709),eq(status,active))'
PRICELIST_POINTS_QUERY = 'eq(status,filled)'
APPROVED_REQUESTS = 'and(eq(status,approved),ge(created,2022-12-1T00:00:00),le(created,2022-12-15T00:00:00),' \
                    'in(asset.connection.type,(test)),in(asset.product.id,(PRD-207-752-513)),in(type,()),' \
                    'in(marketplace.id,()))'

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
    "status": 'all',
    "mkp": {
        "all": False,
        "choices": [],
    },
    "rr_type": {
        "all": False,
        "choices": [],
    },
    "connexion_type": {
        "all": False,
        "choices": ["test"],
    },
}


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
        response_factory(
            query=APPROVED_REQUESTS,
            value=True,
        ),
    ]
    client = sync_client_factory(responses)
    assert api_calls.request_assets(client, input_data)
    assert api_calls.request_listing(client, assets[0]['marketplace']['id'], assets[0]['product']['id'])
    assert api_calls.request_price_list(client, listing[0]['pricelist']['id'])
    assert api_calls.request_price_list_version_points(client, pricelist_version[0]['id'])
    assert api_calls.request_approved_requests(client, input_data)


def test_forexapi_server_error(requests_mock, pricelist_version):
    requests_mock.get(utils.FOREXAPI_URL, status_code=500)
    exchange = utils.get_currency_and_change(pricelist_version[0])
    assert exchange['change'] == 0.0


def test_forexapi_exception(requests_mock, pricelist_version):
    requests_mock.get(utils.FOREXAPI_URL, exc=requests.exceptions.ConnectTimeout)
    exchange = utils.get_currency_and_change(pricelist_version[0])
    assert exchange['change'] == 0.0
