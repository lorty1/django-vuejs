# -*- coding: utf-8 -*-

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext as _

class BlocksApphook(CMSApp):
    name = _('blocks')
    urls = ["blocks.urls"]

apphook_pool.register(BlocksApphook)
