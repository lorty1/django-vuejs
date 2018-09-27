#!/usr/local/bin/python
# coding: utf-8

from django import template
from django.template.defaultfilters import safe
from django.utils.safestring import mark_safe
from django.utils import translation
from ..models import Page, Block, BlockMedia

register = template.Library()

lorem = 'Lorem ipsum dolor sit amet, consectetur \
     adipiscing elit. Phasellus at tempor dui. Nullam ligula metus,\
      bibendum non interdum at, bibendum eget mauris. Integer maximus \
      urna id ex egestas blandit. Vivamus ut vulputate felis. \
      Maecenas dictum molestie nisi, efficitur vestibulum nunc pretium \
      sit amet. In hac habitasse platea dictumst. Proin dictum nulla \
      eget nibh consectetur tincidunt. Maecenas vitae lorem sed dolor \
      rhoncus luctus. Nam leo tellus, convallis quis ex vel, tempor blandit \
      nulla. Curabitur porttitor sapien lorem, sit amet mollis lacus ultrices sed.'

@register.simple_tag()
def show_block_title(block_slug):
    """ Utilisation simple :
    Syntax ::
    {% load pager %}
    {% show_block_title 'block_slug' %}
    """
    result = 'Lorem ipsum dolor sit amet' 
    try:
        block = Block.objects.get(slug=block_slug)
        ln = translation.get_language()
        print(ln)
        if ln != "fr":
            try:
                block = block.translations.get_by_lang(ln)
            except:
                block = Block.objects.get(slug=block_slug)
        result = block.name
    except:
        pass
    return safe("%s" % result)

@register.simple_tag()
def show_block_content(block_slug):
    """ Utilisation simple :
    Syntax ::
    {% load pager %}
    {% show_block_content 'block_slug' %}
    """
    result = lorem 
    try:
        block = Block.objects.get(slug=block_slug)
        ln = translation.get_language()
        if ln != "fr":
            try:
                block = block.translations.get_by_lang(ln)
            except:
                block = Block.objects.get(slug=block_slug)
        result = block.body
    except:
        pass
    return safe("%s" % result)

@register.simple_tag()
def show_block_extra_content(block_slug):
    """ Utilisation simple :
    Syntax ::
    {% load pager %}
    {% show_block_extra_content 'block_slug' %}
    """
    result = lorem
    try:
        block = Block.objects.get(slug=block_slug)
        ln = translation.get_language()
        if ln != "fr":
            block = block.translations.get_by_lang(ln)
        result = block.extra_content
    except:
        pass
    return safe("%s" % result)

@register.simple_tag()
def show_block_image(block_slug, order):
    """ Utilisation simple :
    Syntax ::
    {% load pager %}
    {% show_block_content 'block_slug' %}
    """
    result = 'pager/images/default.png'
    result_title = 'Lorem Ipsum'
    block = BlockMedia.objects.filter(block__slug=block_slug)
    result = block[int(order)].attachment
    result_title = block[int(order)].caption
    return safe("<img src='/static/%s' alt='%s' />" % (result, result_title))

@register.simple_tag()
def show_block_image_url(block_slug, order):
    """ Utilisation simple :
    Syntax ::
    {% load pager %}
    {% show_block_content 'block_slug' %}
    """
    result = 'pager/images/default.png'
    result_title = 'Lorem Ipsum'
    block = BlockMedia.objects.filter(block__slug=block_slug)
    result = block[int(order)].attachment
    result_title = block[int(order)].caption
    return "/static/%s" % (result)

@register.simple_tag()
def show_block_file_url(block_slug, order):
    """ Utilisation simple :
    Syntax ::
    {% load pager %}
    {% show_block_file_url 'block_slug' %}
    """
    result = 'pager/images/default.png'
    result_title = 'Lorem Ipsum'
    try:
        block = BlockMedia.objects.filter(block__slug=block_slug)
        result = block[int(order)].attachment
        result_title = block[int(order)].caption
    except:
        pass
    return "/static/%s" % (result)
