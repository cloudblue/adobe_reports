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


def test_get_hub_id():
    assert utils.get_hub_id(None) == '-'
    assert utils.get_hub_id({}) == '-'
    assert utils.get_hub_id({'hub': {'id': 'HB-3050-0939', 'name': 'commerce-dev.platform.cloudblue.io'}}) == 'HB-3050-0939'
    assert utils.get_hub_id({'hub': {}}) == '-'
    assert utils.get_hub_id({'hub': {'name': 'Only Name'}}) == '-'


def test_get_hub_name():
    assert utils.get_hub_name(None) == '-'
    assert utils.get_hub_name({}) == '-'
    conn = {'hub': {'id': 'HB-3050-0939', 'name': 'commerce-dev.platform.cloudblue.io'}, 'provider': {'name': 'My Provider'}}
    assert utils.get_hub_name(conn) == 'commerce-dev.platform.cloudblue.io'
    assert utils.get_hub_name({'hub': {}, 'provider': {'name': 'Fallback Provider'}}) == 'Fallback Provider'
    assert utils.get_hub_name({'provider': {'name': 'Provider Only'}}) == 'Provider Only'
    # When hub name is None or string "None", use Provider Name
    assert utils.get_hub_name({'hub': {'name': None}, 'provider': {'name': 'Provider When None'}}) == 'Provider When None'
    assert utils.get_hub_name({'hub': {'name': 'None'}, 'provider': {'name': 'Provider When String None'}}) == 'Provider When String None'


def test_convert_to_datetime():
    assert utils.convert_to_datetime('') == '-'


def test_calculate_renewal_date_():
    date_actual_year = utils.today().replace(
        tzinfo=datetime.timezone.utc).replace(year=2020) + datetime.timedelta(days=1)
    date_next_year = utils.today().replace(
        tzinfo=datetime.timezone.utc).replace(year=2022) - datetime.timedelta(days=1)

    # renewal this year
    assert utils.calculate_renewal_date(str(date_actual_year)) == \
           date_actual_year.replace(year=utils.today().year)

    # renewal next year
    assert utils.calculate_renewal_date(str(date_next_year)) == \
           date_next_year.replace(year=utils.today().year + 1)


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


def test_get_flex_discounts_with_single_match():
    """Test get_flex_discounts with a single matching discount using structured_value"""
    params = [
        {
            'id': 'cb_flex_discounts_applied',
            'type': 'object',
            'value': '',
            'structured_value': {
                'discounts': [
                    {
                        'mpn': '65304520CA',
                        'order_id': 'P9201911604',
                        'id': '55555555-8768-4e8a-9a2f-fb6a6b08f557',
                        'code': 'ADOBE_ALL_PROMOTION'
                    }
                ]
            }
        }
    ]
    result = utils.get_flex_discounts(params, '65304520CA', 'P9201911604')
    assert result['discounted_mpn'] == '65304520CA'
    assert result['discounted_order_id'] == 'P9201911604'
    assert result['discount_id'] == '55555555-8768-4e8a-9a2f-fb6a6b08f557'
    assert result['discount_code'] == 'ADOBE_ALL_PROMOTION'


def test_get_flex_discounts_with_multiple_matches():
    """Test get_flex_discounts with multiple matching discounts (concatenated)"""
    params = [
        {
            'id': 'cb_flex_discounts_applied',
            'type': 'object',
            'value': '',
            'structured_value': {
                'discounts': [
                    {
                        'mpn': '65304520CA',
                        'order_id': 'P9201911604',
                        'id': '11111111-1111-1111-1111-111111111111',
                        'code': 'PROMO_1'
                    },
                    {
                        'mpn': '65304520CA',
                        'order_id': 'P9201911604',
                        'id': '22222222-2222-2222-2222-222222222222',
                        'code': 'PROMO_2'
                    }
                ]
            }
        }
    ]
    result = utils.get_flex_discounts(params, '65304520CA', 'P9201911604')
    assert result['discounted_mpn'] == '65304520CA,65304520CA'
    assert result['discounted_order_id'] == 'P9201911604,P9201911604'
    assert result['discount_id'] == '11111111-1111-1111-1111-111111111111,22222222-2222-2222-2222-222222222222'
    assert result['discount_code'] == 'PROMO_1,PROMO_2'


