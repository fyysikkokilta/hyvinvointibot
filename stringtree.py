"""
This module contains all string and some helper functions related to messaging.
"""
import types
from collections import OrderedDict
import scoring
from scoring import GOOD_KEY, BAD_KEY, ScoreObject

RETURN_BUTTON_ID = "return_choice"

#####################
# MESSAGE CONSTANTS #
#####################

BUTTONS_ERROR_MSG = "Valitse yksi annetuista vaihtoehdoista."

RETURN_BUTTON_MESSAGE = "« Alkuun"
RETURN_MESSAGE = "alkuun"
GROUP_REPLY_MESSAGE = "Lähetä komentoja yksityisviestillä."
DID_NOT_UNDERSTAND_MESSAGE = "En ymmärrä. Käytä jotakin annetuista komennoista tai kokeile /help."
UNKNOWN_COMMAND_MESSAGE = "En ymmärrä komentoa. Käytä jotakin annetuista komennoista tai kokeile /help."
START_ADD_EVENT_MESSAGE = "Mihin kategoriaan haluat lisätä pisteitä?"
NOT_PARTICIPANT_MESSAGE = "Et ole minkään ilmoittautuneen joukkueen jäsen. Jos haluat vielä mukaan kilpailuun, ole yhteydessä käyttäjään @martong."

USER_HISTORY_MESSAGE = """
Viimeisimmät lisäämäsi tapahtumat:

{}"""
USER_HISTORY_COUNT_PROMPT = "\n\nPoista tapahtuma antamalla sen numero."
NO_USER_HISTORY_MESSAGE = "Et ole lisännyt tänään vielä yhtään tapahtumaa."
USER_HISTORY_COUNT_ERROR_MESSAGE = "Anna kokonaisluku välillä 1-{}"
ITEM_REMOVED_SUCCESS_MESSAGE = "Tapahtuma poistettiin onnistuneesti."

ALL_ITEMS_ADDED_FOR_TODAY_MESSAGE = """
Olet jo lisännyt kaikki mahdolliset tapahtumat tälle päivälle. Hienoa!

Voit poistaa lisäämiäsi tapahtumia komennolla /poista.
""" #TODO: good?
ADDING_MANY_START_MESSAGE = "Lisätään jäljellä olevat kategoriat tälle päivälle."
ADDING_MANY_FINISHED_MESSAGE = "Kaikki päivän tapahtumat on nyt lisätty." #TODO: good?
ADDING_MANY_CANCEL_MESSAGE = "Lopeta"
ADDING_MANY_CANCELING_MESSAGE = "Selvä."
ITEM_ALREADY_ADDED_FOR_TODAY_MESSAGE = """
Olet jo lisännyt tuon kategorian tänään. Voit muuttaa sitä poistamalla sen komennollla /poista ja lisäämällä sen uudelleen.

Kokeile jotakin toista kategoriaa.
"""


HELP_MESSAGE = """Hyvinvointibotin avulla voit syöttää pisteitä itsellesi ja joukkueellesi Hottiksen hyvinvointikilpailussa. Syöttääksesi pisteitä sinun pitää olla kilpailuun ilmoittautuneen joukkueen jäsen. Jos haluat osallistua kilpailuun jälkikäteen, ota yhteyttä käyttäjään @martong.

Pisteitä voi kerätä kategorioista liikunta, alkoholi, ruoka, vapaa-aika, stressi ja uni. Jokaiseen kategoriaan voi lisätä kerran päivässä pisteitä. Eri vastauksista voit saada joko hyvinvointi-, tai pahoinvointipisteitä. Komennolla /lisaa voit lisätä yhteen kategoriaan pisteitä. Komennolla /lisaapaiva voit lisätä päivän pisteet kaikkiin kategorioihin. Komennolla /poista voit poistaa saman päivänä lisäämiäsi pisteitä.


Komennot

/help - Tulosta ohje.
/lisaa - Lisää pisteitä yhteen kategoriaan.
/lisaapaiva - Lisää pisteitä kaikkiin kategorioihin kerralla.
/poista - Poista pisteitä.
/rank - Näytä parhaat joukkueet.
/info - Näytä tietoja sinusta ja joukkueestasi.
"""  # TODO: format admin  # TODO: add all implemented commands

