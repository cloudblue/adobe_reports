# -*- coding: utf-8 -*-
#
# Copyright (c) 2022, Carlos Anuarbe
# All rights reserved.

from reports import api_calls
from reports import utils

asset_headers = [
    'id', 'status', 'external_id', 'product-id', 'provider-id', 'provider-name', 'marketplace-id',
    'marketplace-name', 'contract-id', 'contract-name', 'reseller-id', 'reseller-external_id', 'reseller-name',
    'created-at', 'customer-id', 'customer-external_id', 'customer-name'
]

asset_params_headers = [
    'external_reference_id', 'seamless_move',  'auto_renewal_status', 'discount_group', 'discount_group_consumables',
    'action_type', 'renewal_date', 'purchase_type', 'adobe_customer_id', 'adobe_vip_number', 'adobe_user_email',
    'cb_adobe_account_subscription_list', 'three_years_commitment', 'commitment_status', 'three_years_minimum_licenses',
    'three_years_minimum_consumables', 'commitment_start_date', 'commitment_end_date', 'three_years_recommitment',
    'three_years_recommitment_minimum_licenses', 'three_years_recommitment_minimum_consumables','recommitment_status',
    'recommitment_start_date', 'recommitment_end_date',
]


def generate(
        client=None,
        input_data=None,
        progress_callback=None,
        renderer_type='xlsx',
        extra_context_callback=None
):
    """
    Extracts data from Connect using the ConnectClient instance
    and input data provided as arguments, applies
    required transformations (if any) and returns the data rendered
    by the given renderer on the arguments list.
    Some renderers may require extra context data to generate the report
    output, for example in the case of the Jinja2 renderer...

    :param client: An instance of the CloudBlue Connect
                    client.
    :type client: cnct.ConnectClient
    :param input_data: Input data used to calculate the
                        resulting dataset.
    :type input_data: dict
    :param progress_callback: A function that accepts t
                                argument of type int that must
                                be invoked to notify the progress
                                of the report generation.
    :type progress_callback: func
    :param renderer_type: Renderer required for generating report
                            output.
    :type renderer_type: string
    :param extra_context_callback: Extra content required by some
                            renderers.
    :type extra_context_callback: func
    """

    assets = api_calls.request_assets(client, input_data)
    total = assets.count()

    counter = 0
    if total == 0:
        yield 'EMPTY ASSETS'
    for asset in assets:
        # assets need to be in a list to yield
        if "commitment_status" in input_data and input_data['commitment_status'] == '3yc':
            print(asset['id'])
            print(utils.get_param_value_by_name(asset['params'], 'commitment_status'))
            if utils.get_param_value_by_name(asset['params'], 'commitment_status') == '-' \
                    or utils.get_param_value_by_name(asset['params'], 'commitment_status') == '':
                counter += 1
                progress_callback(counter, total)
                continue

        yield _process_line(asset)
        counter += 1
        progress_callback(counter, total)


def _process_line(asset: dict) -> list:
    """
    This functions uses several functions on this file to build a line with values to yield at xlsx file

    :param asset: one asset from requested assets
    :return: list with line values
    """
    asset_values = utils.process_asset_headers(asset, asset_headers)
    asset_values.update(utils.process_asset_parameters_by_name(asset['params'], asset_params_headers))

    if not asset_values['renewal_date']:
        asset_values['renewal_date'] = str(utils.handle_renewal_date(asset_values['created-at']))

    # purchase type and seats come from the asset items, no price list needed
    items_summary = utils.get_financials_and_seats(asset['items'], {})
    asset_values['purchase_type'] = items_summary['purchase_type']
    asset_values['seats'] = items_summary['seats']
    return list(asset_values.values())
