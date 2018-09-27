#!/usr/local/bin/python
# coding: utf-8

from django.db import models

from datetime import datetime
from django.template.defaultfilters import slugify
#from django.core.urlresolvers import reverse
from django.urls import reverse
from django.utils.translation import ugettext as _
from mptt.fields import TreeForeignKey
from mptt.managers import TreeManager
from mptt.models import MPTTModel
try:
    from klingon.models import Translatable
except:
    pass

class PageManager(TreeManager):
    use_for_related_fields = True

    def public(self):
        return super(PageManager, self).filter(is_public=True) 

    def public_root_nodes(self):
        return super(PageManager, self).root_nodes().filter(is_public=True)


class Page(MPTTModel):
    title = models.CharField(max_length=100, blank=False, verbose_name=_('title'), 
        help_text=_('Page title'))
    slug = models.CharField(_(u'slug'), max_length=150, blank=True)
    is_public = models.BooleanField(
        _('is public'),
        default=True,
        help_text=_('Only public albums will be displayed in the default views.')
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        verbose_name=_('parent page'),
        related_name='children',
        on_delete=models.CASCADE,
    )
    url = models.CharField(_(u'url'), max_length=150, blank=True)
    description = models.TextField(_('description'), blank=True)
    date_added = models.DateTimeField(_('date added'), auto_now_add=True)
    
    objects = PageManager()
    
    def __unicode__(self):
        return '{0} ({1})'.format(self.title, self.slug)

    def __str__(self):
        return '{0} ({1})'.format(self.title, self.slug)

    def save(self, *args, **kwargs):
        # Raise on circular reference
        #parent = self.parent
        #while parent is not None:
        #    if parent == self:
        #        raise RuntimeError, "Circular references not allowed"
        #    parent = parent.parent

        super(Page, self).save(*args, **kwargs)
    
    def get_page_tree(self):
        tree = [self.slug]
        if self.parent:
            tree = self.parent.get_page_tree() + tree
        return tree

    @property
    def children(self):
        return self.page_set.all().order_by('title')

    def get_absolute_url(self):
        return reverse('page_object_list', kwargs={'page_slug': self.slug})

class BlockManager(models.Manager):
    use_for_related_fields = True

    def public(self):
        return super(BlockManager, self).filter(moderated=True)

#class Block(models.Model, Translatable):
class Block(models.Model):
    page = models.ForeignKey('Page', 
                on_delete=models.CASCADE)
    slug = models.CharField(_(u'slug'), max_length=150, blank=True)
    published_on = models.DateField(_('date de publication'), blank=True, null=True)
    created_on = models.DateTimeField(_('date added'), auto_now_add=True)
    moderated = models.BooleanField(verbose_name=_('moderated'), default=False)
    page = TreeForeignKey(
        Page,
        verbose_name=_('page'),
        related_name='pages',
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=100, blank=False, verbose_name=_('name'), 
            help_text=_('Block name'))
    body = models.TextField(blank=False, verbose_name=_('content'))
    #translatable_fields = ('name', 'body')
    objects = BlockManager()

    class Meta:
        ordering = ['-created_on']
        verbose_name = _('block')
        verbose_name_plural = _('blocks')
        
    def save(self):
        if not self.created_on:
            self.created_on = datetime.now()
        if not self.moderated:
            self.moderated = False
        if not self.slug:
            self.slug = slugify(self.name)
        super(Block, self).save()

    def get_last_media(self):
        try:
            attachment = BlockMedia.objects.get(block=self, header=True)
        except:
            attachment = BlockMedia.objects.filter(block=self).last()
        return attachment

    def get_media(self):
        attachment = BlockMedia.objects.filter(block=self)
        return attachment

    def __unicode__(self):
        return self.page.title + ' ' + self.name + ' ' + self.created_on.strftime('%d/%m/%Y')

    def __str__(self):
        return self.page.title + ' ' + self.name + ' ' + self.created_on.strftime('%d/%m/%Y')

class BlockMedia(models.Model):
    block = models.ForeignKey('Block', null=True, blank=True, on_delete=models.CASCADE)
    attachment = models.FileField('File', upload_to='files/pagers/', blank=True, null=True)
    caption = models.CharField(max_length=100, blank=True, verbose_name=_('caption')) 
    header = models.BooleanField(verbose_name=_('image principale'), default=False)
    created_on = models.DateTimeField(_('date added'), auto_now_add=True)
     
    def save(self):
        if not self.created_on:
            self.created_on = datetime.now()
        super(BlockMedia, self).save()
        
    def __unicode__(self):
        return str(self.attachment) + ' ' + self.created_on.strftime('%d/%m/%Y')

    def __str__(self):
        return str(self.attachment) + ' ' + self.created_on.strftime('%d/%m/%Y')

    def show_url(self):
        if self.attachment:
            return '<a href="/static/%s" target="_blank">Voir l\'image</a>' % (self.attachment)
        else:
            return u'Pas d\image'
    show_url.allow_tags = True

    def show_attachment(self):
        if self.attachment:
            return '<img src="/static/'+str(self.attachment)+'" width=50% />'
        else:
            return '<img src="/static/" width=50% />'
    show_attachment.allow_tags = True

    class Meta:
        ordering = ['-created_on']
        verbose_name = _('media')
        verbose_name_plural = _('medias')
