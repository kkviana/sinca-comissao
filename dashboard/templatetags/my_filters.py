from django import template

register = template.Library()

@register.filter(name='groupby')
def groupby(value, arg):
    """
    Group a list of dictionaries by a given key.
    """
    groups = {}
    for item in value:
        key = item.get(arg)
        if key not in groups:
            groups[key] = []
        groups[key].append(item)
    return groups