#TODO: good?
RANK_MESSAGE = """
*Parhaat joukkueet:*

*Hyvinvointisarja:*
Sijoitus - joukkue (hyvinvointi-indeksi)
{}

*Pahoinvointisarja:*
Sijoitus - joukkue (pahoinvointi-indeksi)
{}
"""

#TODO: good?
INFO_MESSAGE = """
Tietoja käyttäjästä {username}:

Joukkue: {team}
Joukkueen jäsenet: {team_members}
Joukkueen sijoitukset ja indeksit:
Hyvinvointi: {team_rank_good} / {n_teams} ({good_index})
Pahoinvointi: {team_rank_bad} / {n_teams} ({bad_index})

Viimeksi lisäämäsi tapahtumat:
{history_str}
"""

"""
The STRING_TREE object contains all possible chains of discussion. It is a dict
containing dicts. Each sub-dictionary corresponds to a message. Each dict
should have the following key-value pairs:
    msg - the message the bot sends when at this point in the conversation
        (the root node doesn't have this)
    errorMessage - a message that the bot should send when the reply wasn't
        sensible

Furthermore, each non-leaf node should have the attributes
    children - multiple choices, which the user can select from using buttons
    OR
    child AND validation_func - in this case, the user is expected to input
        free-form data, such as a number. this data should be validated using
        the function validation_func, which should return either the validated
        value (such as a number extracted from a string) or None.

If a node has neither of the above, it is assumed to be a leaf node, and the
conversation is terminated after it. A leaf node may have a key-value pair
score_func, which evaluates the score of a given conversation chain.
"""

