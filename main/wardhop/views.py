from django.shortcuts import render
from django.views.generic import TemplateView, View
from wardhop.drafter import ChampionDatabase as ChampionDatabase


cd = ChampionDatabase()


class BasePageView(TemplateView):
    template_name = 'base.html'


class SearchResultsView(View):
    draft_template = 'draft.html'
    error_template = "errors.html"

    def get(self, request):
        champions = cd.get_all_champ_data()
        champ = self.request.GET.get('champion')
        found = cd.search(champ)
        if len(found) > 0:
            return render(request, self.draft_template, {"champions": found})
        return render(request, self.error_template)
