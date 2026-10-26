# -*- coding: utf-8 -*-
#
# Copyright (c) 2022, Carlos Anuarbe
# All rights reserved.
#

from reports import utils
import datetime

# queries
LISTING_QUERY = 'and(eq(marketplace.id,MP-65669),eq(product.id,PRD-207-752-513),eq(status,listed))'


def test_get_param_value(asset):
    assert utils.get_param_value(asset[0]['params'], 'asdf') == '-'
    assert utils.get_param_value(asset[0]['params'], 't0_o_email') == 'mamam@mia.com'


def test_get_value(asset):
    assert utils.get_value(asset[0], 'product', 'asd') == '-'
    assert utils.get_value(asset[0], 'product', 'id') == 'PRD-207-752-513'


def test_convert_to_datetime():
    assert utils.convert_to_datetime('') == '-'


def test_calculate_renewal_date_():
    date_leap = datetime.date(2020, 2, 29)
    current_date_before = datetime.date(2021, 1, 1)
    current_date_after = datetime.date(2021, 6, 16)
    current_date_leap = datetime.date(2024, 2, 29)

    # Leap year before the current date
    assert utils.calculate_renewal_date(str(date_leap), current_date_before) == datetime.date(2021, 3, 1)

    # Leap year after current date
    assert utils.calculate_renewal_date(str(date_leap), current_date_after) == datetime.date(2022, 3, 1)

    # Both dates are leap dates
    assert utils.calculate_renewal_date(str(date_leap), current_date_leap) == datetime.date(2024, 2, 29)

    # Normal date
    assert utils.calculate_renewal_date(str(current_date_after), current_date_leap) == datetime.date(2024, 6, 16)


def test_get_financials_from_product_per_marketplace(sync_client_factory, response_factory, asset):
    responses = [
        response_factory(
            query=LISTING_QUERY,
            value=[]
        ),
    ]
    client = sync_client_factory(responses)
    assert utils.get_financials_from_product_per_marketplace(
        client, asset[0]['marketplace']['id'], asset[0]['product']['id']) == {}


def test_same_currency(pricelist_version):
    assert utils.get_currency_and_change(pricelist_version[1])['change'] == 1.0


def test_get_financials_and_seats(assets):
    items = assets[0]['items']
    price_list_financials = {}
    utils.get_financials_and_seats(items, price_list_financials)


def test_discount_level():
    group1 = '01A12'
    group2 = '01012'
    assert utils.get_discount_level(group1) == 'Level 1'
    assert utils.get_discount_level(group2) == 'TLP Level 1'
    assert utils.get_discount_level('nothing') == 'Empty'


def test_auto_renewal_status():
    active = 'active_auto_renewal_status'
    inactive = 'inactive_auto_renewal_status'
    assert utils.get_auto_renewal_status(active) == 'Active'
    assert utils.get_auto_renewal_status(inactive) == 'Inactive'
    assert utils.get_discount_level('nothing') == 'Empty'

def test_structured_value():
    structured_value_true = {
        "id": "three_years_commitment",
        "structured_value": {
            "3 Years commitment": True
        },
        "value_choices": [
            {
                "label": "3YC",
                "value": "3 Years commitment"
            }
        ]
    }
    structured_value_false = {
        "id": "three_years_commitment",
        "structured_value": {
            "3 Years commitment": False
        },
        "value_choices": [
            {
                "label": "3YC",
                "value": "3 Years commitment"
            }
        ]
    }
    assert utils.get_three_years_commitment(structured_value_true) == 'Y'
    assert utils.get_three_years_commitment(structured_value_false) == 'N'

def test_three_years_commitment():
    structured_value_true = {
        "id": "three_years_commitment",
        "structured_value": {
            "3 Years commitment": True
        }
    }
    structured_value_false = {
        "id": "three_years_commitment",
        "structured_value": {
            "3 Years commitment": False
        }
    }
    assert utils.get_three_years_commitment(structured_value_true) == 'Y'
    assert utils.get_three_years_commitment(structured_value_false) == 'N'

def test_three_years_recommitment():
    structured_value_true = {
        "id": "three_years_recommitment",
        "structured_value": {
            "3YR": True
        },
    }
    structured_value_false = {
        "id": "three_years_recommitment",
        "structured_value": {
            "3YR": False
        },
    }
    assert utils.get_three_years_recommitment(structured_value_true) == 'Y'
    assert utils.get_three_years_recommitment(structured_value_false) == 'N'


def test_get_hub_id():
    connection = {'hub': {'id': 'HB-1234-5678'}}
    assert utils.get_hub_id(connection) == 'HB-1234-5678'

    connection_no_hub = {'provider': {'id': 'PR-1234'}}
    assert utils.get_hub_id(connection_no_hub) == '-'

    assert utils.get_hub_id(None) == '-'


def test_get_hub_name():
    # Case 1: Hub exists and has a valid name
    connection = {
        'hub': {'name': 'My Hub'},
        'provider': {'name': 'My Provider'}
    }
    assert utils.get_hub_name(connection) == 'My Hub'

    # Case 2: Hub name is None
    connection_none = {
        'hub': {'name': None},
        'provider': {'name': 'My Provider'}
    }
    assert utils.get_hub_name(connection_none) == 'My Provider'

    # Case 3: Hub name is "None" string
    connection_none_str = {
        'hub': {'name': 'None'},
        'provider': {'name': 'My Provider'}
    }
    assert utils.get_hub_name(connection_none_str) == 'My Provider'

    # Case 4: Hub missing
    connection_no_hub = {
        'provider': {'name': 'My Provider'}
    }
    assert utils.get_hub_name(connection_no_hub) == 'My Provider'


