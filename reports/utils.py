from reports import api_calls
from datetime import datetime, timezone, date
import calendar
import json

BASE_CURRENCY = 'USD'
FOREXAPI_URL = 'https://theforexapi.com/api/latest'

def get_param_value_by_name(params: list, value: str) -> str:
    try:
        if params[0]['name'] == value:
            return params[0]['value']
        if len(params) == 1:
            return '-'
        return get_param_value_by_name(list(params[1:]), value)
    except Exception:
        return '-'


def get_param_value(params: list, value: str) -> str:
    try:
        if params[0]['id'] == value:
            return params[0]['value']
        if len(params) == 1:
            return '-'
        return get_param_value(list(params[1:]), value)
    except Exception:
        return '-'


def get_basic_value(base, value):
    try:
        if base and value in base:
            return base[value]
        return '-'
    except Exception:
        return '-'


def get_value(base, prop, value):
    if prop in base:
        return get_basic_value(base[prop], value)
    return '-'


def convert_to_datetime(param_value):
    if param_value == "" or param_value == "-" or param_value is None:
        return "-"

    return datetime.strptime(
        param_value.replace("T", " ").replace("+00:00", ""),
        "%Y-%m-%d %H:%M:%S",
    )


def today() -> datetime:
    return datetime.today()


def today_str() -> str:
    return datetime.today().strftime('%Y-%m-%d %H:%M:%S')


def process_asset_headers(asset, asset_headers) -> dict:
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
            params[header] = get_value_from_split_header(asset, header)
        else:
            if header in asset:
                params[header] = asset[header]
            else:
                params[header] = '-'

    return params


def process_asset_parameters_by_name(asset_params: list, asset_parameters: list) -> dict:
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

    handlers = {
        'discount_group': lambda param: get_discount_level(param['value']),
        'discount_group_consumables': lambda param: get_discount_level(param['value']),
        'cb_adobe_account_subscription_list': get_account_subscription_list,
        'auto_renewal_status': lambda param: get_auto_renewal_status(param['value']),
        'three_years_commitment': get_three_years_commitment,
        'three_years_recommitment': get_three_years_recommitment
    }

    for param in asset_params:
        param_id = param['name']
        if param_id in handlers:
            params_dict[param_id] = handlers[param_id](param)
        elif param_id in asset_parameters:
            params_dict[param_id] = param['value'] if 'value' in param else ''
    return params_dict

def handle_renewal_date(asset_creation_date: str) -> date:
    return calculate_renewal_date(asset_creation_date, datetime.now(timezone.utc).date())

def calculate_renewal_date(asset_creation_date: str, current_date: date) -> date:
    date = datetime.fromisoformat(asset_creation_date).date()
    renewal_date = resolve_leap_year_renewal_date(date, current_date.year)
    if renewal_date >= current_date:
        return renewal_date
    return resolve_leap_year_renewal_date(renewal_date, current_date.year + 1)


def resolve_leap_year_renewal_date(original_date: date, target_year: int) -> date:
    if calendar.isleap(original_date.year) and original_date.month == 2 and original_date.day == 29:
        if calendar.isleap(target_year):
            return original_date.replace(year=target_year)
        else:
            return date(year=target_year, month=3, day=1)
    return original_date.replace(year=target_year)



def get_hub_id(connection: dict) -> str:
    """
    Return Hub ID from asset.connection, or '-' if missing/empty.
    """
    if not connection:
        return '-'
    value = get_value(connection, 'hub', 'id')
    return value if value else '-'


def get_hub_name(connection: dict) -> str:
    """
    Return Hub Name from asset.connection. If hub is missing, name empty,
    or name is None/the string "None", return Provider Name for consistency.
    """
    if not connection:
        return '-'
    hub = connection.get('hub') or {}
    name = get_basic_value(hub, 'name')
    if name and name != '-' and str(name).strip().lower() != 'none':
        return name
    return get_value(connection, 'provider', 'name')

    

def get_value_from_split_header(asset: dict, header: str) -> str:
    """
    This function gets the header with '-' format and split it to reach the value in asset
    example: product-id -> asset[product][id]

    :type asset: dict
    :type header: str
    :param asset: requested asset from connect
    :param header: str from headers
    :return: str with value from asset
    """
    try:
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
    except Exception:
        return '-'


