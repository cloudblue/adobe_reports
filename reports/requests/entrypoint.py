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
        # get subscription parameters values
        parameters_list = request['asset']['params']
        vip_number = utils.get_param_value(parameters_list, 'adobe_vip_number')
        order_number = utils.get_param_value(parameters_list, 'adobe_order_id')
        transfer_number = utils.get_param_value(parameters_list, 'transfer_id')
        action = utils.get_param_value(parameters_list, 'action_type')
        adobe_user_email = utils.get_param_value(parameters_list, 'adobe_user_email')
        adobe_cloud_program_id = utils.get_param_value(parameters_list, 'adobe_customer_id')
        discount_group = utils.get_param_value(parameters_list, 'discount_group')
        discount_group_consumables = utils.get_param_value(parameters_list, 'discount_group_consumables')
        pricing_level = utils.get_discount_level(discount_group)
        commitment = utils.get_param_value(parameters_list, 'commitment_status')
        commitment_start_date = utils.get_param_value(parameters_list, 'commitment_start_date')
        commitment_end_date = utils.get_param_value(parameters_list, 'commitment_end_date')
        recommitment = utils.get_param_value(parameters_list, 'recommitment_status')
        recommitment_start_date = utils.get_param_value(parameters_list, 'recommitment_start_date')
        recommitment_end_date = utils.get_param_value(parameters_list, 'recommitment_end_date')
        external_reference_id = utils.get_param_value(parameters_list, 'external_reference_id')
        renewal_date = utils.get_param_value(parameters_list, 'renewal_date')
        effective_date = utils.get_basic_value(request, 'effective_date')
        prorata_days = utils.get_days_between_effective_and_renewal_date(effective_date, renewal_date)

        # get currency from configuration params
        currency = utils.get_param_value(request['asset']['configuration']['params'], 'Adobe_Currency')

        financials = utils.get_financials_from_product_per_marketplace(
            client, request['asset']['marketplace']['id'], request['asset']['product']['id'])

        subscription = api_calls.request_asset(client, request['asset']['id'])  # request for anniversary date
        for item in request['asset']['items']:
            delta_str = _get_delta_str(item)
            if delta_str == '':
                continue
            
            # Get flex discounts for this item
            item_mpn = utils.get_basic_value(item, 'mpn')
            item_type = utils.get_basic_value(item, 'type')
            flex_discounts = utils.get_flex_discounts(parameters_list, item_mpn, order_number)
            
            yield (
                utils.get_basic_value(request, 'id'),  # Request ID
                utils.get_value(request, 'assignee', 'id'),  # Assignee ID
                utils.get_value(request, 'assignee', 'name'),  # Assignee Name
                utils.get_value(request, 'asset', 'id'),  # Connect Subscription ID
                utils.get_value(request, 'asset', 'external_id'),  # End Customer Subscription ID
                action,  # Action
                order_number,  # Adobe Order #
                transfer_number,  # Adobe Transfer ID #
                vip_number,  # VIP #
                adobe_cloud_program_id,  # Adobe Cloud Program ID
                pricing_level,  # Pricing SKU Level (Volume Discount level)
                discount_group,  # Discount Group Licenses
                discount_group_consumables,  # Discount Group Consumables
                utils.get_basic_value(item, 'display_name'),  # Product Description
                item_mpn,  # Part Number
                item_type,  # Unit of Measure
                utils.get_basic_value(item, 'period'),  # Product Period
                utils.get_basic_value(item, 'quantity'),  # Cumulative Seat
                delta_str,  # Order Delta
                flex_discounts['discounted_mpn'],  # Discounted MPN
                flex_discounts['discounted_order_id'],  # Discounted Adobe Order Id
                flex_discounts['discount_id'],  # Adobe Discount Id
                flex_discounts['discount_code'],  # Adobe Discount Code
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
                utils.convert_to_datetime(
                    utils.get_value(subscription, 'billing', 'next_date'),  # Anniversary Date
                ),
                renewal_date,  # Adobe Renewal Date
                utils.convert_to_datetime(
                    effective_date,  # Effective Date
                ),
                prorata_days,  # Prorata (days)
                utils.convert_to_datetime(
                    utils.get_basic_value(request, 'created'),  # Creation Date
                ),
                utils.get_basic_value(request, 'type'),  # Connect Order Type
                adobe_user_email,  # Adobe User Email
                currency,  # Currency
                utils.get_value(financials, item['global_id'], 'cost'),  # Cost
                utils.get_value(financials, item['global_id'], 'reseller_cost'),  # Reseller Cost
                utils.get_value(financials, item['global_id'], 'msrp'),  # MSRP
                utils.get_basic_value(request['asset']['connection'], 'type'),  # Connection Type
                utils.today_str(),  # Exported At
                commitment,  # commitment
                commitment_start_date,  # commitment start date
                commitment_end_date,  # commitment end date
                recommitment,  # recommitment
                recommitment_start_date,  # recommitment start date
                recommitment_end_date,  # recommitment end date
                external_reference_id,  # external reference id
            )
        progress += 1
        progress_callback(progress, total)


def _get_delta_str(item):
    if (utils.get_basic_value(item, 'item_type') != 'PPU'
        and (utils.get_basic_value(item, 'quantity') != '0'
            or utils.get_basic_value(item, 'old_quantity') != '0')
    ):
        delta = 0
        delta_str = '-'
        if len(item['quantity']) > 0 and len(item['old_quantity']) > 0:
            try:
                delta = float(item['quantity']) - float(item['old_quantity'])
            except Exception:
                delta_str = item['quantity'] + ' - ' + item['old_quantity']
        if delta_str == '-' and delta > 0:
            delta_str = "+" + str(delta)
        if delta_str == '-' and delta < 0:
            delta_str = str(delta)
        return delta_str
    return ''
