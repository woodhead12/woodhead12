from django.shortcuts import reverse
from django.template import Library
from web import models

register = Library()


@register.simple_tag
def get_format_number(num):
    num_string = str(num)
    new_string = num_string.rjust(3, '0')
    return '#{}'.format(new_string)