def get_discount_level(discount_group: str) -> str:
    """
    Transform the discount_group to a proper level of discount

    :type discount_group: str
    :param discount_group:
    :return: str with level of discount
    """
    if len(discount_group) > 2 and discount_group[2] == 'A' and discount_group[0] == '1':
        discount = 'Level ' + discount_group[0:2]
    elif len(discount_group) > 2 and discount_group[2] == 'A':
        discount = 'Level ' + discount_group[1]
    elif len(discount_group) > 2 and discount_group[2] == '0':
        discount = 'TLP Level ' + discount_group[1]
    else:
        discount = 'Empty'

    return discount


def get_financials_from_price_list(price_list_points: list) -> dict:
    """
    This function retrieves the cost, reseller_cost and msrp from each point at the price list points

    :type price_list_points: list
    :param price_list_points: request with points of price list
    :return: dict with cost, reseller_cost and msrp
    """
    items_financials = {}
    for point in price_list_points:
        items_financials[point['item']['global_id']] = {} if point['item']['global_id'] not in items_financials \
            else point['item']['global_id']
        if float(point['attributes']['price']) != 0.0:
            items_financials[point['item']['global_id']]['cost'] = \
                float(point['attributes']['price'])

            items_financials[point['item']['global_id']]['reseller_cost'] = \
                float(point['attributes']['st0p']) if 'st0p' in point['attributes'] else 0.0

            items_financials[point['item']['global_id']]['msrp'] = \
                float(point['attributes']['st1p']) if 'st1p' in point['attributes'] else 0.0
    return items_financials


def get_currency_and_change(price_list_version: dict) -> dict:
    """
    Use the price list version to retrieve the currency and change from this currency to dollars in case
    of api fail the change will be 0 so the USD columns will be 0

    :type price_list_version: dict
    :param price_list_version: request with price list version
    :return: dict containing currency acronym and currency change
    """
    currency = {'currency': price_list_version['pricelist']['currency']}
    if currency['currency'] != BASE_CURRENCY:
        exchange_response = api_calls.request_get(FOREXAPI_URL)
        if exchange_response.status_code == 200:
            currency['change'] = exchange_response.json()['rates'][BASE_CURRENCY]
        else:
            currency['change'] = 0.0
    else:
        currency['change'] = 1.0

    return currency


def get_financials_and_seats(items: list, price_list_financials: dict) -> dict:
    """
    This function takes items and price list for those items to return a dict with values if they
    exits at items and all financials added from each item

    :type price_list_financials: dict
    :type items: list
    :param items: list with items from request
    :param price_list_financials: dict with cost, reseller_cost and msrp for each item[global_id]
    :return: dict
    """
    asset_financials = {}
    asset_type = None
    seats = cost = reseller_cost = msrp = 0.0
    for item in items:
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


def get_base_currency_financials(financials_and_seats: dict, currency: dict) -> dict:
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


# This function was used in reports/requests/entrypoint.py to retrieve financial data
# for the removed columns. Commenting out eliminates 3 API calls per request, improving performance.
# NOTE: This function is NOT used in the Assets report. The Assets report uses direct API calls
# to request_listing(), request_price_list(), and request_price_list_version_points() instead.
# If you need to restore the financial columns, uncomment this function and the related code
# in reports/requests/entrypoint.py (lines 39-45 and lines 109-113).
#
def get_financials_from_product_per_marketplace(client, marketplace_id, asset_id):
    listing = api_calls.request_listing(client, marketplace_id, asset_id)
    price_list_points = []
    try:
        if listing and listing['pricelist']:
            price_list_version = api_calls.request_price_list(client, listing['pricelist']['id'])
            price_list_points = api_calls.request_price_list_version_points(client, price_list_version['id'])
    except:
        return {}
    return get_financials_from_price_list(price_list_points)

def get_auto_renewal_status(value: str):
    if value == 'active_auto_renewal_status':
        return 'Active'
    elif value == 'inactive_auto_renewal_status':
        return 'Inactive'
    else:
        return 'Empty'

