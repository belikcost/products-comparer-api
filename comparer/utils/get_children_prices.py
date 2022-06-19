from comparer.db.schema import ShopUnitType


def get_children_prices(node):
    if ShopUnitType(node['type']).value == ShopUnitType.offer.value:
        return [node['price']]

    all_children_deep_prices = []
    for child_node in node['children']:
        all_children_deep_prices += get_children_prices(child_node)
    return all_children_deep_prices
