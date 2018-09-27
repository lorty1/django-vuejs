from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.generic import DetailView, ListView
from django.views.generic.base import TemplateView
from django import template
from .models import Page, Block

class PageList(ListView):
	
	template_name = "pager/page_list.html"
	model = Page

	def get_context_data(self, **kwargs):
		context = super(PageList, self).get_context_data(**kwargs)
		# Permet de retourner tous les objets du model Oeuvre

		return context


class PageDetail(DetailView):
	
	template_name = "pager/page_detail.html"
	model = Page

	def get_context_data(self, **kwargs):
		context = super(PageDetail, self).get_context_data(**kwargs)
		# Permet de retourner tous les objets du model Oeuvre
		context['blocks'] = Block.objects.filter(page__slug=self.kwargs['slug']).filter(moderated=True)

		return context