def get_structured_value(value:{}, param:str):
    return value.get('structured_value', {}).get(param, [])

def get_account_subscription_list(value:{}):
    return json.dumps(get_structured_value(value, 'value'))

def get_three_years_commitment(value: {}) -> str:
    return 'Y' if get_structured_value(value, '3 Years commitment') == True else 'N'

def get_three_years_recommitment(value: {}) -> str:
    return 'Y' if get_structured_value(value, '3YR') == True else 'N'


def get_flex_discounts(params: list, item_mpn: str, order_id: str) -> dict:
    """
    Parse the cb_flex_discounts_applied parameter and match discounts for a specific item.

    :type params: list
    :type item_mpn: str
    :type order_id: str
    :param params: asset parameters list
    :param item_mpn: MPN of the item to match
    :param order_id: Adobe Order ID to match
    :return: dict with matched discount fields or '-' if not found
    """
    result = {
        'discounted_mpn': '-',
        'discounted_order_id': '-',
        'discount_id': '-',
        'discount_code': '-',
    }

    try:
        # Find the cb_flex_discounts_applied parameter
        flex_param = None
        for param in params:
            if param.get('id') == 'cb_flex_discounts_applied':
                flex_param = param
                break

        if not flex_param:
            return result

        # For object-type parameters, data is in 'structured_value', not 'value'
        flex_discounts_data = None
        if 'structured_value' in flex_param and flex_param['structured_value']:
            flex_discounts_data = flex_param['structured_value']
        elif 'value' in flex_param and flex_param['value']:
            # Fallback: try parsing from 'value' field if it's a JSON string
            value = flex_param['value']
            if value and value != '-':
                flex_discounts_data = json.loads(value)

        if not flex_discounts_data:
            return result

        # Get discounts array
        discounts = flex_discounts_data.get('discounts', [])

        if not discounts:
            return result

        # Find matching discounts for this item
        matched_mpns = []
        matched_order_ids = []
        matched_discount_ids = []
        matched_discount_codes = []

        for discount in discounts:
            discount_mpn = discount.get('mpn', '')
            discount_order_id = discount.get('order_id', '')

            # Match by MPN and Order ID
            if discount_mpn == item_mpn and discount_order_id == order_id:
                matched_mpns.append(discount_mpn)
                matched_order_ids.append(discount_order_id)
                matched_discount_ids.append(discount.get('id', ''))
                matched_discount_codes.append(discount.get('code', ''))

        # If matches found, concatenate with comma
        if matched_mpns:
            result['discounted_mpn'] = ','.join(matched_mpns)
            result['discounted_order_id'] = ','.join(matched_order_ids)
            result['discount_id'] = ','.join(matched_discount_ids)
            result['discount_code'] = ','.join(matched_discount_codes)

    except (json.JSONDecodeError, TypeError, KeyError, AttributeError):
        # If any error occurs (invalid JSON, wrong structure, etc.), return default values
        pass

    return result


def get_days_between_effective_and_renewal_date(effective_date, renewal_date):
    """
    Calculate the number of days between effective date and renewal date.

    :type effective_date: str
    :type renewal_date: str
    :param effective_date: Effective date in ISO format (e.g., "2020-11-23T12:52:27+00:00")
    :param renewal_date: Renewal date in YYYY-MM-DD format (e.g., "2020-12-01")
    :return: Number of days between the two dates, or '-' if calculation fails
    """
    try:
        # Handle empty or missing values
        if not effective_date or effective_date == '-' or not renewal_date or renewal_date == '-':
            return "-"

        # Normalize the effective_date string (same approach as convert_to_datetime)
        # Remove timezone info and convert T to space for consistent parsing
        normalized_effective = effective_date.replace("T", " ").replace("+00:00", "").strip()

        # Parse the normalized effective date
        effective = datetime.strptime(normalized_effective, "%Y-%m-%d %H:%M:%S")
        effective_ymd = datetime(effective.year, effective.month, effective.day)

        # Parse renewal date
        renewal = datetime.strptime(renewal_date, "%Y-%m-%d")

        return (renewal - effective_ymd).days
    except Exception:
        return "-"
