from django.shortcuts import render
from django.views.generic import TemplateView, View
from wardhop.drafter import ChampionDatabase as ChampionDatabase
import hashlib
import json
import main.settings as settings
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
        request.session["rotation_counter"] = 0
        request.session["lobby"] = lobby
        request.session["blue_ban"] = [
            "/static/Placeholder.png" for _ in range(5)]
        request.session["red_ban"] = [
            "/static/Placeholder.png" for _ in range(5)]
        request.session["blue"] = ["/static/Placeholder.png" for _ in range(5)]
        request.session["red"] = ["/static/Placeholder.png" for _ in range(5)]
        return render(request, self.template_name, {"lobby": lobby, "images": all_images})


class PickBanView(View):
    draft_template = "pickban.html"
    error_template = "errors.html"
    images = cd.get_all_champ_images()
    champions = cd.get_all_champ_names()
    rotation = ["blue_ban", "red_ban", "blue_ban", "red_ban", "blue_ban", "red_ban", "blue", "red",
                "red", "blue", "blue", "red", "red_ban", "blue_ban", "red_ban", "blue_ban", "red", "blue", "blue", "red"]

    def get(self, request):
        error = ""
        lobby, blue_ban, red_ban, blue, red = self.get_session(request)
        try:
            rotation_counter = request.session["rotation_counter"]
        except KeyError:
            request.session["rotation_counter"] = 0
        return render(request, self.draft_template, self.get_html_elems(lobby, blue_ban, red_ban, blue, red, error, self.champions, self.rotation[rotation_counter]))

    def post(self, request):
        error = ""

        # Initialize rotation counter; KeyError indicates first of session
        try:
            rotation_counter = request.session["rotation_counter"]
        except KeyError:
            request.session["rotation_counter"] = 0

        lobby, blue_ban, red_ban, blue, red = self.get_session(request)

        # New draft request handler
        if request.POST.get("clean"):
            lobby = self.clean_session(request, lobby)
            lobby, blue_ban, red_ban, blue, red = self.get_session(request)
            rotation_counter = request.session["rotation_counter"]
            return render(request, self.draft_template, self.get_html_elems(lobby, blue_ban, red_ban, blue, red, error, self.champions, self.rotation[rotation_counter]))

        # Once the draft ends, draft results are not altered per ``replace_placeholder`` function
        if request.session["rotation_counter"] >= len(self.rotation):
            analysis = self.analyze(blue, red)
            return render(request, self.draft_template, self.get_html_elems(lobby, blue_ban, red_ban, blue, red, error, self.champions, "Draft complete", analysis))

        # Handle champion selection
        champ = request.POST.get("champion")
        if champ:
            found = cd.search(champ)
            if found:
                (lobby, blue_ban, red_ban, blue, red), changed = self.handle_champ_selection(
                    request, found, blue_ban, red_ban, blue, red)
                rotation_counter = request.session["rotation_counter"]
                if rotation_counter < len(self.rotation):
                    if changed:
                        error = "Champion already selected"
                    return render(request, self.draft_template, self.get_html_elems(lobby, blue_ban, red_ban, blue, red, error, self.champions, self.rotation[rotation_counter]))
                else:
                    analysis = self.analyze(blue, red)
                    return render(request, self.draft_template, self.get_html_elems(lobby, blue_ban, red_ban, blue, red, error, self.champions, "Draft complete", analysis))
            else:
                error = "Champion not found."
                return render(request, self.draft_template, self.get_html_elems(lobby, blue_ban, red_ban, blue, red, error, self.champions, self.rotation[rotation_counter]))
        else:
            return render(request, self.draft_template, self.get_html_elems(lobby, blue_ban, red_ban, blue, red, error, self.champions, self.rotation[rotation_counter]))
        return render(request, self.error_template)

    def replace_placeholder(self, l, key):
        for elem in range(len(l)):
            if l[elem] == "/static/Placeholder.png":
                l[elem] = key
                break
        return l

    def clean_session(self, request, lobby):
        print("Cleaning session")
        # Rehash current lobby to generate new lobby
        lobby = hashlib.sha224(lobby.encode('utf-8')).hexdigest()[0:8]
        request.session["rotation_counter"] = 0
        request.session["lobby"] = lobby
        request.session["blue_ban"] = [
            "/static/Placeholder.png" for _ in range(5)]
        request.session["red_ban"] = [
            "/static/Placeholder.png" for _ in range(5)]
        request.session["blue"] = ["/static/Placeholder.png" for _ in range(5)]
        request.session["red"] = ["/static/Placeholder.png" for _ in range(5)]
        return lobby

    def handle_champ_selection(self, request, champ, blue_ban, red_ban, blue, red):
        if champ in self.selected_champs(blue_ban, red_ban, blue, red):
            session = self.get_session(request)
            return session, True
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
        request.session["rotation_counter"] += 1
        session = self.get_session(request)
        return session, False

    def get_session(self, request):
        return request.session["lobby"], request.session["blue_ban"], request.session["red_ban"], request.session["blue"], request.session["red"]

    def get_html_elems(self, lobby, blue_ban, red_ban, blue, red, error, champions, draft_rotation, analysis=""):
        draft_rotation = draft_rotation.replace("_", " ").title()
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
            "error": error,
            "champions": json.dumps(champions),
            "draft_rotation": draft_rotation,
            "analysis": analysis
        }

    def selected_champs(self, blue_ban, red_ban, blue, red):
        return [char.lower().split(".png")[0].split("/")[-1] for char in blue_ban + red_ban + blue + red]

    def red_selected_champs(self, red):
        return [char.lower().split(".png")[0].split("/")[-1] for char in red]

    def blue_selected_champs(self, blue):
        return [char.lower().split(".png")[0].split("/")[-1] for char in blue]

    def analyze(self, blue, red):
        blue_selected_champs = self.blue_selected_champs(blue)
        red_selected_champs = self.red_selected_champs(red)
        blue_analysis = cd.get_multiple_champ_analysis(blue_selected_champs)
        red_analysis = cd.get_multiple_champ_analysis(red_selected_champs)
        analysis = []
        counter = 0
        len_analysis = len(blue_analysis)
        while(counter < len_analysis):
            analysis.append([blue_analysis[counter], red_analysis[counter]])
            counter += 1
        return analysis
