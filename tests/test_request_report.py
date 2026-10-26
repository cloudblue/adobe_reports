# -*- coding: utf-8 -*-
#
# Copyright (c) 2022, Carlos Anuarbe
# All rights reserved.
#
import copy

import openpyxl

import reports.utils
from reports import utils
from reports.requests import entrypoint

# queries
REQUEST_QUERY = 'and(eq(status,approved),ge(created,2021-01-01T00:00:00),le(created,2021-12-01T00:00:00),' \
                'in(asset.connection.type,(production)))'
ASSET_QUERY = 'eq(id,AS-1895-0864-1238)'
TEMPLATE = 'reports/requests/templates/xlsx/template.xlsx'

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


def test_requests_generate(sync_client_factory, response_factory, progress, asset, ff_requests):
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

    headers = [cell.value for cell in openpyxl.load_workbook(TEMPLATE).active[1] if cell.value]
    row = dict(zip(headers, result[0]))
    assert len(result[0]) == len(headers)
    assert not {'Cost', 'Reseller Cost', 'MSRP'} & set(headers)
    assert row['Connection Type'] == utils.get_basic_value(ff_requests[0]['asset']['connection'], 'type')


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
