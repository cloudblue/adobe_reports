
from connect.client import R
import requests


def request_assets(client, input_data) -> list:
    rql = R().events.created.at.ge(input_data['date']['after'])
    rql &= R().events.created.at.le(input_data['date']['before'])
    rql &= R().product.id.oneof(input_data['product']['choices'])
    if input_data['status'] != "all":
        rql &= R().status.eq(input_data['status'])
    return client('subscriptions').assets.filter(rql).all()


def request_listing(client, marketplace_id, product_id) -> dict:
    rql = R()
    rql &= R().marketplace.id.eq(marketplace_id)
    rql &= R().product.id.eq(product_id)
    rql &= R().status.eq('listed')
    return client.listings.filter(rql).first()


def request_price_list(client, price_list_id) -> dict:
    rql = R()
    rql &= R().pricelist.id.eq(price_list_id)
    rql &= R().status.eq('active')
    return client('pricing').versions.filter(rql).first()


def request_price_list_version_points(client, price_list_version_id) -> list:
    rql = R()
    rql &= R().status.eq('filled')
    return client('pricing').versions[price_list_version_id].points.filter(rql).all()


def request_get(url):
    res = requests.models.Response
    res.status_code = 0
    try:
        res = requests.get(url)
    except requests.exceptions.RequestException as e:
        print(e)
    return res
