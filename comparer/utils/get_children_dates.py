def get_children_dates(node):
    if node.get('date'):
        return [node['date']]

    all_children_deep_dates = []
    for child_node in node['children']:
        all_children_deep_dates += get_children_dates(child_node)
    return all_children_deep_dates
