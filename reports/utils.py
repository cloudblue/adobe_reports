import datetime
import re
import requests
from reports import api_calls

BASE_CURRENCY = 'USD'
FOREXAPI_URL = 'https://theforexapi.com/api/latest'


def process_line(asset: dict, asset_headers: list, asset_params_headers: list, marketplace_params: dict) -> list:
    """
    This functions uses several functions on this file to build a line with values to yield at xlsx file

    :param asset: one asset from requested assets
    :param asset_headers: headers to build the dictionaries
    :param asset_params_headers: headers to build the dictionaries
    :param marketplace_params: dict to build the line
    :return: list with line values
    """
    asset_values = _process_asset_headers(asset, asset_headers)
    asset_values.update(_process_asset_parameters(asset['params'], asset_params_headers))
    asset_values['renewal_date'] = _calculate_renewal_date(
        asset_values['renewal_date'], asset_values['created-at'], asset_values['action_type'])
    asset_values.update(marketplace_params)
    return list(asset_values.values())


def _process_asset_headers(asset, asset_headers) -> dict:
    """
    This function takes an asset and asset_headers to reach values in asset for
    each key at asset_headers

    :type asset: dict
    :type asset_headers: list
    :param asset: one asset from requested assets
    :param asset_headers: headers to use as keys
    :return: dict with values from asset and keys from headers
    """
    params = dict.fromkeys(asset_headers)
    for header in asset_headers:
        if '-' in header:
            params[header] = _get_value_from_split_header(asset, header)
        else:
            params[header] = asset[header]
    return params


def _process_asset_parameters(asset_params: list, asset_parameters: list) -> dict:
    """
    This function takes asset_params and asset_parameters(headers) to reach values in asset_params for
    each key at asset_parameters

    :type asset_params: list
    :type asset_parameters: list
    :param asset_params: requested asset['params'] from connect
    :param asset_parameters: headers with keys to build the dict and reach the values
    :return: dict with values from asset_params and keys from asset_parameters
    """
    params_dict = dict.fromkeys(asset_parameters)
    for param in asset_params:
        param_id = param['id']
        if param_id == 'discount_group':
            discount_group = get_discount_level(param['value'])
            params_dict[param_id] = discount_group
        elif param_id in asset_parameters:
            params_dict[param_id] = param['value']
    return params_dict


def _calculate_renewal_date(renewal_date_parameter, asset_creation_date, action_type):
    # Net new, dates set by asset. Second validation n case the report is executed for a non-Adobe product,
    # making sure it doesn't fail
    if action_type == 'purchase' or renewal_date_parameter is None or renewal_date_parameter == '-' or \
            renewal_date_parameter == '' or '/' not in renewal_date_parameter:
        if datetime.datetime.now(datetime.timezone.utc) < (
                datetime.datetime.fromisoformat(asset_creation_date) + datetime.timedelta(days=365)):
            renewal_date = datetime.datetime.fromisoformat(asset_creation_date) + datetime.timedelta(days=365)
        else:
            renewal_date = datetime.datetime.fromisoformat(asset_creation_date).replace(
                year=(datetime.datetime.now(datetime.timezone.utc).year + 1))
    else:  # Transfer, use parameter value
        if '/' in renewal_date_parameter:
            regex = re.match('(.*)/(.*)/(.*)', renewal_date_parameter)
            renewal_date_parameter = regex.group(3) + '-' + regex.group(2) + '-' + regex.group(1)
        if datetime.datetime.now(datetime.timezone.utc) < (
                datetime.datetime.fromisoformat(renewal_date_parameter).replace(
                    tzinfo=datetime.timezone.utc) + datetime.timedelta(days=365)):
            renewal_date = datetime.datetime.fromisoformat(renewal_date_parameter).replace(
                tzinfo=datetime.timezone.utc) + datetime.timedelta(days=365)
        else:
            renewal_date = datetime.datetime.fromisoformat(renewal_date_parameter).replace(
                tzinfo=datetime.timezone.utc).replace(year=(datetime.datetime.now(datetime.timezone.utc).year + 1))

    return renewal_date.strftime("%Y-%m-%d %H:%M:%S")


def _get_value_from_split_header(asset: dict, header: str) -> str:
    """
    This function gets the header with '-' format and split it to reach the value in asset
    example: product-id -> asset[product][id]

    :type asset: dict
    :type header: str
    :param asset: requested asset from connect
    :param header: str from headers
    :return: str with value from asset
    """
    h0 = header.split('-')[0]
    h1 = header.split('-')[1]
    if h0 == 'created':
        value = asset['events'][h0][h1]
    elif h0 == 'provider':
        value = asset['connection'][h0][h1]
    elif h0 in ['customer', 'reseller']:
        if h0 == 'reseller':
            h0 = 'tier1'
        value = asset['tiers'][h0][h1]
    else:
        value = asset[h0][h1]
    return value


def get_discount_level(discount_group: str) -> str:
    """
    Transform the discount_group to a proper level of discount

    :type discount_group: str
    :param discount_group:
    :return: str with level of discount
    """
    if discount_group == '01A12':
        discount = 'Level 1'
    elif discount_group == '02A12':
        discount = 'Level 2'
    elif discount_group == '03A12':
        discount = 'Level 3'
    elif discount_group == '04A12':
        discount = 'Level 4'
    elif discount_group == '01012':
        discount = 'TLP Level 1'
    elif discount_group == '02012':
        discount = 'TLP Level 2'
    elif discount_group == '03012':
        discount = 'TLP Level 3'
    elif discount_group == '04012':
        discount = 'TLP Level 4'
    elif discount_group == '':
        discount = 'Empty'
    else:
        discount = 'Other'
    return discount