STRING_TREE = {
    #### root has no 'msg' (good idea?)
    "msg": START_ADD_EVENT_MESSAGE,
    "errorMessage" : BUTTONS_ERROR_MSG,
    "children" : {
        #TODO: change to OrderedDict?
        "liikunta" : {
            "msg" : "Asteikolla 0-5, kuinka intensiivistä liikuntaa harrastit?",
            "errorMessage" : "Anna vastaukseksi numero välillä 0-5.", #TODO: add 'peruuta kirjoittamalla alkuun' tms
            "validation_func": scoring.liikunta_validate_intensity,
            "child" : {
                "msg" : "Kuinka kauan liikunta kesti tunteina? (max X h)",
                "errorMessage" : "Korkein hyväksytty tuntimäärä on X tuntia.",
                "validation_func": scoring.liikunta_validate_duration,
                "child" : {
                    "msg" : "Hieno homma, jatka samaan malliin!", #TODO: good?
                    "score_func": scoring.liikunta_score
                }
            }
        },
        "alkoholi" : {
            "msg": """
            Kuinka rankasti tuli dokattua eilen?

Voit tulkita tasoja esimerkiksi seuraavasti:
No blast - "Ehkä otin, ehkä en."
Medium blast - "Kun otan, niin juon."
Full blast - Tiedät, mitä tämä tarkoittaa.
Bläkäri - "Vain Bläkkisvuohi muistaa."
            """,
            "errorMessage": BUTTONS_ERROR_MSG,
            "children": OrderedDict([
                ("ei ollenkaan!", {
                    "msg": "Hienoa!",
                    "score_func": lambda h: ScoreObject(0, GOOD_KEY, h),
                }),
                ("no blast", {
                    "msg": "Toivottavasti pari lasillista rentoutti!",
                    "score_func": lambda h: ScoreObject(1, BAD_KEY, h),
                }),
                ("medium blast", {
                    "msg": "Nää on näitä.",
                    "score_func": lambda h: ScoreObject(2, BAD_KEY, h),
                }),
                ("full blast", {
                    "msg": "Hienosti. ",
                    "score_func": lambda h: ScoreObject(3, BAD_KEY, h),
                }),
                ("bläkäri", {
                    "msg": "Tsemppiä tähän päivään!",
                    "score_func": lambda h: ScoreObject(4, BAD_KEY, h),
                }),
             ]),
        },
        "ruoka" : {
            "msg" : """
            Miten hyvin söit tänään?

Voit tulkita vaihtoehtoja seuraavasti:
Tavallista paremmin - Laitoit esimerkiksi itse ruokaa tai muuten kiinnitit huomiota aterioihisi.
Normipäivä - Sinulle tyypilliset ruokailutottumukset.
Huonosti - Nälkä yllätti pahasti tai tuli mässäiltyä.
            """,
            "errorMessage" : BUTTONS_ERROR_MSG,
            "children" : OrderedDict([
                ("panostin tänään",  {
                    "msg" : "Hienoa! Jatka samaan malliin.",          # TODO
                    "score_func" : lambda h: ScoreObject(1, GOOD_KEY, h),
                }),
                ("normipäivä", {
                    "msg" : "Selvä homma.",        #TODO
                    "score_func" : lambda h: ScoreObject(0, GOOD_KEY, h),
                }),
                ("huonosti", {
                    "msg" : "Sellaista sattuu!",        #TODO
                    "score_func" : lambda h: ScoreObject(1, BAD_KEY, h),
                }),
            ]),
        },
        "vapaa-aika" : {
            "msg" : """
            Kuinka paljon vietit vapaa-aikaa tänään?

Voit tulkita vaihtoehtoja seuraavasti:
Runsaasti - Vapaa-aikaa oli tavallista enemmän ja se oli rentouttavaa.
Sopivasti - Vapaa-aikaa oli sen verran kuin itse toivot jokaiselle päivälle.
En riittävästi - Vapaa-aikaa ei ollut tarpeeksi, jotta päivän stressi purkautuisi.
            """,
            "errorMessage" : BUTTONS_ERROR_MSG,
            "children" : OrderedDict([
                ("runsaasti", {
                    "msg" : "Mahtavaa!",
                    "score_func" : lambda h: ScoreObject(2, GOOD_KEY, h),
                }),
                ("sopivasti", {
                    "msg" : "Selvä homma.",
                    "score_func" : lambda h: ScoreObject(0, GOOD_KEY, h),
                }),
                ("ei riittävästi", {
                    "msg" : "Muista ottaa aikaa myös itsellesi!",
                    "score_func" : lambda h: ScoreObject(1, BAD_KEY, h),
                }),
            ]),
        },
        "stressi" : {
            "msg" : "Kuinka stressaantunut olet ollut tänään?",
            "errorMessage" : BUTTONS_ERROR_MSG,
            "children" : OrderedDict([
                ("paljon", {
                    "msg" : "Voi ei! Jos stressi jatkuu pitkään, pyri vähentämään stressiä aiheuttavia asioita.",
                    "score_func" : lambda h: ScoreObject(2, BAD_KEY, h),
                }),
                ("vähän", {
                    "msg" : "Toivottavasti stressitasot pysyvät kohtuullisina!",
                    "score_func" : lambda h: ScoreObject(1, BAD_KEY, h),
                }),
                ("en lainkaan", {
                    "msg" : "Mahtavaa!",
                    "score_func" : lambda h: ScoreObject(0, GOOD_KEY, h),
                }),
            ]),
        },
        "uni" : {
            "msg" : """Kuinka hyvin nukuit viime yönä?

Aikuinen tarvitsee yössä keskimäärin 7-9 tuntia unta. Voit kuitenkin ottaa vastauksissasi huomioon myös unen laadun.""",
            "errorMessage" : BUTTONS_ERROR_MSG,
            "children" : OrderedDict([
                ("tosi hyvin", {
                    "msg" : "Mahtavaa!",
                    "score_func" : lambda h: ScoreObject(1, GOOD_KEY, h),
                }),
                ("riittävästi", {
                    "msg" : "Kiva!",
                    "score_func" : lambda h: ScoreObject(0, GOOD_KEY, h),
                }),
                ("huonosti", {
                    "msg" : "Voi ei! Koita pian lyhentää univelkaa.",
                    "score_func" : lambda h: ScoreObject(1, BAD_KEY, h,)
                }),
                ("heräsin darrassa", {
                    "msg" : "Kuten se on.",
                    "score_func" : lambda h: ScoreObject(2, BAD_KEY, h),
                }),
            ]),
        },
    },
    "root": True
}


