TEST_DICT = {
    "field1": True,
    "field2": 33,
    "field3": "hello",
    "field4": {
        "field4_1": {
            "field4_1_1": "nested"
        },
        "field4_2": False
    }
}

RAW_SENTENCE = "L’affaire Ibrahim Ali est une affaire criminelle française."

TAGGED_SENTENCE = [
    ('Alain', 'I-PER'), ('Juppé', 'I-PER'), ('est', 'O'), ('jugé', 'O'), ('pour', 'O'), ('sa', 'O'),
    ('responsabilité', 'O'), ('dans', 'O'), ('cette', 'O'), ('affaire', 'O'), ('comme', 'O'), ('supérieur', 'O'),
    ('hiérarchique', 'O'), ('et', 'O'), ('complice', 'O'), ('.', 'O')
]

SENTENCES = {
    '131397/00001': {
        'meta': {
            'id': '131397/00001',
            'type': 'sentence',
            'state': 'ne_tagged'
        },
        'data': [
            ("L'", 'O'), ('affaire', 'O'), ('du', 'O'), ('tribunal', 'O'), ('de', 'O'), ('Nice', 'I-LOC'),
            ('est', 'O'), ('une', 'O'), ('affaire', 'O'), ('de', 'O'), ('collusion', 'O'), ("d'", 'O'),
            ('intérêts', 'O'), ('de', 'O'), ('certains', 'O'), ('magistrats', 'O'), ('du', 'O'), ('tribunal', 'O'),
            ('de', 'O'), ('Nice', 'I-LOC'), (',', 'O'), ('révélée', 'O'), ('par', 'O'), ('le', 'O'),
            ('procureur', 'O'), ('du', 'O'), ('tribunal', 'O'), ('de', 'O'), ('Nice', 'O'), ('depuis', 'O'),
            ('1999', 'O'), (',', 'O'), ('Éric', 'O'), ('de', 'O'), ('Montgolfier', 'I-LOC'), ('.', 'O')
        ]
    },
    '131397/00002': {
        'meta': {
            'id': '131397/00002',
            'type': 'sentence',
            'state': 'ne_tagged'
        },
        'data': [
            ('Le', 'O'), ('juge', 'O'), ("d'", 'O'), ('instruction', 'O'), ('Jean-Paul', 'I-PER'), ('Renard', 'I-PER'),
            ('est', 'O'), ('un', 'O'), ('de', 'O'), ('ces', 'O'), ('magistrats', 'O'), ('mis', 'O'), ('en', 'O'),
            ('cause', 'O'), ('par', 'O'), ('Éric', 'O'), ('de', 'O'), ('Montgolfier', 'I-LOC'), ('.', 'O')
        ]
    },
    '131397/00003': {
        'meta': {
            'id': '131397/00003',
            'type': 'sentence',
            'state': 'ne_tagged'
        },
        'data': [
            ('Un', 'O'), ('rapport', 'O'), ('rédigé', 'O'), ('par', 'O'), ('Vincent', 'I-PER'), ('Lamanda', 'I-PER'),
            ('et', 'O'), ('rendu', 'O'), ('public', 'O'), ('par', 'O'), ('Le', 'O'), ('Journal', 'O'), ('du', 'O'),
            ('dimanche', 'O'), ('le', 'O'), ('10', 'O'), ('octobre', 'O'), ('met', 'O'), ('en', 'O'), ('cause', 'O'),
            ('des', 'O'), ('relations', 'O'), ('de', 'O'), ('proximité', 'O'), ('avec', 'O'), ('des', 'O'),
            ('figures', 'O'), ('du', 'O'), ('"', 'O'), ('milieu', 'O'), ('"', 'O'), ('et', 'O'), ('des', 'O'),
            ('élus', 'O'), ('visés', 'O'), ('par', 'O'), ('des', 'O'), ('procédures', 'O'), (',', 'O'), ('des', 'O'),
            ('interventions', 'O'), ('illégales', 'O'), ('dans', 'O'), ('des', 'O'), ('affaires', 'O'), ('en', 'O'),
            ('cours', 'O'), (':', 'O')
        ]
    },
    '131397/00004': {
        'meta': {
            'id': '131397/00004',
            'type': 'sentence',
            'state': 'ne_tagged'
        },
        'data': [
            ('Les', 'O'), ('rapports', 'O'), ('de', 'O'), ('Jean-Paul', 'I-PER'), ('Renard', 'I-PER'), ('et', 'O'),
            ('de', 'O'), ('Michel', 'I-PER'), ('Mouillot', 'I-PER'), (',', 'O'), ('ancien', 'O'), ('maire', 'O'),
            ('de', 'O'), ('Cannes', 'O'), (',', 'O'), ('sont', 'O'), ('aussi', 'O'), ('en', 'O'), ('cause', 'O'),
            (':', 'O'), ('ils', 'O'), ('se', 'O'), ('sont', 'O'), ('rencontrés', 'O'), ('à', 'O'), ('la', 'O'),
            ('Grande', 'O'), ('Loge', 'O'), ('nationale', 'O'), ('française', 'O'), ('(', 'O'), ('GLNF', 'O'),
            (')', 'O'), ('et', 'O'), ('Jean-Paul', 'I-PER'), ('Renard', 'I-PER'), ('a', 'O'), ('instruit', 'O'),
            ('des', 'O'), ('procédures', 'O'), ('pénales', 'O'), ('impliquant', 'O'), ('Michel', 'I-PER'),
            ('Mouillot', 'I-PER'), ('.', 'O')
        ]
    }
}

