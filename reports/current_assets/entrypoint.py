# -*- coding: utf-8 -*-
#
# Copyright (c) 2026, CloudBlue
# All rights reserved.
#

from reports import utils
from reports import api_calls
from reports.requests.entrypoint import EXCLUDED_PRODUCTION_HUB_IDS


def generate(client, parameters, progress_callback, renderer_type=None, extra_context=None, ):
    assets = api_calls.request_current_assets(client, parameters)

    progress = 0
    total = assets.count()
    for asset in assets:
        connection = asset.get('connection') or {}
        if _is_excluded(asset, connection, parameters):
            progress += 1
            progress_callback(progress, total)
            continue

        params = asset.get('params', [])
        tiers = asset.get('tiers', {})
        for item in asset.get('items', []):
            if not _has_quantity(item):
                continue

            yield (
                utils.get_basic_value(asset, 'id'),  # Asset ID
                utils.get_basic_value(asset, 'status'),  # Asset Status
                utils.get_basic_value(asset, 'external_id'),  # End Customer Subscription ID
                utils.get_value(asset, 'product', 'id'),  # Product ID
                utils.get_value(asset, 'product', 'name'),  # Product Name
                utils.get_value(connection, 'provider', 'id'),  # Provider ID
                utils.get_value(connection, 'provider', 'name'),  # Provider Name
                utils.get_hub_id(connection),  # Hub ID
                utils.get_hub_name(connection),  # Hub Name
                utils.get_value(asset, 'marketplace', 'id'),  # Marketplace ID
                utils.get_value(asset, 'marketplace', 'name'),  # Marketplace Name
                utils.get_basic_value(connection, 'type'),  # Connection Type
                utils.get_value(tiers, 'tier1', 'id'),  # Reseller ID
                utils.get_value(tiers, 'tier1', 'external_id'),  # Reseller External ID
                utils.get_value(tiers, 'tier1', 'name'),  # Reseller Name
                utils.get_value(tiers, 'customer', 'id'),  # Customer ID
                utils.get_value(tiers, 'customer', 'external_id'),  # Customer External ID
                utils.get_value(tiers, 'customer', 'name'),  # Customer Name
                utils.convert_to_datetime(
                    utils.get_value(asset.get('events', {}), 'created', 'at'),  # Created At
                ),
                utils.get_param_value(params, 'adobe_customer_id'),  # Adobe Customer ID
                utils.get_param_value(params, 'adobe_vip_number'),  # Adobe VIP Number
                utils.get_param_value(params, 'adobe_user_email'),  # Adobe User Email
                utils.get_param_value(params, 'discount_group'),  # Discount Group Licenses
                utils.get_param_value(params, 'discount_group_consumables'),  # Discount Group Cons.
                utils.get_param_value(params, 'renewal_date'),  # Renewal Date
                utils.get_param_value(params, 'auto_renewal_status'),  # Auto Renewal Status
                utils.get_param_value(params, 'commitment_status'),  # 3YC Status
                utils.get_param_value(params, 'commitment_start_date'),  # 3YC Start Date
                utils.get_param_value(params, 'commitment_end_date'),  # 3YC End Date
                utils.get_param_value(params, 'recommitment_status'),  # 3YC Recommitment Status
                utils.get_param_value(params, 'external_reference_id'),  # External Reference ID
                utils.get_basic_value(item, 'display_name'),  # Item Name
                utils.get_basic_value(item, 'mpn'),  # MPN
                utils.get_basic_value(item, 'quantity'),  # Current Quantity
                utils.get_basic_value(item, 'type'),  # Unit of Measure
                utils.get_basic_value(item, 'item_type'),  # Item Type
                utils.get_basic_value(item, 'period'),  # Billing Period
                utils.today_str(),  # Exported At
            )
        progress += 1
        progress_callback(progress, total)


def _is_excluded(asset, connection, parameters):
    conn_type = utils.get_basic_value(connection, 'type')
    if conn_type == 'production' and utils.get_hub_id(connection) in EXCLUDED_PRODUCTION_HUB_IDS:
        return True
    if parameters.get('commitment_status') == '3yc':
        commitment = utils.get_param_value(asset.get('params', []), 'commitment_status')
        if commitment == '-' or commitment == '':
            return True
    return False


def _has_quantity(item):
    try:
        return float(item.get('quantity') or 0) != 0
    except (TypeError, ValueError):
        return True
