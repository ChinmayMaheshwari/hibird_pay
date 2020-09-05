from django import template

register = template.Library()

@register.filter(name='batch')
def batch(iterable, n=4):
    l = len(iterable)
    for ndx in range(0, l):
        yield iterable[ndx:min(ndx + n, l)]
