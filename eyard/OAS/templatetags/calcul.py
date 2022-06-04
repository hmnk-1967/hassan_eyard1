from django import template

register = template.Library()


@register.filter(name='sum')
def sum(value):
    return int(value)*100
