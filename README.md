# README

## BigWorldGraph

This project is dedicated to make today's political sphere more transparent, visualizing the links between entities in 
power. This is achieved by automatically extracting those links from texts, utilizing techniques from [Natural Language 
Processing](https://en.wikipedia.org/wiki/Natural_language_processing) and enriching those results with 
[Wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page).

The data can then be inspected afterwards using an interactive graph.

### General information

The prototype of this project was developed during an internship at [MAJ // Digital](http://maj.digital/) in Lisbon in 2017. 
It is open-source (see LICENSE.md) and hoped to be improved upon by other volunteers (see section Contributing for more 
information). 

The project is intended to work with all kinds of texts in different languages; however, the prototype was developed to 
work with a corpus composed of Wikipedia articles of (political) affairs in France since 1996.

#### Project description

The project consists of two main parts: The NLP pipeline, extracting links between entities from text and storing them 
in a graph database as well as the front end using a graph visualization library.

#### Contributing

Contributions of all forms, be it code contributions, bug reports or suggestions are welcome. Please read the 
CONTRIBUTE.md file for more information or visit the [project's GitHub page](https://github.com/majdigital/bigworldgraph).

### Usage

#### Pipeline

##### Installation

To install all necessary python packages to run the pipeline, execute the following command in your terminal in the projects 
root directory:

    pip3 install -r requirements.txt
    
You also have to have [Neo4j](https://neo4j.com/download/) installed.

##### Data

Theoretically, the data can be any kind of text. The only prerequisite is to provide the data in a shallow XML format, e.g.

    <doc id="123456" url="www.url-to-text.com" title="The title or headline of this text.">
        The text that is going to be processed comes here.
    </doc>
    
You could start with creating your own corpus from Wikipedia, downloading a [Wikipedia XML dump](https://dumps.wikimedia.org/)
and following the instructions of the [MW-Dumper](https://www.mediawiki.org/wiki/Manual:MWDumper).

For steps involving Natural Languages Processing, appropriate [Stanford NLP](https://stanfordnlp.github.io/CoreNLP/download.html) models are also required.

##### Writing your own pipeline tasks

If you want to modify existing pipeline tasks or write new ones, it is recommended to add a new module to the `nlp` package,
see e.g. `nlp/french_wikipedia.py` as reference. You can inherit tasks from other modules to solve common problems:

* `nlp/standard_tasks.py`: Standard NLP tasks like PoS tagging, Dependency Parsing etc.
* `nlp/corenlp_server_tasks.py`: Same standard NLP tasks, but using the `Stanford CoreNLP server` instead to speed up 
cumbersome and slow tasks.
* `nlp/wikipedia_tasks.py`: Reading an input file in the shallow `MW-Dumper` XML format; extracting addtional information 
from Wikidata.
* `nlp/additional_tasks.py`: Creating a file with information about the current pipeline run, writing relationships into 
a graph database and more.

With its standard configuration, the pipeline comprises the following tasks:

![](img/flowchart.png)

##### Adjusting pipeline_config.py

If you add a new kind of task to the pipeline, make sure to include a description of its necessary parameters in 
`pipeline_config.py`:

    CONFIG_DEPENDENCIES = {
        ...
        # Your task
        "my_new_task": [
             "{language}_SPECIFIC_PARAMETER", 
             "LANGUAGE_INDEPENDENT_PARAMETER"
        ],
        ...
    }
    
Then you have to include those declared parameters somewhere in your config file:

    # My config parameters
    ENGLISH_SPECIFIC_PARAMETER = 42
    LANGUAGE_INDPENENDENT_PARAMETER = "yada yada"
    
If you implement tasks that extend the pipeline to support other language, please add it to the following list:

    SUPPORTED_LANGUAGES = ["FRENCH", "ENGLISH"]
    
Finally, create a module for your own pipeline (e.g. `nlp/my_pipeline.py) and build the configuration before running the pipeline, using the 
pre-defined task names in `pipeline_config.py`: 

    import luigi
    from bwg.nlp.config_management import build_task_config_for_language
    
    class MyNewTask(luigi.Task):
        def requires():
            # Define task input here
            
        def output():
            # Define task output here
            
        def run():
            # Define what to do during the task here
            
    
    if __name__ == "__main__":
        task_config = build_task_config_for_language(
            tasks=[
                "my_new_task"
            ],
            language="english",
            config_file_path="path/to/pipeline_config.py"
        )
        
        # MyNewTask is the last task of the pipeline
        luigi.build(
            [MyNewTask(task_config=task_config)],
            local_scheduler=True, workers=1, log_level="INFO"
        )

##### Preparing

As the last step before running the pipeline, make sure to run the `StanfordCoreNLP` server in case you are using a task
from the module `nlp/corenlp_server_tasks.py`, using the following command in the directory with the appropriate Stanford
models (in this case the `-serverProperties` argument is used to tell the Server the language of incoming texts):

    java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000 -serverProperties StanfordCoreNLP-french.properties 
    
You also have to include at least this config parameter:

    STANFORD_CORENLP_SERVER_ADDRESS = "http://localhost:9000"
      
In case you are writing the data into a `Neo4j` database, make sure to include the following parameters

    # Neo4j
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "neo4j"
    NEO4J_NETAG2MODEL = {
        "I-PER": "Person",
        "I-LOC": "Location",
        "I-ORG": "Organization",
        "DATE": "Date",
        "I-MISC": "Miscellaneous"
    }
    
and remember to run the server before running the pipeline, either by running `Neo4j`'s [community edition](https://neo4j.com/download/),
executing the [`neo4j` shell](http://technoracle.blogspot.pt/2012/04/neo4j-installing-running-and-shell.html) in the terminal 
or using [docker images](https://neo4j.com/developer/docker/) etc.

In case you are using any task using `bwg/wikidata.py:WikidataAPIMixin`, e.g. `bwg/nlp/wikipedia_tasks.py:PropertiesCompletionTask`,
please include a `user-config.py` file in your directory for `pywikibot`

    mylang = "wikidata"
    family = "wikidata"
    usernames["wikidata"]["wikidata"] = u"BigWorldGraphBot"

##### Running the pipeline

To execute your pipeline, just run your module:

    python3 bwg/nlp/my_pipeline.py

#### Graph visualization

TODO: How to install and use

#### Server deployment

TODO: How to

## Warnings

* If you are using the project locally, on MacOS with Python > 3.4, you can only use one worker at a time for the 
pipline, otherwise running the pipeline will result in an exception being thrown.

curl -gX GET http://127.0.0.1:5000/entities?"uid"="c34b43b3f3f74aa99ae012615b904760"
 MATCH (n)-[r]-(m), (m)-[r2]-(o)
WHERE n.uid = 'c34b43b3f3f74aa99ae012615b904760' 
RETURN n, o, m