def test_get_flex_discounts_no_match():
    """Test get_flex_discounts when no matching discount is found"""
    params = [
        {
            'id': 'cb_flex_discounts_applied',
            'type': 'object',
            'value': '',
            'structured_value': {
                'discounts': [
                    {
                        'mpn': '65304520CA',
                        'order_id': 'P9201911604',
                        'id': '55555555-8768-4e8a-9a2f-fb6a6b08f557',
                        'code': 'ADOBE_ALL_PROMOTION'
                    }
                ]
            }
        }
    ]
    result = utils.get_flex_discounts(params, 'DIFFERENT_MPN', 'P9201911604')
    assert result['discounted_mpn'] == '-'
    assert result['discounted_order_id'] == '-'
    assert result['discount_id'] == '-'
    assert result['discount_code'] == '-'


def test_get_flex_discounts_missing_parameter():
    """Test get_flex_discounts when parameter doesn't exist"""
    params = [
        {
            'id': 'some_other_param',
            'value': 'some_value',
        }
    ]
    result = utils.get_flex_discounts(params, '65304520CA', 'P9201911604')
    assert result['discounted_mpn'] == '-'
    assert result['discounted_order_id'] == '-'
    assert result['discount_id'] == '-'
    assert result['discount_code'] == '-'


def test_get_flex_discounts_with_json_string():
    """Test get_flex_discounts with JSON string in value field (backward compatibility)"""
    params = [
        {
            'id': 'cb_flex_discounts_applied',
            'value': '{"discounts":[{"mpn":"65304520CA","order_id":"P9201911604","id":"55555555-8768-4e8a-9a2f-fb6a6b08f557","code":"ADOBE_ALL_PROMOTION"}]}',
        }
    ]
    result = utils.get_flex_discounts(params, '65304520CA', 'P9201911604')
    assert result['discounted_mpn'] == '65304520CA'
    assert result['discounted_order_id'] == 'P9201911604'
    assert result['discount_id'] == '55555555-8768-4e8a-9a2f-fb6a6b08f557'
    assert result['discount_code'] == 'ADOBE_ALL_PROMOTION'


def test_get_flex_discounts_invalid_json():
    """Test get_flex_discounts with invalid JSON"""
    params = [
        {
            'id': 'cb_flex_discounts_applied',
            'value': 'invalid json {{{',
        }
    ]
    result = utils.get_flex_discounts(params, '65304520CA', 'P9201911604')
    assert result['discounted_mpn'] == '-'
    assert result['discounted_order_id'] == '-'
    assert result['discount_id'] == '-'
    assert result['discount_code'] == '-'


def test_get_days_between_effective_and_renewal_date_with_timezone():
    """Test prorata calculation with timezone in effective date"""
    result = utils.get_days_between_effective_and_renewal_date(
        '2020-11-23T12:52:27+00:00',
        '2021-11-23'
    )
    assert result == 365


def test_get_days_between_effective_and_renewal_date_without_timezone():
    """Test prorata calculation without timezone in effective date"""
    result = utils.get_days_between_effective_and_renewal_date(
        '2020-11-23T12:52:27',
        '2021-11-23'
    )
    assert result == 365


def test_get_days_between_effective_and_renewal_date_space_separator():
    """Test prorata calculation with space separator in effective date"""
    result = utils.get_days_between_effective_and_renewal_date(
        '2020-11-23 12:52:27',
        '2021-11-23'
    )
    assert result == 365


def test_get_days_between_effective_and_renewal_date_real_data():
    """Test prorata calculation with real data from report"""
    result = utils.get_days_between_effective_and_renewal_date(
        '2025-10-10T03:20:04+00:00',
        '2026-09-08'
    )
    assert result == 333


def test_get_days_between_effective_and_renewal_date_missing_effective():
    """Test prorata calculation with missing effective date"""
    result = utils.get_days_between_effective_and_renewal_date(
        '-',
        '2021-11-23'
    )
    assert result == '-'


def test_get_days_between_effective_and_renewal_date_missing_renewal():
    """Test prorata calculation with missing renewal date"""
    result = utils.get_days_between_effective_and_renewal_date(
        '2020-11-23T12:52:27+00:00',
        '-'
    )
    assert result == '-'


def test_get_flex_discounts_empty_discounts():
    """Test get_flex_discounts with empty discounts array"""
    params = [
        {
            'id': 'cb_flex_discounts_applied',
            'type': 'object',
            'value': '',
            'structured_value': {
                'discounts': []
            }
        }
    ]
    result = utils.get_flex_discounts(params, '65304520CA', 'P9201911604')
    assert result['discounted_mpn'] == '-'
    assert result['discounted_order_id'] == '-'
    assert result['discount_id'] == '-'
    assert result['discount_code'] == '-'