# --- CBPFR-2164: Flex discount (cb_flex_discount_final + cb_flex_discounts_applied) ---

def test_get_flex_discounts_no_param():
    """Missing both params -> all keys '-'."""
    params = []
    result = utils.get_flex_discounts(params, 'MPN-1', 'ORD-1')
    assert result['discounted_mpn'] == '-'
    assert result['application_type'] == '-'
    assert result['discount_value'] == '-'


def test_get_flex_discounts_legacy_single_match():
    """Legacy cb_flex_discounts_applied: match by MPN + order_id; new columns '-'."""
    params = [
        {
            'id': 'cb_flex_discounts_applied',
            'structured_value': {
                'discounts': [
                    {'mpn': 'MPN-A', 'order_id': 'ORD-1', 'id': 'id1', 'code': 'CODE1'}
                ]
            },
        }
    ]
    result = utils.get_flex_discounts(params, 'MPN-A', 'ORD-1')
    assert result['discounted_mpn'] == 'MPN-A'
    assert result['discounted_order_id'] == 'ORD-1'
    assert result['discount_id'] == 'id1'
    assert result['discount_code'] == 'CODE1'
    assert result['application_type'] == '-'
    assert result['discount_type'] == '-'
    assert result['discount_value'] == '-'


def test_get_flex_discounts_legacy_no_match():
    """Legacy: no match -> all '-'."""
    params = [
        {
            'id': 'cb_flex_discounts_applied',
            'structured_value': {'discounts': [{'mpn': 'OTHER', 'order_id': 'X', 'id': 'i', 'code': 'c'}]},
        }
    ]
    result = utils.get_flex_discounts(params, 'MPN-A', 'ORD-1')
    assert result['discounted_mpn'] == '-'


def test_get_flex_discounts_new_format_match():
    """New cb_flex_discount_final: match by MPN only; request order # for context; new columns."""
    params = [
        {
            'id': 'cb_flex_discount_final',
            'structured_value': {
                'discounts': [
                    {
                        'mpn': '30001472CB',
                        'id': 'uuid-1',
                        'code': 'FLEX_EDU',
                        'application_type': 'FULL_CHAIN',
                        'discounts': [
                            {'type': 'PERCENTAGE_DISCOUNT', 'values': [{'discountValue': 15}]}
                        ],
                    }
                ]
            },
        }
    ]
    result = utils.get_flex_discounts(params, '30001472CB', 'P9201150234')
    assert result['discounted_mpn'] == '30001472CB'
    assert result['discounted_order_id'] == 'P9201150234'
    assert result['discount_id'] == 'uuid-1'
    assert result['discount_code'] == 'FLEX_EDU'
    assert result['application_type'] == 'FULL_CHAIN'
    assert result['discount_type'] == 'PERCENTAGE_DISCOUNT'
    assert result['discount_value'] == '15'


def test_get_flex_discounts_new_format_multiple_nested():
    """New format: multiple nested discounts -> concatenate type and value (amount only)."""
    params = [
        {
            'id': 'cb_flex_discount_final',
            'structured_value': {
                'discounts': [
                    {
                        'mpn': 'MPN-X',
                        'id': 'id1',
                        'code': 'C1',
                        'application_type': 'FULL_CHAIN',
                        'discounts': [
                            {'type': 'PERCENTAGE_DISCOUNT', 'values': [{'discountValue': 10}]},
                            {'type': 'FIXED_DISCOUNT', 'values': [{'discountValue': 20}]},
                        ],
                    }
                ]
            },
        }
    ]
    result = utils.get_flex_discounts(params, 'MPN-X', 'ORD-R')
    assert result['discount_type'] == 'PERCENTAGE_DISCOUNT,FIXED_DISCOUNT'
    assert result['discount_value'] == '10,20'


def test_get_flex_discounts_failover_prefer_final():
    """When both params have data, prefer cb_flex_discount_final."""
    params = [
        {
            'id': 'cb_flex_discounts_applied',
            'structured_value': {
                'discounts': [{'mpn': 'MPN-A', 'order_id': 'ORD-1', 'id': 'legacy', 'code': 'L'}],
            },
        },
        {
            'id': 'cb_flex_discount_final',
            'structured_value': {
                'discounts': [
                    {
                        'mpn': 'MPN-A',
                        'id': 'final',
                        'code': 'F',
                        'application_type': 'FULL_CHAIN',
                        'discounts': [{'type': 'PERCENTAGE_DISCOUNT', 'values': [{'discountValue': 5}]}],
                    }
                ]
            },
        },
    ]
    result = utils.get_flex_discounts(params, 'MPN-A', 'ORD-1')
    assert result['discount_id'] == 'final'
    assert result['application_type'] == 'FULL_CHAIN'
    assert result['discount_value'] == '5'


def test_get_flex_discounts_failover_final_empty_use_applied():
    """When final is present but empty, use cb_flex_discounts_applied."""
    params = [
        {
            'id': 'cb_flex_discount_final',
            'structured_value': {'discounts': []},
        },
        {
            'id': 'cb_flex_discounts_applied',
            'structured_value': {
                'discounts': [{'mpn': 'MPN-B', 'order_id': 'O2', 'id': 'applied-id', 'code': 'A'}],
            },
        },
    ]
    result = utils.get_flex_discounts(params, 'MPN-B', 'O2')
    assert result['discount_id'] == 'applied-id'
    assert result['application_type'] == '-'
