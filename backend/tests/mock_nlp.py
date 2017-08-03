class MockTokenizer:
    @staticmethod
    def tokenize(sentence_data):
        return sentence_data.split(" ")  # Yes, yes, very sophisticated


class MockTagger:
    def __init__(self, naive_tag_rule):
        assert callable(naive_tag_rule)
        self.naive_tag_rule = naive_tag_rule

    def tag(self, tokenized_sentence):
        return [self.naive_tag_rule(token.lower(), tokenized_sentence) for token in tokenized_sentence]


class MockParser:
    @staticmethod
    def raw_parse(sentence_data):
        tokens = sentence_data.split(" ")

        return {
            "root": {
                "address": 0
            },
            "nodes": {
                node_id: {
                    "address": node_id,
                    "word": "ROOT" if node_id == 0 else tokens[node_id - 1],
                    "rel": None if node_id == 0 else node_id - 1,
                    "deps": {
                        "rel": node_id + 1
                    }
                }
                for node_id in range(len(tokens) + 1)
            }
        }
