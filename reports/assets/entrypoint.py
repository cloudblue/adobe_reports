# -*- coding: utf-8 -*-
#
# Copyright (c) 2022, Carlos Anuarbe
# All rights reserved.

from reports import api_calls
from reports import utils

asset_headers = [
    'id', 'status', 'created-at', 'external_id', 'product-id', 'provider-id', 'provider-name', 'marketplace-id',
    'marketplace-name', 'contract-id', 'contract-name', 'reseller-id', 'reseller-external_id', 'reseller-name',
    'customer-id', 'customer-external_id', 'customer-name'
]

asset_params_headers = [
    'seamless_move', 'discount_group', 'action_type', 'renewal_date', 'purchase_type', 'adobe_customer_id',
    'adobe_vip_number', 'adobe_user_email'
]

marketplace_headers = [
    'currency', 'cost', 'reseller_cost', 'msrp', 'seats', 'USD-cost', 'USD-msrp',
    'USD-reseller_cost'
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
    headers = asset_headers + asset_params_headers + marketplace_headers

    if renderer_type == 'xlsx':
        yield headers

    total = assets.count()
    counter = 0
    if total == 0:
        yield 'Empty assets'
    for asset in assets:
        marketplace_params = utils.get_marketplace_params(client, asset)
        if not marketplace_params:
            marketplace_params = dict.fromkeys(marketplace_headers)
        # assets need to be in a list to yield
        yield utils.process_line(asset, asset_headers, asset_params_headers, marketplace_params)
        counter += 1
        progress_callback(counter, total)
