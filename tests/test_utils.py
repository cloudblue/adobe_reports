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
