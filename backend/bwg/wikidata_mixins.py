# -*- coding: utf-8 -*-
"""
This module provides two different way to access Wikidata:
    * Through the Wikimedia API with ``Pywikibot`` as a wrapper
    * Over a scraper using ``BeautifulSoup4``
    
Currently, accessing the data via the API is faster than the scraper.
"""

# STD
import abc
import hashlib
import threading

# EXT
import pywikibot
from pywikibot.data import api

# PROJECT
from bwg.helpers import construct_dict_from_source
from bwg.serializing import retry_with_fallback


class RequestCache:
    """
    Special class used as a Cache, so that requests being made don't have to be repeated if they occurred in the past.
    """
    def __init__(self):
        self.lock = threading.Lock()
        self.cache = {}
        self.requested = set()
        self.number_of_requests = 0
        self.number_of_avoided_requests = 0

    def __contains__(self, item):
        return item in self.requested

    def __delitem__(self, key):
        del self.cache[key]
        self.requested.remove(key)

    def __getitem__(self, key):
        return self.cache[key]

    def __setitem__(self, key, value):
        self.cache[key] = value
        self.requested.add(key)

    def __enter__(self):
        self.lock.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lock.release()

    def __len__(self):
        return len(self.requested)

    def request(self, key, request_func, *request_args, **request_kwargs):
        """
        Make a request, but make a lookup to the cache first to see if you may be able to avoid it.

        :param key: Key that should be used to cache the request.
        :type key: str, int
        :param request_func: Function to do the request.
        :type request_func: func
        :param request_args: Arguments for request.
        :type request_args: tuple
        :param request_kwargs: Key word arguments for request.
        :type request_kwargs: dict
        """
        if key in self:
            self.number_of_avoided_requests += 1
            return self[key]

        request_result = request_func(*request_args, **request_kwargs)
        self.number_of_requests += 1

        self[key] = request_result

        return request_result


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
    def get_entity(self, wikidata_id, language, relevant_properties, properties_implying_relations):
        """
        Get Wikidata information about an entity based on its identifier.
        
        :param wikidata_id: Wikidata ID of desired entity.
        :type wikidata_id: str
        :param language: Abbreviation of target language.
        :type language: str
        :param relevant_properties: Types of claims that should be included.
        :type relevant_properties: list
        :param properties_implying_relations: Set of property IDs for properties that are not mere characteristics, but 
        imply other relations that should later be shown in the graph.
        :type properties_implying_relations: list, set
        :return: List of dates about every sense of the entity (un-ambiguous entites just will have one sense).
        :rtype: list
        """
        pass


class WikidataAPIMixin(AbstractWikidataMixin):
    """
    Access Wikidata information via Wikimedia's API.
    """
    wikidata_site = pywikibot.Site("wikidata", "wikidata")
    request_cache = RequestCache()
    match_cache = RequestCache()

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
    def get_entity(self, wikidata_id, language, relevant_properties, properties_implying_relations, recursively=True):
        """
        Get Wikidata information about an entity based on its identifier.
        
        :param wikidata_id: Wikidata ID of desired entity.
        :type wikidata_id: str
        :param language: Abbreviation of target language.
        :type language: str
        :param relevant_properties: Types of claims that should be included.
        :type relevant_properties: list
        :param properties_implying_relations: Dict of property IDs for properties that are not mere characteristics, but
        imply other relations that should later be shown in the graph. The properties are the keys and the entity node
        class they're implying are the values.
        :type properties_implying_relations: dict
        :param recursively: Request data for fof nodes recursively.
        :type recursively: bool
        :return: Wikidata entity as dictionary
        :rtype: dict
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
                        source["claims"], language=language,
                        relevant_properties=relevant_properties,
                        properties_implying_relations=properties_implying_relations,
                        recursively=recursively
                    ) if recursively else {}
                },
                entity
            )
            for id_, entity in response["entities"].items()
        ][0]

    @retry_with_fallback(triggering_error=KeyError, language="en")
    def resolve_claims(self, claims, language, relevant_properties, properties_implying_relations, recursively=True):
        """
        Resolve the claims (~ claimed facts) about a wikidata entity. 
        
        :param claims: Dictionary with property ID as key and claim data as value.
        :type claims: dict
        :param language: Abbreviation of target language.
        :type language: str
        :param relevant_properties: Types of claims that should be included.
        :type relevant_properties: list
        :param properties_implying_relations: Set of property IDs for properties that are not mere characteristics, but 
        imply other relations that should later be shown in the graph.
        :type properties_implying_relations: list, set
        :param recursively: Request data for fof nodes recursively.
        :type recursively: bool
        :return: List of dates about every sense of the entity (un-ambiguous entities just will have one sense).
        :rtype: list
        """
        properties = {}

        for property_id, claim in claims.items():
            if property_id in relevant_properties:
                property_name = self.get_property_name(property_id, language=language)

                if property_id != "P18":
                    target = self.get_entity_name(claim[0]["mainsnak"]["datavalue"]["value"]["id"], language=language)
                else:
                    # Handle images differently
                    target = self.get_image_url(claim[0]["mainsnak"]["datavalue"]["value"])

                property_data = {
                    "target": target,
                    "implies_relation": property_id in properties_implying_relations,
                    "entity_class": properties_implying_relations.get(property_id, None),
                }

                if property_id in properties_implying_relations:

                    target_senses = self.match_cache.request(
                        target, self.get_matches, target, language=language
                    )

                    property_data["target_data"] = [
                        self.request_cache.request(
                            target_sense["id"], self.get_entity,
                            target_sense["id"], language=language,
                            relevant_properties=relevant_properties,
                            properties_implying_relations=properties_implying_relations,
                            recursively=False
                        )
                        for target_sense in target_senses
                    ]
                else:
                    property_data["target_data"] = {}

                properties[property_name] = property_data

        return properties

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

    @staticmethod
    def get_image_url(image_name):
        """
        Generate Wikidata URL for a Wikidata image.

        :param image_name: Name of image as given by the API request.
        :type image_name: str
        :return: Link to image.
        :rtype: str
        """
        # See http://stackoverflow.com/questions/34393884/how-to-get-image-url-property-from-wikidata-item-by-api
        # for explanation
        image_name = image_name.replace(" ", "_")

        md5_sum = hashlib.md5(image_name.encode('utf-8')).hexdigest()

        return "https://upload.wikimedia.org/wikipedia/commons/{a}/{ab}/{image_name}".format(
            image_name=image_name, a=md5_sum[0], ab=md5_sum[0:2]
        )
