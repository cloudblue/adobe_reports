# -*- coding: utf-8 -*-
#
# Copyright (c) 2022, Carlos Anuarbe
# All rights reserved.
#

from reports.assets.entrypoint import generate


def test_assets_report(
    asset,
    progress,
    sync_client_factory,
    response_factory,
    extra_context_callback,
):

    responses = []
    # create a response for a count call

    responses.append(response_factory(count=2))

    # create response for a collection

    responses.append(
        response_factory(
            query='and(ge(events.created.at,2021-01-01T00:00:00),le(events.created.at,2021-12-01T00:00:00),'
                  'in(product.id,(PRD-207-752-513)),eq(status,active))',
            value=[asset],
        ),
    )

    # create a response that raises an Exception

    # responses.append(response_factory(exception=Exception('my_exception')))

    # create a response that returns a http 404

    # responses.append(response_factory(status=404))

    # create a response and pass an RQL query, ordering and select
    # to check that it match

    responses.append(response_factory(
        query='and(eq(marketplace.id,MP-91673),eq(product.id,PRD-276-377-545),eq(status,listed))',
        value=[],
    ))

    # create a client instance

    client = sync_client_factory(responses)

    # input_data

    parameters = {
        "date": {
            "after": "2021-01-01T00:00:00",
            "before": "2021-12-01T00:00:00",
        },
        "product": {
            "all": False,
            "choices": ['PRD-207-752-513'],
        },
        "status": 'active',
        "connexion_type": {
            "all": False,
            "choices": ["preview"],
        },
    }
    result = list(generate(client, parameters, progress))

    assert len(result) == 2
