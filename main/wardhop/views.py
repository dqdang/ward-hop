from django.shortcuts import render
from django.views.generic import TemplateView, View
from wardhop.drafter import ChampionDatabase as ChampionDatabase
import main.settings as settings


cd = ChampionDatabase()


class BasePageView(View):
    template_name = "base.html"
    images = cd.get_all_champ_images()

    def get(self, request):
        all_images = [settings.STATIC_URL + self.images[champ]["full"]
                      for champ in self.images.keys()]
        return render(request, self.template_name, {"images": all_images})


class PickBanView(View):
    draft_template = "pickban.html"
    error_template = "errors.html"
    images = cd.get_all_champ_images()
    blue_ban = ["", "", "", "", ""]
    red_ban = ["", "", "", "", ""]
    blue = ["", "", "", "", ""]
    red = ["", "", "", "", ""]
    rotation = ["blue_ban", "red_ban", "blue_ban", "red_ban", "blue_ban", "red_ban", "blue", "red",
                "red", "blue", "blue", "red", "red_ban", "blue_ban", "red_ban", "blue_ban", "red", "blue", "blue", "red"]

    def get(self, request):
        if self.request.GET.get("clean"):
            print("Cleaning session")
            request.session["rotation_counter"] = 0
            self.blue_ban.clear()
            self.red_ban.clear()
            self.blue.clear()
            self.red.clear()
            self.blue_ban = ["", "", "", "", ""]
            self.red_ban = ["", "", "", "", ""]
            self.blue = ["", "", "", "", ""]
            self.red = ["", "", "", "", ""]
            print("blue_ban:", self.blue_ban)
            print("red_ban:", self.red_ban)
            print("blue:", self.blue)
            print("red:", self.red)
            print("rotation_counter:", request.session["rotation_counter"])
            print("rotation at rotation_counter:",
                  self.rotation[request.session["rotation_counter"]])
        champ = self.request.GET.get("champion")
        try:
            rotation_counter = request.session["rotation_counter"]
        except KeyError:
            request.session["rotation_counter"] = 0
        if request.session["rotation_counter"] >= len(self.rotation):
            request.session["rotation_counter"] = 0
            return render(request, self.draft_template, {"blue_ban": self.blue_ban, "red_ban": self.red_ban, "blue1": self.blue[0], "red1": self.red[0], "blue2": self.blue[1], "red2": self.red[1], "blue3": self.blue[2], "red3": self.red[2], "blue4": self.blue[3], "red4": self.red[3], "blue5": self.blue[4], "red5": self.red[4], "error": ""})
        if champ:
            found = cd.search(champ)
            picked = False
            print("rotation_counter:", request.session["rotation_counter"])
            print("rotation at rotation_counter:",
                  self.rotation[request.session["rotation_counter"]])
            if len(found) > 0:
                for champ in found:
                    if champ in set([char.lower().split(".png")[0].split("/")[-1] for char in self.blue_ban + self.red_ban + self.blue + self.red]):
                        print("Champion already picked")
                        picked = True
                        continue
                    image = cd.get_champ_image(champ)
                    if self.rotation[request.session["rotation_counter"]] == "blue_ban":
                        self.blue_ban = self.replace_empty_space(
                            self.blue_ban, settings.STATIC_URL + image["full"])
                    elif self.rotation[request.session["rotation_counter"]] == "red_ban":
                        self.red_ban = self.replace_empty_space(
                            self.red_ban, settings.STATIC_URL + image["full"])
                    elif self.rotation[request.session["rotation_counter"]] == "blue":
                        self.blue = self.replace_empty_space(
                            self.blue, settings.STATIC_URL + image["full"])
                    elif self.rotation[request.session["rotation_counter"]] == "red":
                        self.red = self.replace_empty_space(
                            self.red, settings.STATIC_URL + image["full"])
                if not picked:
                    request.session["rotation_counter"] += 1
                print("blue_ban:", self.blue_ban)
                print("red_ban:", self.red_ban)
                print("blue:", self.blue)
                print("red:", self.red)
                return render(request, self.draft_template, {"blue_ban": self.blue_ban, "red_ban": self.red_ban, "blue1": self.blue[0], "red1": self.red[0], "blue2": self.blue[1], "red2": self.red[1], "blue3": self.blue[2], "red3": self.red[2], "blue4": self.blue[3], "red4": self.red[3], "blue5": self.blue[4], "red5": self.red[4], "error": ""})
            else:
                error = "Champion not found."
                return render(request, self.draft_template, {"blue_ban": self.blue_ban, "red_ban": self.red_ban, "blue": self.blue, "red": self.red, "error": error})
        else:
            all_images = [settings.STATIC_URL + self.images[champ]["full"]
                          for champ in self.images.keys()]
            return render(request, self.draft_template, {"images": all_images})
        return render(request, self.error_template)

    def replace_empty_space(self, l, key):
        for elem in range(len(l)):
            if l[elem] == "":
                l[elem] = key
                break
        return l


class SearchResultsView(View):
    template_name = "draft.html"
    images = cd.get_all_champ_images()

    def get(self, request):
        all_images = [settings.STATIC_URL + self.images[champ]["full"]
                      for champ in self.images.keys()]
        return render(request, self.template_name, {"images": all_images})
