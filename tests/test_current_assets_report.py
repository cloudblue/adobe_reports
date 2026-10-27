# -*- coding: utf-8 -*-
#
# Copyright (c) 2026, CloudBlue
# All rights reserved.
#
import copy

import openpyxl
import pytest

from reports.current_assets import entrypoint

QUERY = 'and(in(product.id,(PRD-207-752-513)),in(marketplace.id,(MP-65669)),' \
        'in(status,({status})),in(connection.type,({conn})))'
ASSETS_QUERY = QUERY.format(status='active', conn='preview')
TEMPLATE = 'reports/current_assets/templates/xlsx/template.xlsx'

# Column indexes (starting at 0)
CONNECTION_TYPE = 11
HUB_ID = 7
ITEM_NAME = 31
MPN = 32
QUANTITY = 33
UNIT_OF_MEASURE = 34

parameters = {
    "product": {
        "all": False,
        "choices": ['PRD-207-752-513'],
    },
    "mkp": {
        "all": False,
        "choices": ['MP-65669'],
    },
    "status": {
        "all": False,
        "choices": ['active'],
    },
    "connexion_type": {
        "all": False,
        "choices": ['preview'],
    },
    "commitment_status": "all assets",
}


@pytest.fixture
def run(sync_client_factory, response_factory, progress):
    def _generate(assets, params=None, query=ASSETS_QUERY):
        responses = [
            response_factory(query=query, count=len(assets)),
            response_factory(query=query, value=assets),
        ]
        client = sync_client_factory(responses)
        return list(entrypoint.generate(client, params or parameters, progress))

    return _generate


def _set_param(asset, name, value, param_id=None):
    for param in asset['params']:
        if param['name'] == name:
            param['value'] = value
            return
    asset['params'].append({'id': param_id or name, 'name': name, 'value': value})


def test_current_assets_generate(run, progress, assets):
    result = run(assets)

    assert len(result) == 4  # number of items on active_assets.json
    assert result[1][ITEM_NAME] == 'Acrobat Pro DC for teams (US/CA)'
    assert result[1][MPN] == '65304520CA'
    assert result[1][QUANTITY] == 25.0
    assert result[1][UNIT_OF_MEASURE] == 'Units'
    assert result[0][UNIT_OF_MEASURE] == 'Licenses'
    assert result[0][CONNECTION_TYPE] == 'preview'
    assert result[0][HUB_ID] == 'HB-0000-0000'
    progress.assert_called_with(1, 1)


def test_current_assets_row_matches_template(run, progress, assets):
    result = run(assets)
    headers = [cell.value for cell in openpyxl.load_workbook(TEMPLATE).active[1] if cell.value]

    assert len(result[0]) == len(headers)


def test_current_assets_all_choices_no_filters(run, progress, assets):
    params = {
        "product": {"all": True, "choices": []},
        "mkp": {"all": True, "choices": []},
        "status": {"all": True, "choices": []},
        "connexion_type": {"all": True, "choices": []},
        "commitment_status": "all assets",
    }
    result = run(assets, params, None)

    assert len(result) == 4


def test_current_assets_multiple_statuses_query(run, progress, assets):
    params = copy.deepcopy(parameters)
    params['status']['choices'] = ['active', 'suspended']
    query = QUERY.format(status='active,suspended', conn='preview')
    result = run(assets, params, query)

    assert len(result) == 4


def test_current_assets_skips_zero_quantity_items(run, progress, assets):
    assets = copy.deepcopy(assets)
    assets[0]['items'][0]['quantity'] = 0
    assets[0]['items'][1]['quantity'] = '0'
    result = run(assets)

    assert len(result) == 2
    assert '65305409CA' not in [row[MPN] for row in result]


def test_current_assets_excluded_production_hub(run, progress, assets):
    assets = copy.deepcopy(assets)
    assets[0]['connection']['type'] = 'production'
    assets[0]['connection']['hub']['id'] = 'HB-4043-4841'
    params = copy.deepcopy(parameters)
    params['connexion_type']['choices'] = ['production']
    query = QUERY.format(status='active', conn='production')
    result = run(assets, params, query)

    assert result == []
    progress.assert_called_with(1, 1)


def test_current_assets_3yc_filter(run, progress, assets):
    params = copy.deepcopy(parameters)
    params['commitment_status'] = '3yc'

    assert run(assets, params) == []

    assets = copy.deepcopy(assets)
    _set_param(assets[0], 'commitment_status', 'COMMITTED', 'PRM-207-752-513-0099')
    result = run(assets, params)

    assert len(result) == 4
    assert result[0][26] == 'COMMITTED'  # 3YC Status


def test_current_assets_empty(run, progress):
    assert run([]) == []
    progress.assert_not_called()


def test_has_quantity_unparseable_keeps_item():
    assert entrypoint._has_quantity({'quantity': 'n/a'}) is True
    assert entrypoint._has_quantity({}) is False


def test_current_assets_multiple_marketplaces_query(run, assets):
    params = copy.deepcopy(parameters)
    params['mkp']['choices'] = ['MP-65669', 'MP-12345']
    query = ASSETS_QUERY.replace('(MP-65669)', '(MP-65669,MP-12345)')

    assert len(run(assets, params, query)) == 4


def test_current_assets_params_matched_by_name(run, assets):
    # params added later to the product get a generated id, only the name is stable
    assets = copy.deepcopy(assets)
    for param in assets[0]['params']:
        if param['name'] == 'discount_group':
            param['id'] = 'PRM-207-752-513-0065'
    _set_param(assets[0], 'discount_group_consumables', '02A12', 'PRM-207-752-513-0092')
    _set_param(assets[0], 'external_reference_id', 'EXT-1', 'PRM-207-752-513-0087')
    row = run(assets)[0]

    assert row[22] == '04A12'  # Discount Group Licenses
    assert row[23] == '02A12'  # Discount Group Consumables
    assert row[30] == 'EXT-1'  # External Reference ID
    assert row[19] == 'P1005042327'  # Adobe Customer ID (id == name)
