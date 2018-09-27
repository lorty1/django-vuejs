# top-level views for the project, which don't belong in any specific app

from django.views.generic.base import TemplateView


#def custom_proc(request):
#    "A context processor that provides 'articles'"
#    
#    try: 
#        articles = Article.objects.all()[:4]    
#    except:
#        articles = ''
#    
#    return {
#        'articles': articles,
#    }

class HomePage(TemplateView):

    template_name = "index.html"

class AboutPage(TemplateView):

    template_name = "static.html"
    def get_context_data(self, **kwargs):
        context = super(AboutPage, self).get_context_data(**kwargs)
        return context

class LegalsPage(TemplateView):

    template_name = "static.html"
    def get_context_data(self, **kwargs):
        context = super(LegalsPage, self).get_context_data(**kwargs)
        return context
