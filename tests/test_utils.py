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
