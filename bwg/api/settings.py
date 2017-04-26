nodes = {
    "item_title": "node",
    "resource_methods": ["GET", "PUT", "DELETE"],
    "item_methods": ["GET", "PATCH", "PUT", "DELETE"]
}
edges = {
    "item_title": "edge",
    "resource_methods": ["GET", "PUT", "DELETE"],
    "item_methods": ["GET", "PATCH", "PUT", "DELETE"]
}
DOMAIN = {
    "nodes": nodes,
    "edges": edges
}

GRAPH_DATABASE = 'http://localhost:7687/db/data/'
GRAPH_USER = 'neo4j'
GRAPH_PASSWORD = 'neo4jj'

ITEM_URL = 'regex("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")'


