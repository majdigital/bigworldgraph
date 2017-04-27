people = {
    "item_title": "person",
    "resource_methods": ["GET", "DELETE"],
    "item_methods": ["GET", "PATCH", "PUT", "DELETE"]
}
locations = {
    "item_title": "location",
    "resource_methods": ["GET", "DELETE"],
    "item_methods": ["GET", "PATCH", "PUT", "DELETE"]
}
organizations = {
    "item_title": "organization",
    "resource_methods": ["GET", "DELETE"],
    "item_methods": ["GET", "PATCH", "PUT", "DELETE"]
}
dates = {
    "item_title": "date",
    "resource_methods": ["GET", "DELETE"],
    "item_methods": ["GET", "PATCH", "PUT", "DELETE"]
}
misc = {
    "item_title": "misc",
    "resource_methods": ["GET", "DELETE"],
    "item_methods": ["GET", "PATCH", "PUT", "DELETE"]
}
relations = {
    "item_title": "relations",
    "resource_methods": ["GET", "DELETE"],
    "item_methods": ["GET", "PATCH", "PUT", "DELETE"]
}
DOMAIN = {
    "people": people,
    "locations": locations,
    "organizations": organizations,
    "dates": dates,
    "misc": misc,
    "relations": relations,
}

# RELATION_BASE_CLASSES = ()
NODE_BASE_CLASSES = ("Entity", )
RELATION_TYPES = {"relations"}
NODE_TYPES = {"people", "locations", "organizations", "dates", "misc"}
NEO4J_USER = 'neo4j'
NEO4J_PASSWORD = 'neo4jj'
NEO4J_PORT = 7687
NEO4J_HOST = "localhost"

ITEM_URL = 'regex("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")'


