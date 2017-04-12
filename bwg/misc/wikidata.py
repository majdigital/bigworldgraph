# -*- coding: utf-8 -*-
"""
This module provides two different way to access wikidata:
    - Through the Wikimedia API
    - Over a scraper
"""

# STD
import abc
import re
import urllib.request
import urllib.parse

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


class WikidataScraperMixin(AbstractWikidataMixin):
    """
    Access Wikidata information via a scraper.
    """
    wikidata_base_url = "https://www.wikidata.org/wiki/"
    wikidata_entity_url = "https://www.wikidata.org/wiki/{entity_id}"
    wikidata_property_url = "https://www.wikidata.org/wiki/Property:{property_id}"
    wikidata_search_url = "https://www.wikidata.org/w/index.php?search=&search={name}&language={language}"

    def get_matches(self, name, language):
        """
        Get matches for an entity's name on Wikidata.
        """
        parsed_html = self._get_parsed_html(self.wikidata_search_url.format(
            name=urllib.parse.quote(name), language=language)
        )
        raw_search_results = [result.text for result in parsed_html.find_all("div", ["mw-search-result-heading"])]

        matches = [re.search("(.+?) \((Q\d+)\): (.+)", raw_result) for raw_result in raw_search_results]

        return [
            {
                "id": match.group(2),
                "description": match.group(3),
                "label": match.group(1)
            }
            for match in matches if match is not None
        ]

    @retry_with_fallback(triggering_error=AssertionError, language="en")
    def get_entity(self, entity_id, language, relevant_properties):
        """
        Get Wikidata information about an entity based on its identifier.
        """
        # TODO (Feature): Implement [DU 11.07.17]
        # aliases, description, id, label, modified, claims
        parsed_html = self._get_parsed_html(self.wikidata_entity_url.format(entity_id=entity_id))
        search_results = [
            result for result in parsed_html.find_all(
                "tr", [
                    "wikibase-entitytermsforlanguageview-{}".format(language)
                ]
            )
        ]
        # If no results found for language, raise AssertionError and re-try function with English
        assert len(search_results) != 0 or language == "en"

        return [
            {
                "id": entity_id,
                "aliases": self._unwrap_aliases(result),
                "description": self._unwrap_description(result),
                "label": self._unwrap_label(result),
                "modified": self._get_last_modification(parsed_html),
                "claims": self._get_claims(parsed_html, language=language, relevant_properties=relevant_properties)
            }
            for result in search_results
        ]

    @staticmethod
    def _unwrap_aliases(result):
        raw_aliases = result.find_all("li", ["wikibase-aliasesview-list-item"])
        aliases = [raw_alias.text.strip() for raw_alias in raw_aliases]
        return aliases

    @staticmethod
    def _unwrap_description(result):
        return result.find_all("td", ["wikibase-entitytermsforlanguageview-description"])[0].text.strip()

    @staticmethod
    def _unwrap_label(result):
        return result.find_all("td", ["wikibase-entitytermsforlanguageview-label"])[0].text.strip()

    @staticmethod
    def _get_last_modification(parsed_html):
        raw_modification_time = parsed_html.find("li", {"id": "footer-info-lastmod"}).text.strip()
        matches = re.search("on (.+?), at (\d{2}:\d{2})", raw_modification_time)
        modification_time = "{}, {}".format(matches.group(1), matches.group(2))
        return modification_time

    def _get_claims(self, parsed_html, language, relevant_properties):
        raw_claims = parsed_html.find_all("div", ["wikibase-statementgroupview"])
        filtered_raw_claims = [raw_claim for raw_claim in raw_claims if raw_claim.attrs["id"] in relevant_properties]

        return {
            property: value
            for property, value in zip(
                [self._get_claim_property(raw_claim, language=language) for raw_claim in filtered_raw_claims],
                [self._get_claim_value(raw_claim, language) for raw_claim in filtered_raw_claims]
            )
            if property is not None and value is not None
        }

    @staticmethod
    @retry_with_fallback(triggering_error=AssertionError, language="en")
    def _get_claim_property(raw_claim, language):
        # TODO (Refactor): Get name of property in current language [DU 12.04.17]
        raw_property_name = raw_claim.find("div", "wikibase-statementgroupview-property")

        assert raw_property_name is not None or language == "en"

        if raw_property_name is not None:
            property_name = raw_property_name.text.strip()
            return property_name

        return None

    @staticmethod
    @retry_with_fallback(triggering_error=AssertionError, language="en")
    def _get_claim_value(raw_claim, language):
        raw_value = raw_claim.find("div", "wikibase-snakview-variation-valuesnak")

        assert raw_value is not None or language == "en"

        if raw_value is not None:
            property_value = raw_value.text.strip()
            return property_value

        return None

    @staticmethod
    def _get_parsed_html(url):
        # TODO (Improve): Use other library than urllib [DU 12.04.17]
        with urllib.request.urlopen(url) as response:
            html = response.read()
            return bs4.BeautifulSoup(html, "lxml")


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
