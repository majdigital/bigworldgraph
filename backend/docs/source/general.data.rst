Data
====

All kinds of data (input corpora, pipeline output files, stanford models) are by default stored in ``backend/data/`` in
folders called ``stanford``, ``corpora_<language>`` and ``pipeline_<language>`` accordingly. This behaviour can be changed
by changing the pipeline's config.

Input data
~~~~~~~~~~

Theoretically, the input data can be any kind of text. The only prerequisite
is to provide the data in a shallow XML format, e.g.

::

    <doc id="123456" url="www.url-to-text.com" title="The title or headline of this text.">
        The text that is going to be processed comes here.
    </doc>

You could start with creating your own corpus from Wikipedia,
downloading a `Wikipedia XML dump <https://dumps.wikimedia.org/>`__ and
following the instructions of the
`MW-Dumper <https://www.mediawiki.org/wiki/Manual:MWDumper>`__.

For steps involving Natural Languages Processing, appropriate `Stanford
NLP <https://stanfordnlp.github.io/CoreNLP/download.html>`__ models are
also required.

Task outputs
~~~~~~~~~~~~

The pipeline tasks output their results as ``JSON`` files. They have the following structure:

::

    {
        "meta": {
            "id": "49937",
            "url": "https://fr.wikipedia.org/wiki?curid=49937",
            "title": "Affaire des emplois fictifs de la mairie de Paris",
            "type": "article", "state": "parsed"
        },
        "data": {
            "49937/00001": {
                "meta": {
                    "id": "49937/00001",
                    "type": "sentence",
                    "state": "parsed"
                },
                "data": "L'affaire des emplois fictifs de la mairie de Paris, ou « affaire des emplois fictifs du RPR », ou encore « affaire des chargés de mission de la ville de Paris », instruite par les juges Patrick Desmure puis Alain Philibeaux, concerne sept employés permanents du RPR, dont le salaire a été payé par le conseil municipal de Paris."
            },
            ...
        }
    }

Usually, the ``JSON`` isn't written into the file in this prettified and humanly-readable way, but just as one line, with
one article in the corpus corresponding to one line in the output file.

Intuitively, the ``meta`` field gives information about the current ``article`` or ``sentence`` while ``data`` contains
the actual content. The IDs for sentences are created by concatenating the article ID with a simple sentence count.

Depending on the kind of task, the ``data`` field of a sentence can be of a different data type. In this case it's a
simple string, but lists and dictionaries are possible as well.
