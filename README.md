# README

## R3

A description of the project, TODO

TODO: How to install it
TODO: How to use it
* How to edit the config


* Example Affairs in french wikipedia
* Download
* MWDumper (https://www.mediawiki.org/wiki/Manual:MWDumper)
    * time bzcat frwiki-20161001-pages-articles.xml.bz2 | java -jar mwdumper-1.25.jar --format=xml --filter=titlematch:Affaire.* > affaire_pages.xml
    * bzip2 fr_affaire_pages.xml 
    * Wikipedia extractor (https://github.com/bwbaugh/wikipedia-extractor)
    * bzcat fr_affaire_pages.xml.bz2 | python WikiExtractor.py -cb 250K -o extracted -
    * find extracted -name '*bz2' -exec bunzip2 -c {} \; > text.xml
    
Commenting two lines (219) in nltk/parse/stanford.py when using utf-8 corpus, otherwise dependency parsing breaks.

* Starting CoreNLP Server:
    * java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000 -serverProperties StanfordCoreNLP-french.properties 
    
Only 1 Worker on MacOS with Python > 3.4

user-config.py for pywikibot
