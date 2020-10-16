from django.shortcuts import render
from django.views.generic import TemplateView, View
from wardhop.drafter import ChampionDatabase as ChampionDatabase
import main.settings as settings


cd = ChampionDatabase()


class BasePageView(View):
    template_name = 'base.html'
    images = cd.get_all_champ_images()

    def get(self, request):
        all_images = [settings.STATIC_URL + self.images[champ]['full'] for champ in self.images.keys()]
        return render(request, self.template_name, {"images": all_images})

class SearchResultsView(View):
    draft_template = 'draft.html'
    error_template = "errors.html"

    def get(self, request):
        champ = self.request.GET.get('champion')
        found = cd.search(champ)
        all_images = []
        for champ in found:
            image = cd.get_champ_image(champ)
            all_images.append(settings.STATIC_URL + image['full'])
        if len(found) > 0:
            return render(request, self.draft_template, {"images": all_images})
        return render(request, self.error_template)

class PickBanView(View):
    template_name = 'pickban.html'

    def get(self, request):
        all_images = [settings.STATIC_URL + self.images[champ]['full'] for champ in self.images.keys()]
        return render(request, self.template_name, {"images": all_images})