DEPENDENCY_TREE = {
    'nodes': {
        0: {
            'address': 0,
            'word': 'ROOT',
            'rel': None,
            'deps': {
                'ROOT': [8]
            }
        },
        8: {
            'address': 8,
            'word': 'terminé',
            'rel': 'ROOT',
            'deps': {
                'nsubj': [2],
                'dobj': [6],
                'aux': [7],
                'nmod': [10],
                'punct': [11]
            }
        },
        2: {
            'address': 2,
            'word': 'procès',
            'rel': 'nsubj',
            'deps': {
                'det': [1],
                'nmod': [5]
            }
        },
        1: {
            'address': 1,
            'word': 'Le',
            'rel': 'det',
            'deps': {}
        },
        5: {
            'address': 5,
            'word': 'instance',
            'rel': 'nmod',
            'deps': {
                'case': [3],
                'amod': [4]
            }
        },
        3: {
            'address': 3,
            'word': 'en',
            'rel': 'case',
            'deps': {}
        },
        4: {
            'address': 4,
            'word': 'première',
            'rel': 'amod',
            'deps': {}
        },
        6: {
            'address': 6,
            'word': "s'",
            'rel': 'dobj',
            'deps': {}
        },
        7: {
            'address': 7,
            'word': 'est',
            'rel': 'aux',
            'deps': {}
        },
        10: {
            'address': 10,
            'word': 'mercredi',
            'rel': 'nmod',
            'deps': {
                'det': [9]
            }
        },
        9: {
            'address': 9,
            'word': 'le',
            'rel': 'det',
            'deps': {}
        },
        11: {
            'address': 11,
            'word': '.',
            'rel': 'punct',
            'deps': {}
        }
    },
    'root': {
        'address': 8,
        'word': 'terminé',
        'rel': 'ROOT',
        'deps': {
            'nsubj': [2],
            'dobj': [6],
            'aux': [7],
            'nmod': [10],
            'punct': [11]
        }
    }
}

RELATIONS = [('il', 'exerçait', 'la fonction de maire de Paris')]

WIKIDATA_ENTITIES = [
    [
        {
            'description': 'commune française du département des Alpes-Maritimes (chef-lieu)',
            'id': 'Q33959',
            'label': 'Nice',
            'modified': '2017-05-24T16:45:26Z',
            'claims': {
                'pays': {
                    'target': 'France',
                    'implies_relation': False,
                    'entity_class': None,
                    'target_data': {}
                },
                'image': {
                    'target': "https://upload.wikimedia.org/wikipedia/commons/e/e7/Port_Of_Nice,_Côte_d'Azur.jpg",
                    'implies_relation': False,
                    'entity_class': None,
                    'target_data': {}
                },
                'connected_with': {
                    'target': 'Different entity',
                    'implies_relation': True,
                    'entity_class': 'Entity',
                    'target_data': {
                        "param": "test"
                    }
                }
            },
            'type': 'I-LOC'
        },
        {
            'description': 'nom de famille',
            'id': 'Q16878069',
            'label': 'Nice',
            'modified': '2017-02-21T06:46:01Z',
            'claims': {},
            'type': 'I-LOC'
        },
        {
            'description': "page d'homonymie d'un projet Wikimédia",
            'id': 'Q249634',
            'label': 'Nice',
            'modified': '2017-04-30T19:49:10Z',
            'claims': {},
            'type': 'I-LOC'
        },
        {
            'id': 'Q10600423',
            'label': 'Nice',
            'modified': '2016-07-14T08:19:04Z',
            'claims': {},
            'type': 'I-LOC'
        },
        {
            'id': 'Q12861045',
            'label': 'Nice',
            'modified': '2017-04-10T00:50:11Z',
            'claims': {},
            'type': 'I-LOC'
        },
        {
            'description': 'album de Rollins Band',
            'id': 'Q13653182',
            'label': 'Nice',
            'modified': '2017-03-09T23:26:34Z',
            'claims': {},
            'type': 'I-LOC'
        },
        {
            'id': 'Q16581992',
            'label': 'Nice',
            'modified': '2017-05-20T09:13:30Z',
            'claims': {},
            'type': 'I-LOC'
        }
    ]
]

#                           #########################################################
#                           ##                NLP Pipeline Fixtures                ##
#                           #########################################################

READING_TASK = {
    "input": [
        '<doc id="12345" url="https://web.site" title="Sample article">',
        '<!---',
        'Comment in sample article',
        '-->',
        'Sample article',
        '',
        'First sample article sentence',
        'This is the second sample article sentence.',
        '</doc>'
    ],
    "output": [
        {
            "meta": {
                "id": "12345",
                "url": "https://web.site",
                "title": "Sample article",
                "type": "article",
                "state": "parsed"
            },
            "data": {
                "12345/00001": {
                    "meta": {
                        "id": "12345/00001",
                        "type": "sentence",
                        "state": "parsed"
                    },
                    "data": "First sample article sentence"
                },
                "12345/00002": {
                    "meta": {
                        "id": "12345/00002",
                        "type": "sentence",
                        "state": "parsed"
                    },
                    "data": "This is the second sample article sentence."
                }
            }
        }
    ]
}

# TODO (Implement): Add test data [DU 20.06.17]
NER_TASK = {
    "input": READING_TASK["output"],
    "output": []
}

# TODO (Implement): Add test data [DU 20.06.17]
DEPENDENCY_TASK = {
    "input": READING_TASK["output"],
    "output": []
}

# TODO (Implement): Add test data [DU 20.06.17]
POS_TAGGING_TASK = {
    "input": READING_TASK["output"],
    "output": []
}

# TODO (Implement): Add test data [DU 20.06.17]
NAIVE_OPEN_RELATION_EXTRACTION_TASK = {
    "input": [],
    "output": []
}

# TODO (Implement): Add test data [DU 20.06.17]
PARTICIPATION_EXTRACTION_TASK = {
    "input": [],
    "output": []
}
