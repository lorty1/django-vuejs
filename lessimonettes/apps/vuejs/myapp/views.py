# Create your views here.
from django.template import RequestContext
from django.views.generic.base import TemplateView
from django.template.response import TemplateResponse

class VueView(TemplateView):

  template_name = "indexVue.html"

  def get_context_data(self, **kwargs):
    context = super(VueView, self).get_context_data(**kwargs)
    return context
