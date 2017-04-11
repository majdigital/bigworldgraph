# -*- coding: utf-8 -*-
"""
This module provides two different way to access wikidata:
    - Through the Wikimedia API
    - Over a scraper
"""

# TODO (Refactor): Remove pywikibot from requirements.txt? [DU 11.04.17]
# Notes
# https://www.wikidata.org/wiki/Q1

# STD
import abc

# EXT
import bs4
import pywikibot
from pywikibot.data import api

# PROJECT
from bwg.misc.helpers import construct_dict_from_source
from bwg.nlp.utilities import retry_with_fallback


class AbstractWikidataMixin:
    """
    Define the functions inheriting subclasses should implement.
    """
    @abc.abstractmethod
    def get_matches(self, name, language):
        """
        Get matches for an entity's name on Wikidata.
        """
        pass

    @abc.abstractmethod
    def get_entity(self, wikidata_id, language, relevant_properties):
        """
        Get Wikidata information about an entity based on its identifier.
        """
        pass

    @abc.abstractmethod
    def resolve_claims(self, claims, language, relevant_properties):
        """
        Transform the claims made about a Wikidata entity into a human-readable format.
        """
        pass

    @abc.abstractmethod
    def get_property_name(self, property_id, language):
        """
        Get the name of a property based on its identifier.
        """
        pass

    @abc.abstractmethod
    def get_entity_name(self, entity_id, language):
        """
        Get the name of an entity based on its identifier.
        """
        pass


class WikidataScraperMixin(AbstractWikidataMixin):
    """
    Access Wikidata information via a scraper.
    """
    wikidata_base_url = "https://www.wikidata.org/wiki/"
    wikidata_entity_url = "https://www.wikidata.org/wiki/{entity_id}"
    wikidata_property_url = "https://www.wikidata.org/wiki/Property:{property_id}"
    wikidata_search_url = "https://www.wikidata.org/w/index.php?search=&search={name}"

    def get_matches(self, name, language):
        """
        Get matches for an entity's name on Wikidata.
        """
        # TODO (Feature): Implement [DU 11.07.17]
        pass

    def get_entity(self, wikidata_id, language, relevant_properties):
        """
        Get Wikidata information about an entity based on its identifier.
        """
        # TODO (Feature): Implement [DU 11.07.17]
        pass

    def resolve_claims(self, claims, language, relevant_properties):
        """
        Transform the claims made about a Wikidata entity into a human-readable format.
        """
        # TODO (Feature): Implement [DU 11.07.17]
        pass

    def get_entity_name(self, entity_id, language):
        """
        Get the name of an entity based on its identifier.
        """
        # TODO (Feature): Implement [DU 11.07.17]
        pass

    def get_property_name(self, property_id, language):
        """
        Get the name of a property based on its identifier.
        """
        # TODO (Feature): Implement [DU 11.07.17]
        pass

    def _get_soup(self, url):
        return bs4.BeautifulSoup(url, "html.parser")


class WikidataAPIMixin(AbstractWikidataMixin):
    """
    Access Wikidata information via Wikimedia's API.
    """
    wikidata_site = pywikibot.Site("wikidata", "wikidata")

    @retry_with_fallback(triggering_error=KeyError, language="en")
    def get_matches(self, name, language):
        """
        Get matches for an entity's name on Wikidata.
        """
        additional_request_parameters = {
            "action": "wbsearchentities",
            "language": language,
            "type": "item",
            "search": name
        }

        response = self._request(**additional_request_parameters)

        if len(response["search"]) == 0:
            return []

        return [
            construct_dict_from_source(
                {
                    "uri": lambda source: source["concepturi"],
                    "id": lambda source: source["id"],
                    "description": lambda source: source["description"],
                    "label": lambda source: source["label"]
                },
                search_result
            )
            for search_result in response["search"]
        ]

    @retry_with_fallback(triggering_error=KeyError, language="en")
    def get_entity(self, wikidata_id, language, relevant_properties):
        """
        Get Wikidata information about an entity based on its identifier.
        """
        additional_request_parameters = {
            "ids": wikidata_id
        }

        response = self._request(**additional_request_parameters)

        if len(response["entities"]) == 0:
            return {}

        return [
            construct_dict_from_source(
                {
                    "aliases": lambda source: [alias_dict["value"] for alias_dict in source["aliases"][language]],
                    "description": lambda source: source["descriptions"][language]["value"],
                    "id": lambda source: source["id"],
                    "label": lambda source: source["labels"][language]["value"],
                    "modified": lambda source: source["modified"],
                    "claims": lambda source: self.resolve_claims(
                        source["claims"], language=language, relevant_properties=relevant_properties
                    )
                },
                entity
            )
            for id_, entity in response["entities"].items()
        ][0]

    @retry_with_fallback(triggering_error=KeyError, language="en")
    def resolve_claims(self, claims, language, relevant_properties):
        """
        Resolve the claims (~ claimed facts) about a wikidata entity. 
        """
        return {
            self.get_property_name(property_id, language):
                self.get_entity_name(claim[0]["mainsnak"]["datavalue"]["value"]["id"], language=language)
            for property_id, claim in claims.items()
            if property_id in relevant_properties
        }

    @retry_with_fallback(triggering_error=KeyError, language="en")
    def get_property_name(self, property_id, language):
        """
        Get the name of a wikidata property.
        """
        additional_request_parameters = {
            "ids": property_id
        }

        response = self._request(**additional_request_parameters)

        return [
            entity["labels"][language]["value"]
            for id_, entity in response["entities"].items()
        ][0]

    @retry_with_fallback(triggering_error=KeyError, language="en")
    def get_entity_name(self, entity_id, language):
        """
        Get the name of a wikidata entity.
        """
        additional_request_parameters = {
            "ids": entity_id
        }

        response = self._request(**additional_request_parameters)

        return [
            entity["labels"][language]["value"]
            for id_, entity in response["entities"].items()
        ][0]

    def _request(self, **additional_request_parameters):
        """
        Send a request to the API.
        """
        request_parameters = {
            "site": self.wikidata_site,
            "action": 'wbgetentities',
            "format": 'json',
            "use_get": True,
            "throttle": False,
            "max_retries": 5
        }

        request_parameters.update(additional_request_parameters)
        request = api.Request(**request_parameters)
        return request.submit()
