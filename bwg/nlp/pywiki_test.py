
from pywikibot.data import api
import pywikibot
import pprint
import functools

LANGUAGE_ABBREVIATION = "fr"
RELEVANT_PROPERTIES_PER = {"P21", "P463", "P106", "P108", "P39", "P102", "P1416"}


def retry_with_fallback(triggering_error, **fallback_kwargs):
    def time_decorator(func):
        """
        Actual decorator
        """
        @functools.wraps(func)
        def func_wrapper(*args, **kwargs):
            try:
                function_result = func(*args, **kwargs)
            except triggering_error:
                kwargs.update(fallback_kwargs)
                function_result = func(*args, **fallback_kwargs)

            return function_result

        return func_wrapper

    return time_decorator


def try_entity_lookup():
    global LANGUAGE_ABBREVIATION  # TODO (Refactor): Pass this with task_config

    def get_entity_senses(itemtitle, language=LANGUAGE_ABBREVIATION):
        site = pywikibot.Site("wikidata", "wikidata")  # TODO (Refactor): Make this class variable
        request_parameters = {
            'action': 'wbsearchentities',
            'format': 'json',
            'language': language,
            'type': 'item',
            'search': itemtitle
        }
        request = api.Request(site=site, **request_parameters)
        response = request.submit()

        if len(response["search"]) == 0:
            return []

        return [
            {
                "uri": search_result["concepturi"],
                "id": search_result["id"],
                "description": search_result["description"],
                "label": search_result["label"]
            }
            for search_result in response["search"]
        ]

    def get_entity(wikidata_id, language=LANGUAGE_ABBREVIATION):
        site = pywikibot.Site("wikidata", "wikidata")  # TODO (Refactor): Make this class variable
        request = api.Request(
            site=site,
            action='wbgetentities',
            format='json',
            ids=wikidata_id
        )
        response = request.submit()

        if len(response["entities"]) == 0:
            return {}

        # TODO (Feature): Add claims to result if they correspond to specification
        return [
            {
                "aliases": [alias_dict["value"] for alias_dict in entity["aliases"][language]],
                "description": entity["descriptions"][language]["value"],
                "id": entity["id"],
                "label": entity["labels"][language]["value"],
                "modified": entity["modified"],
                "claims": _resolve_claims(entity["claims"], language)
            }
            for id_, entity in response["entities"].items()
        ][0]

    def _resolve_claims(claims, language=LANGUAGE_ABBREVIATION):
        global RELEVANT_PROPERTIES_PER
        return {
            _get_property_name(property_id, language): _get_entity_name(claim[0]["mainsnak"]["datavalue"]["value"]["id"])
            for property_id, claim in claims.items()
            if property_id in RELEVANT_PROPERTIES_PER
        }

    def _get_property_name(property_id, language=LANGUAGE_ABBREVIATION):
        site = pywikibot.Site("wikidata", "wikidata")  # TODO (Refactor): Make this class variable
        request = api.Request(
            site=site,
            action='wbgetentities',
            format='json',
            ids=property_id
        )
        response = request.submit()

        return [
            entity["labels"][language]["value"]
            for id_, entity in response["entities"].items()
        ][0]

    def _get_entity_name(entity_id, language=LANGUAGE_ABBREVIATION):
        site = pywikibot.Site("wikidata", "wikidata")  # TODO (Refactor): Make this class variable
        request = api.Request(
            site=site,
            action='wbgetentities',
            format='json',
            ids=entity_id
        )
        response = request.submit()

        return [
            entity["labels"][language]["value"]
            for id_, entity in response["entities"].items()
        ][0]

    def pretty_print(variable):
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(variable)

    wikidata_entries = get_entity_senses("André Boisclair")
    #wikidata_entries = get_entity_senses("Google")

    pretty_print(wikidata_entries)

    wikidata_id = wikidata_entries[0]["id"]
    pretty_print(get_entity(wikidata_id))


if __name__ == "__main__":
    try_entity_lookup()