def verifyTree(tree, verbose = False):
    """
    recursively traverse the message tree and check that each node has certain attributes
    """

    if tree != STRING_TREE:
        # every other node than the root should have 'msg'
        assert "msg" in tree, tree
    #assert "errorMessage" in tree, tree # needed? -- TODO: this is needed only for nodes with children, move it accordingly.

    if "score_func" in tree:
      assert type(tree["score_func"]) == types.FunctionType

    if "children" in tree:
        for childName, child in tree["children"].items():
            verifyTree(child, verbose)

    elif "child" in tree:
        assert "validation_func" in tree
        verifyTree(tree["child"], verbose)

    else:
        if verbose:
            print("verifyTree(): found leaf node: {}".format(tree))
        assert "score_func" in tree, "no score function found for leaf {}".format(tree)

verifyTree(STRING_TREE)

# this error is thrown if a message is invalid in a given context
class InvalidMessageError(Exception): pass


class StringTreeParser():
    def __init__(self):
        self.root = STRING_TREE
        self.current_message = STRING_TREE
        #self.message_chain = []

    def goForward(self, message_str): #, user): #TODO
        """
        Attempt to advance the conversation based on message_str. If the
        message is invalid, raise ValueError so the caller can send the
        errorMessage of the current message.
        Returns a pair (next_message, validated_value), where next_message is
        the subtree dict of the rest of the conversation and validated_value is
        the validated value of message_str (such as a number), if applicable,
        or None.
        """
        next_message = None
        validated_value = None

        node = self.current_message
        if "children" in node:
            children = node["children"]

            if message_str not in children:
                #TODO: back button etc
                #if message_str in [RETURN_BUTTON_MESSAGE, RETURN_MESSAGE]: self.reset(); return self.nextMessage #TODO: not good idea to reset here without notifying caller...
                raise InvalidMessageError("invalid button") #TODO: should include errorMessage here?
            else:
                #self.message_chain.append(node)
                self.current_message = children[message_str]
                #return self.current_message #TODO: move this to 'ret'?
                next_message = self.current_message

        elif "child" in node:
            # validate message
            validated_value = node["validation_func"](message_str)
            if validated_value is None:
                raise InvalidMessageError("invalid value")
            else:
                #self.message_chain.append(node)
                self.current_message = node["child"]
                #return self.current_message
                next_message = self.current_message

        # was leaf, don't do anything? is it good that the caller handles no children?
        if "score_func" in node:
            print("TODO: score_func found, what do???") #TODO - or should be done by callee?

        return (next_message, validated_value)

        return ret

    #def goBack(self):
    #    if self.message_chain:
    #        self.current_message = self.message_chain.pop()
    #    else:
    #        raise NotImplementedError

    def reset(self):
        self.current_message = self.root
        #self.message_chain = []

    def get_categories(self):
        return list(self.root["children"].keys())

    #def go_to_category(self, category):
    #    category = category.lower()
    #    #if category not in self.root["children"]:
    #    #    #TODO: raise valueError?

    #    self.current_message = category


    def is_at_root(self):
        return self.current_message == self.root
