def analyze(champ):
    switcher = {
            "seraphine": "Seraphine hard poke in lane, save ult for disengage",
            "shyvana": "Shyvana farm til 6, contest drags",
            "singed": "Singed proxies til laning phase over, peel and split once laning phase is over",
            "shen": "Shen peels carries while getting prio",
            "sejuani": "Sejuani counter ganks and tries to pick carries late",
            "sett": "Sett hard pumps lane and roams with ult",
            "shaco": "Shaco farms and one shot",
            "sion": "Sion farms and gets unkillable during objectives",
            "syndra": "Syndra farms and gets picks with e and r",
            "fizz": "Fizz roams and kills bot lane",
        }
    return switcher.get(champ, "Invalid champ")
