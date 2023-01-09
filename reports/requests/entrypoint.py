# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, Carolina Giménez Escalante
# All rights reserved.
#

from reports import utils
from reports import api_calls


def generate(client, parameters, progress_callback, renderer_type=None, extra_context=None, ):
    requests = api_calls.request_approved_requests(client, parameters)

    progress = 0
    total = requests.count()
    for request in requests:
        order_number = ''
        transfer_number = ''
        vip_number = ''
        adobe_cloud_program_id = ''
        pricing_level = ''
        action = ''
        adobe_user_email = ''

        # get subscription parameters values
        parameters_list = request['asset']['params']
        vip_number = utils.get_param_value(parameters_list, 'adobe_vip_number')
        order_number = utils.get_param_value(parameters_list, 'adobe_order_id')
        transfer_number = utils.get_param_value(parameters_list, 'transfer_id')
        action = utils.get_param_value(parameters_list, 'action_type')
        adobe_user_email = utils.get_param_value(parameters_list, 'adobe_user_email')
        adobe_cloud_program_id = utils.get_param_value(parameters_list, 'adobe_customer_id')
        pricing_level = utils.get_discount_level(utils.get_param_value(parameters_list, 'discount_group'))

        # get currency from configuration params
        currency = utils.get_param_value(request['asset']['configuration']['params'], 'Adobe_Currency')

        financials = utils.get_financials_from_product_per_marketplace(
            client, request['asset']['marketplace']['id'], request['asset']['product']['id'])

        subscription = api_calls.request_asset(client, request['asset']['id'])  # request for anniversary date
        for item in request['asset']['items']:
            if (utils.get_basic_value(item, 'item_type') == 'PPU'
                    or utils.get_basic_value(item, 'quantity') == '0'):
                continue
            else:
                delta = 0
                delta_str = ''
                if len(item['quantity']) > 0 and len(item['old_quantity']) > 0:
                    try:
                        delta = float(item['quantity']) - float(item['old_quantity'])
                    except Exception:
                        delta_str = item['quantity'] + ' - ' + item['old_quantity']
                if delta_str == '' and delta > 0:
                    delta_str = "+" + str(delta)
                if delta_str == '' and delta < 0:
                    delta_str = "-" + str(delta)
                yield (
                    utils.get_basic_value(request, 'id'),  # Request ID
                    utils.get_value(request, 'asset', 'id'),  # Connect Subscription ID
                    utils.get_value(request, 'asset', 'external_id'),  # End Customer Subscription ID
                    action,  # Type of Purchase
                    order_number,  # Adobe Order #
                    transfer_number,  # Adobe Transfer ID #
                    vip_number,  # VIP #
                    adobe_cloud_program_id,  # Adobe Cloud Program ID
                    pricing_level,  # Pricing SKU Level (Volume Discount level)
                    utils.get_basic_value(item, 'display_name'),  # Product Description
                    utils.get_basic_value(item, 'mpn'),  # Part Number
                    utils.get_basic_value(item, 'period'),  # Product Period
                    utils.get_basic_value(item, 'quantity'),  # Cumulative Seat
                    delta_str,  # Order Delta
                    utils.get_value(request['asset']['tiers'], 'tier1', 'id'),  # Reseller ID
                    utils.get_value(request['asset']['tiers'], 'tier1', 'name'),  # Reseller Name
                    utils.get_value(request['asset']['tiers'], 'customer', 'name'),  # End Customer Name
                    utils.get_value(request['asset']['tiers'], 'customer', 'external_id'),  # End Customer External ID
                    utils.get_value(request['asset']['connection'], 'provider', 'id'),  # Provider ID
                    utils.get_value(request['asset']['connection'], 'provider', 'name'),  # Provider Name
                    utils.get_value(request, 'marketplace', 'name'),  # Marketplace
                    utils.get_value(request['asset'], 'product', 'id'),  # Product ID
                    utils.get_value(request['asset'], 'product', 'name'),  # Product Name
                    utils.get_value(request, 'asset', 'status'),  # Subscription Status
                    utils.get_value(subscription, 'billing', 'next_date'),  # Anniversary Date
                    utils.convert_to_datetime(
                        utils.get_basic_value(request, 'effective_date'),  # Effective  Date
                    ),
                    utils.convert_to_datetime(
                        utils.get_basic_value(request, 'created'),  # Creation  Date
                    ),
                    utils.get_basic_value(request, 'type'),  # Transaction Type
                    adobe_user_email,  # Adobe User Email
                    currency,  # Currency
                    utils.get_value(financials, item['global_id'], 'cost'),  # Cost
                    utils.get_value(financials, item['global_id'], 'reseller_cost'),  # Reseller Cost
                    utils.get_value(financials, item['global_id'], 'msrp'),  # MSRP
                    utils.get_basic_value(request['asset']['connection'], 'type'),  # Connection Type,
                    utils.today_str(),  # Exported At
                )
        progress += 1
        progress_callback(progress, total)
