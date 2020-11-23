from django.shortcuts import render
from django.views.generic import TemplateView, View
from wardhop.drafter import ChampionDatabase as ChampionDatabase
import main.settings as settings
import hashlib
import time


cd = ChampionDatabase()


class BasePageView(View):
    template_name = "base.html"
    images = cd.get_all_champ_images()

    def get(self, request):
        # Some browsers do not have a session id in cookies. Use time for now.
        try:
            id = request.COOKIES.get('sessionid') + str(time.time())
        except TypeError:
            id = str(time.time())
        lobby = hashlib.sha224(id.encode('utf-8')).hexdigest()[0:8]
        all_images = [settings.STATIC_URL + self.images[champ]["full"]
                      for champ in self.images.keys()]
        request.session["blue_ban"] = ["/static/Placeholder.png" for _ in range(6)]
        request.session["red_ban"] = ["/static/Placeholder.png" for _ in range(6)]
        request.session["blue"] = ["/static/Placeholder.png" for _ in range(6)]
        request.session["red"] = ["/static/Placeholder.png" for _ in range(6)]
        request.session["lobby"] = lobby
        return render(request, self.template_name, {"lobby": lobby, "images": all_images})


class PickBanView(View):
    draft_template = "pickban.html"
    error_template = "errors.html"
    images = cd.get_all_champ_images()
    rotation = ["blue_ban", "red_ban", "blue_ban", "red_ban", "blue_ban", "red_ban", "blue", "red",
                "red", "blue", "blue", "red", "red_ban", "blue_ban", "red_ban", "blue_ban", "red", "blue", "blue", "red"]

    def get(self, request):
        lobby, blue_ban, red_ban, blue, red = self.get_session(request)
        return render(request, self.draft_template, self.get_html_elems(lobby, blue_ban, red_ban, blue, red, ""))

    def post(self, request):
        lobby, blue_ban, red_ban, blue, red = self.get_session(request)

        # New draft request handler
        if request.POST.get("clean"):
            lobby = self.clean_cookies(request, lobby)
            lobby, blue_ban, red_ban, blue, red = self.get_session(request)
            return render(request, self.draft_template, self.get_html_elems(lobby, blue_ban, red_ban, blue, red, ""))

        # Initialize rotation counter; KeyError indicates first of session
        try:
            rotation_counter = request.session["rotation_counter"]
        except KeyError:
            request.session["rotation_counter"] = 0

        # Once the draft ends, reset the counter back to 0 to avoid index out of range for rotation array. Draft results are not altered per ``replace_placeholder`` function
        if request.session["rotation_counter"] >= len(self.rotation):
            request.session["rotation_counter"] = 0
            return render(request, self.draft_template, self.get_html_elems(lobby, blue_ban, red_ban, blue, red, ""))

        # Handle champion selection
        champ = request.POST.get("champion")
        if champ:
            found = cd.search(champ)
            if len(found) > 0:
                lobby, blue_ban, red_ban, blue, red = self.handle_champ_selection(
                    request, found, blue_ban, red_ban, blue, red)
                return render(request, self.draft_template, self.get_html_elems(lobby, blue_ban, red_ban, blue, red, ""))
            else:
                error = "Champion not found."
                return render(request, self.draft_template, self.get_html_elems(lobby, blue_ban, red_ban, blue, red, error))
        else:
            return render(request, self.draft_template, self.get_html_elems(lobby, blue_ban, red_ban, blue, red, ""))
        return render(request, self.error_template)

    def replace_placeholder(self, l, key):
        for elem in range(len(l)):
            if l[elem] == "/static/Placeholder.png":
                l[elem] = key
                break
        return l

    def clean_cookies(self, request, lobby):
        print("Cleaning session")
        request.session["rotation_counter"] = 0
        lobby = hashlib.sha224(lobby.encode('utf-8')).hexdigest()[0:8] # Rehash current lobby to generate new lobby
        request.session["lobby"] = lobby
        request.session["blue_ban"] = ["/static/Placeholder.png" for _ in range(6)]
        request.session["red_ban"] = ["/static/Placeholder.png" for _ in range(6)]
        request.session["blue"] = ["/static/Placeholder.png" for _ in range(6)]
        request.session["red"] = ["/static/Placeholder.png" for _ in range(6)]
        return lobby

    def handle_champ_selection(self, request, found, blue_ban, red_ban, blue, red):
        picked = False
        for champ in found:
            if champ in set([char.lower().split(".png")[0].split("/")[-1] for char in blue_ban + red_ban + blue + red]):
                print("Champion already picked")
                picked = True
                continue
            image = cd.get_champ_image(champ)
            if self.rotation[request.session["rotation_counter"]] == "blue_ban":
                request.session["blue_ban"] = self.replace_placeholder(
                    request.session["blue_ban"], settings.STATIC_URL + image["full"])
            elif self.rotation[request.session["rotation_counter"]] == "red_ban":
                request.session["red_ban"] = self.replace_placeholder(
                    request.session["red_ban"], settings.STATIC_URL + image["full"])
            elif self.rotation[request.session["rotation_counter"]] == "blue":
                request.session["blue"] = self.replace_placeholder(
                    request.session["blue"], settings.STATIC_URL + image["full"])
            elif self.rotation[request.session["rotation_counter"]] == "red":
                request.session["red"] = self.replace_placeholder(
                    request.session["red"], settings.STATIC_URL + image["full"])
        if not picked:
            request.session["rotation_counter"] += 1
        return self.get_session(request)

    def get_session(self, request):
        return request.session["lobby"], request.session["blue_ban"], request.session["red_ban"], request.session["blue"], request.session["red"]

    def get_html_elems(self, lobby, blue_ban, red_ban, blue, red, error):
        return {
            "lobby": lobby,
            "blue_ban": blue_ban,
            "red_ban": red_ban,
            "blue1": blue[0],
            "red1": red[0],
            "blue2": blue[1],
            "red2": red[1],
            "blue3": blue[2],
            "red3": red[2],
            "blue4": blue[3],
            "red4": red[3],
            "blue5": blue[4],
            "red5": red[4],
            "error": error
        }
