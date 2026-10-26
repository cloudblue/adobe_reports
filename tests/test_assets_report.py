# -*- coding: utf-8 -*-
#
# Copyright (c) 2022, Carlos Anuarbe
# All rights reserved.
#

import openpyxl

from reports.assets import entrypoint

# queries
ASSETS_QUERY = 'and(ge(events.created.at,2022-12-1T00:00:00),le(events.created.at,2022-12-15T00:00:00),in(product.id,' \
               '(PRD-207-752-513)),eq(status,active))'

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


def test_assets_generate(sync_client_factory, response_factory, progress, assets):
    responses = [
        response_factory(
            query=ASSETS_QUERY,
            count=1
        ),
        response_factory(
            query=ASSETS_QUERY,
            value=assets,
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


def test_assets_generate_with_3yc(sync_client_factory, response_factory, progress, assets):
    responses = [
        response_factory(
            query=ASSETS_QUERY,
            count=1
        ),
        response_factory(
            query=ASSETS_QUERY,
            value=assets,
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


def _template_headers():
    workbook = openpyxl.load_workbook('reports/assets/templates/xlsx/template.xlsx')
    return [cell.value for cell in workbook.active[1] if cell.value]


def test_process_line_matches_template(assets):
    values = entrypoint._process_line(assets[0])
    row = dict(zip(_template_headers(), values))

    assert len(values) == len(_template_headers())
    assert row['Asset Id'] == 'AS-7509-2534-5097'
    assert row['PurchaseType'] == 'team'
    assert row['Seats'] == 273  # 67 + 25 + 96 + 85 items quantity


def test_template_has_no_financial_columns():
    financial_headers = {
        'Currency', 'Cost', 'Reseller Cost', 'MSRP', 'USD Cost', 'USD Reseller Cost', 'USD MSRP',
    }
    assert not financial_headers & set(_template_headers())
