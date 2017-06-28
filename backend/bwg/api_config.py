# Logging
import logging

# General config
DEBUG = True

# API resource config
# TODO (Improve) Add more methods for resources [DU 28.04.17]
entities = {
    "item_title": "entity",
    "resource_methods": ["GET"],
    "item_methods": ["GET"]
}
people = {
    "item_title": "person",
    "resource_methods": ["GET"],
    "item_methods": ["GET"]
}
parties = {
    "item_title": "party",
    "resource_methods": ["GET"],
    "item_methods": ["GET"]
}
companies = {
    "item_title": "company",
    "resource_methods": ["GET"],
    "item_methods": ["GET"]
}
locations = {
    "item_title": "location",
    "resource_methods": ["GET"],
    "item_methods": ["GET"]
}
organizations = {
    "item_title": "organization",
    "resource_methods": ["GET"],
    "item_methods": ["GET"]
}
affairs = {
    "item_title": "affair",
    "resource_methods": ["GET"],
    "item_methods": ["GET"]
}
politicians = {
    "item_title": "politician",
    "resource_methods": ["GET"],
    "item_methods": ["GET"]
}
businesspeople = {
    "item_title": "businessperson",
    "resource_methods": ["GET"],
    "item_methods": ["GET"]
}
media = {
    "item_title": "media",
    "resource_methods": ["GET"],
    "item_methods": ["GET"]
}
journalists = {
    "item_title": "journalist",
    "resource_methods": ["GET"],
    "item_methods": ["GET"]
}
dates = {
    "item_title": "date",
    "resource_methods": ["GET"],
    "item_methods": ["GET"]
}
misc = {
    "item_title": "misc",
    "resource_methods": ["GET"],
    "item_methods": ["GET"]
}

DOMAIN = {
    "entities": entities,
    "people": people,
    "locations": locations,
    "organizations": organizations,
    "dates": dates,
    "misc": misc,
    "parties": parties,
    "affairs": affairs,
    "politicians": politicians,
    "businesspeople": businesspeople,
    "journalists": journalists,
    "media": media,
    "companies": companies
}
PAGINATION_LIMIT = 10001
PAGINATION_DEFAULT = 10000

# RELATION_BASE_CLASSES = ()
NODE_BASE_CLASSES = ("Entity", )
RELATION_TYPES = {"relations"}
NODE_TYPES = DOMAIN.keys()
NEO4J_USER = 'neo4j'
NEO4J_PASSWORD = 'neo4jj'
NEO4J_PORT = 7687
NEO4J_HOST = "localhost"

ITEM_URL = 'regex("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")'
API_HOST = "localhost"

# Logging config
LOGGING_PATH = "../logs/api_log.txt"
LOGGING_LEVEL = logging.DEBUG
TEST_PARAM = "test"
