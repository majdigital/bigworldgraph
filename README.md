
![](./img/logo.png)

___

**DISCLAIMER**: **This project is still in development and hasn't produced a stable version yet**.

___

[![Documentation Status](https://readthedocs.org/projects/bigworldgraph/badge/?version=latest)](http://bigworldgraph.readthedocs.io/?badge=latest)
[![Code Health](https://landscape.io/github/majdigital/bigworldgraph/develop/landscape.svg?style=flat)](https://landscape.io/github/majdigital/bigworldgraph/develop)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://img.shields.io/badge/license-MIT-blue.svg)
[![Open Issues](https://img.shields.io/github/issues/majdigital/bigworldgraph.svg)](https://img.shields.io/github/issues/majdigital/bigworldgraph.svg)

# BigWorldGraph

This project is dedicated to make today's political sphere more transparent, visualizing the links between entities in 
power. This is achieved by automatically extracting those links from texts, utilizing techniques from [Natural Language 
Processing](https://en.wikipedia.org/wiki/Natural_language_processing) and enriching those results with 
[Wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page).

The data can then be inspected afterwards using an interactive graph.


## General information

The prototype of this project was developed during an internship at [MAJ // Digital](http://maj.digital/) in Lisbon in 2017. 
It is open-source (see `LICENSE.md`) and hoped to be improved upon by other volunteers (see section Contributing for more 
information). 

The project is intended to work with all kinds of texts in different languages; however, the prototype was developed to 
work with a corpus composed of Wikipedia articles of (political) affairs in France since 1996.

To see what future features are planned to be included in this project, check `TODO.md`.

### Project description

The project consists of two main parts: The NLP pipeline, extracting links between entities from text and storing them 
in a graph database as well as the front end using a graph visualization library.

### Contributing

Contributions of all forms, be it code contributions, bug reports or suggestions are welcome. Please read the 
`CONTRIBUTE.md` file for more information or visit the [project's GitHub page](https://github.com/majdigital/bigworldgraph).

### Documentation

Documentation is hosted on *Readthedocs* and can be found [here](http://bigworldgraph.readthedocs.io/). 
There you can find more information about how the pipeline is used, how the data in your input corpus is supposed to 
look and what to expect as intermediate results from the pipeline tasks.

## Usage

### Installation

Clone the project from Github using the following command:

    git clone https://github.com/majdigital/bigworldgraph.git

### Testing

To test the project, execute the following commands in the project's root directory

    docker-compose -f docker-compose-test.yml build --no-cache
    docker-compose -f docker-compose-test.yml up
    
### Quickstart

There are two things you can do right after cloning the repository:

1. Running a demo pipeline to see how the pipeline in this project is supposed to work.
2. Building the project and playing around with some toy data on the frontend.

#### Running the demo pipeline

To run the demo pipeline, execute 

    python3 backend/bwg/demo_pipeline.py
    
Your terminal should show you the following on successful execution:

    ===== Luigi Execution Summary =====
    
    Scheduled 4 tasks of which:
    * 4 ran successfully:
        - 1 DemoTask1(...)
        - 1 DemoTask2(...)
        - 1 DemoTask3(...)
        - 1 SimpleReadingTask(...)
    
    This progress looks :) because there were no failed tasks or missing external dependencies
    
    ===== Luigi Execution Summary =====

To see the results of your pipeline, go to ``backend/data/pipeline_demo``: There you can the output of different 
pipeline tasks. The output of the final task, ``demo_corpus_replaced.json``, is written in prettified ``JSON`` to 
enhance readability.

If you want to know more about how the demo pipeline works, visit this [site](http://bigworldgraph.readthedocs.io/bwg.demo_pipeline.html) in the project's documentation.

#### Building the project with toy data

Building is handled by [Docker](https://www.docker.com/), so make sure to have it installed beforehand.  
Afterwards, the project setup is fairly simple. Just go the root directory of the project and execute the following command:

    docker-compose build && docker-compose up
    
The building of the docker images in this project might take a while, especially during the first time you're using this
project. requests to the API using port `6050` by default (see the documentation for [`bwg/run_api.py`](http://bigworldgraph.readthedocs.io/bwg.run_api.html)
for more information).

Now you can play around on the frontend by visiting [127.0.0.1:8080](127.0.0.1:8080) on your browser!

#### Getting serious: Running the real pipeline

First of all, make sure to have the corpus file in its designated directory (``backend/data/corpora_french/`` by default).

Set up the project like in the previous step with 

    docker-compose build && docker-compose up

After all containers are running, you can run the pipeline by executing the following:

    cd ./pipeline/
    docker build . -t pipeline
    docker run -v /var/run/docker.sock:/var/run/docker.sock -v `pwd`/stanford/models/:/stanford_models/ --name pipeline pipeline
    
If you are on a Windows system, replace `pwd` inside the `-v` flag with the **absolute** path to the `stanford/models` 
 directory.

First of all, all the necessary Stanford models will be downloaded from a MAJ server to ``/pipeline/stanford/models`` if necessary. 
This might take a while.
Afterwards, the pipeline will be started. Depending on the size of the corpus file and the tasks in the pipeline, run time
can also vary heavily. 

The final output of the pipeline should look something like this: 

    ===== Luigi Execution Summary =====

    Scheduled 4 tasks of which:
    * 3 present dependencies were encountered:
        - 1 FrenchPipelineRunInfoGenerationTask(...)
        - 1 FrenchServerPropertiesCompletionTask(...)
        - 1 FrenchServerRelationMergingTask(...)
    * 1 ran successfully:
        - 1 FrenchRelationsDatabaseWritingTask(...)
    
    This progress looks :) because there were no failed tasks or missing external dependencies
    
    ===== Luigi Execution Summary =====

Now go to [127.0.0.1:8080](127.0.0.1:8080) again and marvel at your graph!