def get_marketplace_params(client, asset):
    """
    This function returns a dict with key,value pairs for each marketplace_header or None if there is no listing
    for the marketplace and product in asset

    :type client:
    :type asset: dict
    :param client:
    :param asset: dict with asset from connect
    :return: dict if listing or None
    """
    listing = api_calls.request_listing(client, asset['marketplace']['id'], asset['product']['id'])
    if listing and 'pricelist' in listing:
        price_list_version = api_calls.request_price_list(client, listing['pricelist']['id'])
        price_list_points = api_calls.request_price_list_version_points(client, price_list_version['id'])
        if price_list_version and price_list_points:
            # dict with currency and currency change
            currency = _get_currency_and_change(price_list_version)

            # dict with all financials from all items in price list
            price_list_financials = get_financials_from_price_list(price_list_points)

            # dict with seats and financials from assets items
            financials_and_seats = _get_financials_and_seats(asset['items'], price_list_financials)

            # dict with financials in USD
            base_financials = _get_base_currency_financials(financials_and_seats, currency)

            currency.pop('change')
            currency.update(financials_and_seats)
            currency.update(base_financials)
            return currency
    # Listing has no price list or is not active
    return None


def get_financials_from_price_list(price_lists_points: list) -> dict:
    """
    This function retrieves the cost, reseller_cost and msrp from each point at the price list points

    :type price_lists_points: list
    :param price_lists_points: request with points of price list
    :return: dict with cost, reseller_cost and msrp
    """
    items_financials = {}
    for point in price_lists_points:
        if point['item']['global_id'] not in items_financials:
            items_financials[point['item']['global_id']] = {}
        if float(point['attributes']['price']) != 0.0:
            items_financials[point['item']['global_id']]['cost'] = \
                float(point['attributes']['price'])

            items_financials[point['item']['global_id']]['reseller_cost'] = \
                float(point['attributes']['st0p']) if 'st0p' in point['attributes'] else 0.0

            items_financials[point['item']['global_id']]['msrp'] = \
                float(point['attributes']['st1p']) if 'st1p' in point['attributes'] else 0.0
    return items_financials


def _get_currency_and_change(price_list_version: dict) -> dict:
    """
    Use the price list version to retrieve the currency and change from this currency to dollars

    :type price_list_version: dict
    :param price_list_version: request with price list version
    :return: dict containing currency acronym and currency change
    """
    currency = {'currency': price_list_version['pricelist']['currency']}
    if currency['currency'] != BASE_CURRENCY:
        try:
            exchange_response = requests.get(FOREXAPI_URL)
            if exchange_response.status_code == 200:
                currency['change'] = exchange_response.json()['rates'][BASE_CURRENCY]
        except requests.exceptions.RequestException as e:
            print(e)
    else:
        currency['change'] = 1.0
    return currency


def _get_financials_and_seats(asset_items: list, price_list_financials: dict) -> dict:
    """
    This function takes the items from asset request and price list for those items to return a dict
    with the marketplace_headers as keys and their values filled if present on asset items

    :type price_list_financials: dict
    :type asset_items: list
    :param asset_items: list with items from requested asset
    :param price_list_financials: dict with cost, reseller_cost and msrp for each item[global_id]
    :return: dict with marketplace_headers as keys(not automated)
    """
    asset_financials = {}
    asset_type = None
    seats = cost = reseller_cost = msrp = 0.0
    for item in asset_items:
        item_quantity = int(item['quantity'])
        if 'Enterprise' in item['display_name'] and not asset_type:
            asset_type = 'enterprise'
        elif 'Enterprise' in item['display_name'] and asset_type == 'team':
            asset_type = 'both'
        else:
            asset_type = 'team'
        if item_quantity > 0:
            seats = seats + item_quantity
            if price_list_financials and item['global_id'] in price_list_financials:
                cost = cost + item_quantity * price_list_financials[item['global_id']]['cost']
                reseller_cost = reseller_cost + item_quantity * price_list_financials[item['global_id']][
                    'reseller_cost']
                msrp = msrp + item_quantity * price_list_financials[item['global_id']]['msrp']

    asset_financials['purchase_type'] = asset_type
    asset_financials['cost'] = cost
    asset_financials['reseller_cost'] = reseller_cost
    asset_financials['msrp'] = msrp
    asset_financials['seats'] = seats
    return asset_financials


def _get_base_currency_financials(financials_and_seats: dict, currency: dict) -> dict:
    """
    This function returns the value in dollars for the current cost, reseller_cost and msrp

    :type financials_and_seats: dict
    :type currency: dict
    :param financials_and_seats: contains the cost, reseller_cost and msrp
    :param currency: contains the change(float) to multiply against financials_and_seats values
    :return: dict with cost, reseller_cost and msrp in dollars
    """
    return {
        'USD-cost': '{:0.2f}'.format(financials_and_seats['cost'] * currency['change']),
        'USD-reseller_cost': '{:0.2f}'.format(financials_and_seats['reseller_cost'] * currency['change']),
        'USD-msrp': '{:0.2f}'.format(financials_and_seats['msrp'] * currency['change'])}
