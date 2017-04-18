# -*- coding: utf-8 -*-
"""
This module provides two different way to access Wikidata:
    * Through the Wikimedia API with Pywikibot as a wrapper
    * Over a scraper using BeautifulSoup4
    
Currently, accessing the data via the API is faster than the scraper.
"""

# STD
import abc
import re
import urllib.request
import urllib.parse
import requests

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
        
        :param name: Name of entity.
        :type name: str
        :param language: Abbreviation of target language.
        :type language: str
        :return: List of matches.
        :rtype: list
        """
        pass

    @abc.abstractmethod
    def get_entity(self, wikidata_id, language, relevant_properties):
        """
        Get Wikidata information about an entity based on its identifier.
        
        :param wikidata_id: Wikidata ID of desired entity.
        :type wikidata_id: str
        :param language: Abbreviation of target language.
        :type language: str
        :param relevant_properties: Types of claims that should be included.
        :type relevant_properties: list
        :return: List of dates about every sense of the entity (un-ambiguous entites just will have one sense).
        :rtype: list
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
        
        :param name: Name of entity.
        :type name: str
        :param language: Abbreviation of target language.
        :type language: str
        :return: List of matches.
        :rtype: list
        """
        parsed_html = self._get_parsed_html(
            self.wikidata_search_url.format(name=urllib.parse.quote(name), language=language)
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
    def get_entity(self, wikidata_id, language, relevant_properties):
        """
        Get Wikidata information about an entity based on its identifier.
        
        :param wikidata_id: Wikidata ID of desired entity.
        :type wikidata_id: str
        :param language: Abbreviation of target language.
        :type language: str
        :param relevant_properties: Types of claims that should be included.
        :return: List of dates about every sense of the entity (un-ambiguous entites just will have one sense).
        :rtype: list
        """
        # aliases, description, id, label, modified, claims
        parsed_html = self._get_parsed_html(self.wikidata_entity_url.format(entity_id=wikidata_id))
        search_results_html = [
            result for result in parsed_html.find_all(
                "tr", [
                    "wikibase-entitytermsforlanguageview-{}".format(language)
                ]
            )
        ]

        # If no results found for language, raise AssertionError and re-try function with English
        assert len(search_results_html) != 0 or language == "en"

        return [
            {
                "id": wikidata_id,
                "aliases": self._unwrap_aliases(result_html),
                "description": self._unwrap_description(result_html),
                "label": self._unwrap_label(result_html),
                "modified": self._get_last_modification(parsed_html),
                "claims": self._get_claims(parsed_html, language=language, relevant_properties=relevant_properties)
            }
            for result_html in search_results_html
        ]

    @staticmethod
    def _unwrap_aliases(search_result_html):
        """
        Extract aliases from the Wikidata site html of a Wikidata entity.
        
        :param search_result_html: Parsed html of an search result.
        :type search_result_html: bs4.BeautifulSoup
        :return: All aliases of a Wikidata entity.
        :rtype: list
        """
        raw_aliases = search_result_html.find_all("li", ["wikibase-aliasesview-list-item"])
        aliases = [raw_alias.text.strip() for raw_alias in raw_aliases]

        return aliases

    @staticmethod
    def _unwrap_description(search_result_html):
        """
        Extract the description from the Wikidata site html of a Wikidata entity.

        :param search_result_html: Parsed html of an search result.
        :type search_result_html: bs4.BeautifulSoup
        :return: Description of a Wikidata entity.
        :rtype: str
        """
        return search_result_html.find_all("td", ["wikibase-entitytermsforlanguageview-description"])[0].text.strip()

    @staticmethod
    def _unwrap_label(search_result_html):
        """
        Extract the label from the Wikidata site html of a Wikidata entity.

        :param search_result_html: Parsed html of an search result.
        :type search_result_html: bs4.BeautifulSoup
        :return: Label of a Wikidata entity.
        :rtype: str
        """
        return search_result_html.find_all("td", ["wikibase-entitytermsforlanguageview-label"])[0].text.strip()

    @staticmethod
    def _get_last_modification(parsed_html):
        """
        Extract the last modification of this Wikipedia entry.
        
        :param parsed_html: Parsed html of this entry's Wikidata site.
        :type parsed_html: bs4.BeautifulSoup 
        :return: The date and time of the last modification.
        :rtype: str
        """
        raw_modification_time = parsed_html.find("li", {"id": "footer-info-lastmod"}).text.strip()
        matches = re.search("on (.+?), at (\d{2}:\d{2})", raw_modification_time)
        modification_time = "{}, {}".format(matches.group(1), matches.group(2))

        return modification_time

    def _get_claims(self, parsed_html, language, relevant_properties):
        """
        Extract the claims of this Wikipedia entry.

        :param parsed_html: Parsed html of this entry's Wikidata site.
        :type parsed_html: bs4.BeautifulSoup 
        :param language: Abbreviation of target language.
        :type language: str
        :param relevant_properties:
        """
        raw_claims = parsed_html.find_all("div", ["wikibase-statementgroupview"])
        filtered_raw_claims = [raw_claim for raw_claim in raw_claims if raw_claim.attrs["id"] in relevant_properties]

        return {
            property_: value
            for property_, value in zip(
                [self._get_claim_property(raw_claim, language=language) for raw_claim in filtered_raw_claims],
                [self._get_claim_value(raw_claim, language=language) for raw_claim in filtered_raw_claims]
            )
            if property_ is not None and value is not None
        }

    @staticmethod
    @retry_with_fallback(triggering_error=AssertionError, language="en")
    def _get_claim_property(raw_claim, language):
        """
        Extract the property from inside a claim.
        
        :param raw_claim: Parsed html of this entry's Wikidata site.
        :type raw_claim: bs4.BeautifulSoup
        :param language: Abbreviation of target language.
        :type language: str
        :return: Name of property or None
        :rtype: str, None
        """
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
        """
        Extract the value from inside a claim.

        :param raw_claim: Parsed html of this entry's Wikidata site.
        :type raw_claim: bs4.BeautifulSoup
        :param language: Abbreviation of target language.
        :type language: str
        :return: Value or None
        :rtype: str, None
        """
        raw_value = raw_claim.find("div", "wikibase-snakview-variation-valuesnak")

        assert raw_value is not None or language == "en"

        if raw_value is not None:
            property_value = raw_value.text.strip()
            return property_value

        return None

    @staticmethod
    def _get_parsed_html(url, session=None):
        """
        Get parsed HTML from an URL.
        
        :param url: URL of the site the HTML should be requested and parsed from.
        :type url: str
        :param session: Request session (optional).
        :type session: request.Session, None
        :return: Parsed HTML.
        :rtype: bs4.BeautifulSoup
        """
        strainer = bs4.SoupStrainer("body")  # One parse the important part of the page

        if session is None:
            session = requests.Session()
        html_ = session.get(url, headers={'Accept-Encoding': 'identity'}).content

        return bs4.BeautifulSoup(html_, "lxml", parse_only=strainer)


class WikidataAPIMixin(AbstractWikidataMixin):
    """
    Access Wikidata information via Wikimedia's API.
    """
    wikidata_site = pywikibot.Site("wikidata", "wikidata")

    @retry_with_fallback(triggering_error=KeyError, language="en")
    def get_matches(self, name, language):
        """
        Get matches for an entity's name on Wikidata.
        
        :param name: Name of entity.
        :type name: str
        :param language: Abbreviation of target language.
        :type language: str 
        :return: List of matches.
        :rtype: list
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
        
        :param wikidata_id: Wikidata ID of desired entity.
        :type wikidata_id: str
        :param language: Abbreviation of target language.
        :type language: str
        :param relevant_properties: Types of claims that should be included.
        :type relevant_properties: list
        :return: List of dates about every sense of the entity (un-ambiguous entities just will have one sense).
        :rtype: list
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
        
        :param claims: Dictionary with property ID as key and claim data as value.
        :type claims: dict
        :param language: Abbreviation of target language.
        :type language: str
        :param relevant_properties: Types of claims that should be included.
        :type relevant_properties: list
        :return: List of dates about every sense of the entity (un-ambiguous entities just will have one sense).
        """
        return {
            self.get_property_name(property_id, language=language):
                self.get_entity_name(claim[0]["mainsnak"]["datavalue"]["value"]["id"], language=language)
            for property_id, claim in claims.items()
            if property_id in relevant_properties
        }

    @retry_with_fallback(triggering_error=KeyError, language="en")
    def get_property_name(self, property_id, language):
        """
        Get the name of a wikidata property.
        
        :param property_id: Wikidata property ID.
        :type property_id: str
        :param language: Abbreviation of target language.
        :type language: str
        :return: Name of property.
        :rtype: str
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
        
        :param entity_id: Wikidata property ID.
        :type entity_id: str
        :param language: Abbreviation of target language.
        :type language: str
        :return: Name of entity.
        :rtype: str
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
        
        :param additional_request_parameters: Additional parameters for the request that is being sent to the API.
        :type additional_request_parameters: dict
        :return: Response following the request.
        :rtype: dict
        """
        request_parameters = {
            "site": self.wikidata_site,
            "action": 'wbgetentities',
            "format": 'json',
            "use_get": True,
            "throttle": False,
            "max_retries": 30,
            "maxlag": 20,
            "retry_wait": 20
        }

        request_parameters.update(additional_request_parameters)
        request = api.Request(**request_parameters)
        return request.submit()
