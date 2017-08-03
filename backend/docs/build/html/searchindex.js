Search.setIndex({docnames:["bwg","bwg.additional_tasks","bwg.config_management","bwg.corenlp_server_tasks","bwg.demo_pipeline","bwg.french_wikipedia","bwg.helpers","bwg.mixins","bwg.neo4j_extensions","bwg.run_api","bwg.standard_tasks","bwg.utilities","bwg.wikidata","bwg.wikipedia_tasks","general","general.data","general.pipeline","index"],envversion:51,filenames:["bwg.rst","bwg.additional_tasks.rst","bwg.config_management.rst","bwg.corenlp_server_tasks.rst","bwg.demo_pipeline.rst","bwg.french_wikipedia.rst","bwg.helpers.rst","bwg.mixins.rst","bwg.neo4j_extensions.rst","bwg.run_api.rst","bwg.standard_tasks.rst","bwg.utilities.rst","bwg.wikidata.rst","bwg.wikipedia_tasks.rst","general.rst","general.data.rst","general.pipeline.rst","index.rst"],objects:{"bwg.config_management":{MissingConfigParameterException:[2,1,1,""],UnsupportedLanguageException:[2,1,1,""],build_task_config_for_language:[2,2,1,""],format_config_parameter:[2,2,1,""],format_task_config_key:[2,2,1,""],get_config_from_py_file:[2,2,1,""],overwrite_local_config_with_environ:[2,2,1,""]},"bwg.helpers":{construct_dict_from_source:[6,2,1,""],download_nltk_resource_if_missing:[6,2,1,""],fast_copy:[6,2,1,""],filter_dict:[6,2,1,""],flatten_dictlist:[6,2,1,""],get_if_exists:[6,2,1,""],is_collection:[6,2,1,""],seconds_to_hms:[6,2,1,""]},"bwg.mixins":{ArticleProcessingMixin:[7,3,1,""],CoreNLPServerMixin:[7,3,1,""]},"bwg.mixins.ArticleProcessingMixin":{is_relevant_article:[7,4,1,""],is_relevant_sentence:[7,4,1,""],process_articles:[7,4,1,""],task_config:[7,5,1,""],task_workflow:[7,4,1,""],workflow_resources:[7,5,1,""]},"bwg.mixins.CoreNLPServerMixin":{process_sentence_with_corenlp_server:[7,4,1,""],server:[7,5,1,""],task_config:[7,5,1,""],workflow_resources:[7,5,1,""]},"bwg.neo4j_extensions":{Entity:[8,3,1,""],EveCompatibilityMixin:[8,3,1,""],Neo4jDatabase:[8,3,1,""],Neo4jLayer:[8,3,1,""],Neo4jResult:[8,3,1,""],Neo4jTarget:[8,3,1,""],PipelineRunInfo:[8,3,1,""],Relation:[8,3,1,""]},"bwg.neo4j_extensions.Entity":{DoesNotExist:[8,1,1,""],category:[8,5,1,""],data:[8,5,1,""],label:[8,5,1,""],relations:[8,5,1,""],uid:[8,5,1,""],weight:[8,5,1,""]},"bwg.neo4j_extensions.Neo4jDatabase":{find_friends_of_friends:[8,6,1,""],find_nodes:[8,4,1,""],get_node_class:[8,6,1,""],get_or_create_connection:[8,6,1,""],get_or_create_node:[8,6,1,""]},"bwg.neo4j_extensions.Neo4jLayer":{aggregate:[8,4,1,""],combine_queries:[8,4,1,""],find:[8,4,1,""],find_list_of_ids:[8,4,1,""],find_one:[8,4,1,""],find_one_raw:[8,4,1,""],get_value_from_query:[8,4,1,""],init_app:[8,4,1,""],insert:[8,4,1,""],is_empty:[8,4,1,""],node_base_classes:[8,5,1,""],node_base_classes_names:[8,5,1,""],node_types:[8,5,1,""],query_contains_field:[8,4,1,""],relation_base_classes:[8,5,1,""],relation_base_classes_names:[8,5,1,""],relation_types:[8,5,1,""],remove:[8,4,1,""],replace:[8,4,1,""],update:[8,4,1,""]},"bwg.neo4j_extensions.Neo4jResult":{clean_unserializables:[8,4,1,""],count:[8,4,1,""],is_json_serializable:[8,6,1,""],return_selection:[8,5,1,""]},"bwg.neo4j_extensions.Neo4jTarget":{add_relation:[8,4,1,""],categorize_node:[8,4,1,""],exists:[8,4,1,""]},"bwg.neo4j_extensions.PipelineRunInfo":{DoesNotExist:[8,1,1,""],article_ids:[8,5,1,""],run_id:[8,5,1,""],timestamp:[8,5,1,""],uid:[8,5,1,""]},"bwg.neo4j_extensions.Relation":{data:[8,5,1,""],label:[8,5,1,""],weight:[8,5,1,""]},bwg:{config_management:[2,0,0,"-"],french_wikipedia:[5,0,0,"-"],helpers:[6,0,0,"-"],mixins:[7,0,0,"-"],neo4j_extensions:[8,0,0,"-"],wikidata:[12,0,0,"-"]}},objnames:{"0":["py","module","Python module"],"1":["py","exception","Python exception"],"2":["py","function","Python function"],"3":["py","class","Python class"],"4":["py","method","Python method"],"5":["py","attribute","Python attribute"],"6":["py","staticmethod","Python static method"]},objtypes:{"0":"py:module","1":"py:exception","2":"py:function","3":"py:class","4":"py:method","5":"py:attribute","6":"py:staticmethod"},terms:{"20z":9,"31t03":9,"42904ca7f582449eafb98c1e94cd8b0d":9,"\u00e9t\u00e9":15,"break":8,"case":[2,3,8,15,16],"catch":6,"charg\u00e9":15,"class":[0,2,4,7,8,16,17],"default":[2,6,15,16,17],"employ\u00e9":15,"final":[2,4,5,7,8,16,17],"float":6,"function":[0,2,6,7,8,9,16,17],"import":[2,4,16],"int":6,"new":[2,4,6,8,16],"pay\u00e9":15,"return":[2,6,7,8,9],"static":8,"true":[2,4,7,8,16],"try":16,"var":[16,17],"while":[8,15,16,17],Eve:[0,8,9,17],For:[3,4,8,15],IDs:15,Its:2,PoS:16,The:[0,2,4,5,7,8,14,15,17],Then:[2,4,16],There:17,Used:8,Using:[0,17],With:16,__main__:[2,4,16],__name__:[2,4,16],_id:8,_io:7,_item:9,_specific_paramet:[2,4,16],about:[5,8,14,15,16,17],abov:[7,8],absolut:[16,17],access:8,accord:8,accordingli:15,achiev:[8,17],action:7,actual:[7,8,15],add:[2,4,8,16],add_rel:8,added:8,adding:2,addit:[7,8],additional_task:[0,16,17],addtion:16,adipisc:4,adjust:[0,3,14,17],advantag:8,affair:[5,9,15,17],after:[7,16,17],afterward:[5,7,16,17],again:[7,17],aggreg:8,agnost:2,alain:15,aliqua:4,aliquip:4,all:[2,5,6,7,8,15,16,17],allow:8,along:7,alreadi:8,also:[3,7,9,15,17],altern:8,although:8,amet:4,ani:[2,7,8,9,15],anim:4,annot:7,anoth:7,anymor:8,api:[0,8,9,16,17],app:8,appli:[7,8],appropri:[3,15],aren:6,arg:[2,8],argument:[3,7],around:[5,17],arrayproperti:8,articl:[4,5,7,15,17],article_id:8,articleprocessingmixin:7,assign:8,attribut:8,aut:4,automat:17,backend:[3,15,17],background:16,backstori:[0,17],base:[2,7,8],base_class:8,basi:5,becaus:[2,8,9,17],been:8,befor:[2,4,7,16],beforehand:17,behaviour:15,being:[2,7,8],better:8,between:17,big:9,bigworldgraph:[4,9],book:7,bool:[2,6,7,8],both:8,bridg:8,browser:17,bug:17,build:[2,4,9,16],build_task_config_for_languag:[2,4,16],businesspeopl:9,bwg:[0,16,17],cach:17,call:[2,3,7,8,15],can:[0,3,4,7,8,9,15,16,17],carri:7,categor:8,categori:[8,9],categorization_funct:8,categorize_nod:8,caus:8,certain:[2,8],chang:[8,15],chapter:7,charact:4,check:[6,7,8,17],cillum:4,ciux:4,claim:9,class_nam:8,claud:9,clean:8,clean_unserializ:8,client_project:8,clone:17,code:17,collect:[6,8],com:[4,9,15,17],combine_queri:8,come:15,command:[3,9,17],commodo:4,common:16,commun:7,compani:9,compat:[0,8,17],compil:5,complet:[7,16],complex:8,complic:8,compos:[3,9,16,17],compound:8,compris:[4,5,9,16],concaten:15,concern:[2,15],condit:8,config:[2,4,7,9,15,16],config_depend:[2,4,16],config_file_path:[2,4,16],config_manag:[0,4,16,17],config_paramet:2,config_path:2,configur:[0,14,17],connect:[8,9,17],consectetur:4,conseil:15,consequat:4,consid:[7,8],consider:8,consist:[7,17],constraint:8,construct:6,construct_dict_from_sourc:6,consult:3,consum:8,contain:[0,2,7,8,9,15,16,17],content:15,context:4,convert:6,coonnsectetu:4,coonnsequxt:4,cooxxoodoo:4,copi:[6,8],copyright:9,core:[7,8],corenlp:[0,7,16,17],corenlp_server_task:[0,16,17],corenlpservermixin:7,corpora:15,corpora_:15,corpora_demo:4,corpora_french:17,corpu:[0,3,4,5,9,15,17],correspond:[2,3,7,8,15],correspondingli:7,could:[8,15],count:[8,15],creat:[0,4,5,6,8,15,16,17],creator:5,criteria:8,criterion:7,cuidxtxt:4,culpa:4,cumbersom:16,cupidatat:4,curid:15,curl:9,current:[2,3,7,8,9,15,16],cux:4,data:[2,3,4,5,7,8,9,14],databas:[0,2,8,9,16,17],datalay:8,dataset:5,datasourc:8,datastor:8,date:2,deal:8,declar:[2,4,16],dedic:17,def:[2,4,7,16],defin:[2,4,7,8,16],definit:8,delet:8,demo:4,demo_corpu:4,demo_corpus_remov:4,demo_corpus_replac:17,demo_pipelin:[0,17],demo_pipeline_config:4,demotask1:[4,17],demotask2:[4,17],demotask3:[4,17],denot:7,depend:[15,16,17],des:15,describ:7,descript:[2,4,7,9,16],deserunt:4,deseunnt:4,design:17,desir:6,desmur:15,destin:8,determin:8,develop:17,dict:[2,6,7,8],dictionari:[2,6,7,8,15],dictlist:6,dictparamet:7,differ:[7,15,17],digit:[3,5,17],directli:8,directori:[9,16,17],disclaim:17,doc:[4,15],doc_or_doc:8,docker:[3,9,16,17],dockerfil:3,docstr:8,document:[3,8,9,16],doe:8,doesn:8,doesnotexist:8,doing:16,dolor:4,don:8,done:7,dont:15,doo:4,doooo:4,dooooe:4,download:[3,6,15,17],download_nltk_resource_if_miss:6,dreyfu:9,driver:8,duh:7,dui:4,dump:[5,15],dumper:[15,16],duplic:4,dure:[2,4,16,17],each:7,easi:8,eehenndeit:4,eit:4,eiusmod:4,eiusxood:4,elect:5,elit:4,emploi:15,empti:8,enabl:7,encor:15,encount:17,end:[7,8,17],endpoint:[8,9],engin:8,english:[2,4,16],english_specific_paramet:[2,4,16],enhanc:17,enim:4,ennix:4,enrich:17,entir:8,entiti:[8,9,17],entity_class:8,entity_properti:8,entri:[5,6,7,8],environ:2,especi:[16,17],ess:4,est:4,etc:[8,16],eve:8,eve_neo4j:8,evecompabilitymixin:8,evecompatibilitymixin:8,even:16,everi:[2,7],exampl:[0,4,6,8,16,17],except:[2,8],excepteur:4,exceteu:4,execitxtioonn:4,execut:[8,16,17],exercit:4,exist:[2,8,16],expect:[7,17],explain:16,express:8,extend:[2,4,8,16],extens:[0,17],extern:17,extract:[6,7,16,17],fail:17,fairli:17,fals:[7,8],far:9,fast:6,fast_copi:6,featur:[0,8,17],fictif:15,field:[6,7,8,15],field_nam:8,file:[2,4,7,9,15,16,17],fill:9,filter:[5,6,7,8,9],filter_dict:6,find:[8,17],find_friends_of_friend:8,find_list_of_id:8,find_nod:8,find_on:8,find_one_raw:8,first:[8,16,17],first_fil:7,fit:[3,7],flag:[2,7,16,17],flask_neo4j:8,flatten:6,flatten_dictlist:6,fly:8,folder:[9,15],follow:[0,2,4,5,7,9,15,16,17],forget:8,form:[7,17],format:[2,15,16],format_config_paramet:2,format_task_config_kei:2,found:[6,8,17],franc:17,french:[0,2,3,4,5,16,17],french_wikipedia:[0,16,17],frenchpipelineruninfogenerationtask:17,frenchrelationsdatabasewritingtask:17,frenchserverpropertiescompletiontask:17,frenchserverrelationmergingtask:17,friend:[8,9],from:[2,3,4,5,6,7,8,15,16,17],front:17,frontend:17,fugiat:4,fugixt:4,fulfil:8,func:7,furthermor:7,futur:17,gap:8,get:[5,6,7,8,9],get_config_from_py_fil:2,get_if_exist:6,get_node_class:8,get_or_create_connect:8,get_or_create_nod:8,get_value_from_queri:8,git:17,github:[4,9,17],give:15,given:[2,8],going:[6,8,15],graph:[8,9,16,17],grumberg:9,handl:17,has:8,hasn:17,have:[2,4,8,15,16,17],headlin:[7,15],heavili:17,help:[0,3,16,17],helper:[0,8,17],here:[2,4,7,8,15,16,17],hit:8,hope:17,host:[8,17],hour:6,how:[2,4,7,16,17],howev:[7,17],html:17,http:[4,9,15,17],human:9,humanli:15,id_:8,id_field:8,identifi:[6,8,9],identifier_valu:8,ids:8,illustr:[4,5],imag:[16,17],implement:[2,4,7,8,9,16],improv:17,incididunt:4,includ:[0,2,4,5,7,8,16,17],include_opt:2,index:17,indic:7,info:[4,16],inform:[8,9,14,15,16],inherit:[7,8,16],init_app:8,initi:7,inn:4,inncididunnt:4,input:[2,4,7,14,16,17],insert:8,insid:[16,17],inspect:17,instanc:[7,8],instead:[6,16],instruct:15,instruit:15,integerproperti:8,intend:17,interact:17,interest:8,interfac:8,intermedi:17,internship:17,intersect:8,intuit:[7,15],involv:[0,15,17],ipsum:4,irur:4,is_collect:6,is_empti:8,is_json_serializ:8,is_relevant_articl:7,is_relevant_sent:7,isn:[8,15],isux:4,item:8,iter:[6,7],its:[2,3,4,6,9,16,17],iue:4,jean:9,json:[4,7,8,15,17],jsonproperti:8,juge:15,just:[2,8,9,15,16,17],keep_field:6,kei:[6,7,8],keyerror:6,kind:[2,4,7,9,15,16,17],know:[2,8,17],kwarg:[2,8],label:[8,9],labor:4,labori:4,laborum:4,lambda:8,languag:[2,3,4,6,7,15,16,17],language_independent_paramet:[2,4,16],language_indpenendent_paramet:[2,4,16],last:[2,4,7,16],layer:8,lda:9,lead:[6,7,8],les:15,librari:[8,17],licens:[9,17],like:[4,8,9,16,17],line1:7,line2:7,line:[7,15],link:[6,9,17],lisbon:17,list:[2,4,6,7,8,15,16],live:17,load:2,loc:2,local:2,local_schedul:[2,4,16],localhost:8,locat:[2,9],log_level:[4,16],looex:4,look:[4,8,17],lookup:8,lorem:4,los:2,luigi:[0,2,4,7,8,16,17],magna:4,mai:7,main:7,mainli:8,maintain:8,mairi:15,maj:[3,5,17],majdigit:[4,9,17],make:[0,2,4,5,7,8,9,16,17],malabaristalici:9,manag:2,manual:5,marvel:17,match:8,mean:[7,8],media:[7,9],meta:[2,4,7,15],metadata:7,method:8,might:[7,16,17],minim:[0,4,16,17],minut:6,misalign:7,misc:[2,9],miscellan:2,miss:[2,6,17],missingconfigparameterexcept:2,mission:15,mixin:[0,17],mode:8,model:[3,8,15,16,17],modifi:16,modul:16,mollit:4,mongo:8,more:[3,8,9,16,17],most:8,mostli:[0,8,17],motiv:[0,17],movi:7,msg:8,municip:15,must:8,my_new_task:[2,4,16],my_pipelin:[2,4,16],my_pipeline_config:2,mynewtask:[2,4,16],name:[2,4,6,7,8,16,17],natur:[6,7,15,17],necessari:[2,4,7,16,17],need:8,neo4j:[0,2,8,17],neo4j_extens:[0,17],neo4j_netag2model:2,neo4j_password:2,neo4j_us:2,neo4jdatabas:8,neo4jlay:8,neo4jresult:8,neo4jtarget:8,neomodel:8,nest:6,new_stat:7,newspap:7,nfor:9,nisi:4,nlp:[0,2,3,4,7,15,16,17],nltk:6,nnisi:4,nnoonn:4,nnoostud:4,nnux:4,node:[8,9],node_base_class:8,node_base_classes_nam:8,node_categori:8,node_class:8,node_relevance_funct:8,node_typ:8,non:[3,4],none:[6,7,8],nostrud:4,notic:8,now:[7,17],nulla:4,number:[6,7],obj:6,obj_ent:8,object:[6,7,8],obligatori:[0,17],occaecat:4,occur:8,offici:3,officia:4,often:[0,17],one:[7,8,15],ones:[7,16],onli:[5,7,8,9,15],only_include_relevant_articl:7,only_include_relevant_sent:7,ooccxecxt:4,oofficix:4,ooidennt:4,open:[7,8,17],oper:8,optim:8,option:[2,8],order:8,org:[2,15],organ:[2,9],origin:[4,5,8],originalchangederror:8,other:[2,4,6,7,8,9,16,17],otherwis:[2,8],output:[2,4,7,8,14,16,17],output_fil:7,overwrit:[2,7],overwrite_local_config_with_environ:2,overwritten:8,own:[0,4,14,15,17],packag:16,page:[8,17],par:15,paragraph:7,paramet:[2,4,6,7,8,9,16],pari:15,pariatur:4,pars:[8,15,16],parsedrequest:8,part:[2,8,17],parti:9,pass:7,password:8,path:[2,4,6,16,17],patrick:15,peopl:[8,9],per:[2,8,9],perfom:8,perform:[7,8],perman:15,person:[2,9],philibeaux:15,pictur:7,piec:[14,17],pipelin:[0,5,7,8,9,14,15],pipeline_:15,pipeline_config:[4,16],pipeline_demo:[4,17],pipeline_run_info:8,pipelineruninfo:8,plai:17,plan:17,pleas:[2,4,16,17],polit:17,politician:9,port:[8,16,17],possibl:[8,15],postprocessing_func:7,potenti:8,power:17,pre:[2,4,8,16],predefin:6,prerequisit:15,present:[9,17],pretti:[7,9],prettifi:[15,17],previou:17,primari:8,print:7,probabl:[8,9],problem:[8,16],process:[0,6,7,8,15,17],process_articl:7,process_sentence_with_corenlp_serv:7,produc:[8,17],progress:17,proident:4,project:[3,4,5,8,14,16],proper:8,properti:[7,8],propos:7,prototyp:17,provid:[4,7,8,9,15,16],pui:15,purpos:4,pwd:[16,17],pycorenlp:7,python3:[4,16,17],python:[8,16],pywikibot:[0,17],q3039421:9,qualifi:8,queri:[8,9],query_a:8,query_b:8,query_contains_field:8,question:6,qui:4,rais:[2,6,8],ran:17,raw:[7,8],raw_articl:7,raw_pipeline_config:[4,16],read:[7,9,16,17],readabl:[9,15,17],readthedoc:17,real:[2,7],reason:8,recommend:[9,16],record:8,refer:[2,7,16],relat:8,relation_base_class:8,relation_base_classes_nam:8,relation_json:8,relation_typ:8,relationship:[8,9,16],relationship_manag:8,relationshipdefinit:8,relev:[5,7,8],reli:8,remain:6,remov:[4,8],replac:[4,8,16,17],report:17,repositori:17,reprehenderit:4,req:8,request:[8,9,16,17],requir:[2,3,4,7,9,15,16],resourc:[6,7,8],resource_path:6,respons:9,rest:8,result:[4,6,7,8,9,15,16,17],retriev:8,return_select:8,reveal:17,right:17,root:[9,17],row:8,rpr:15,rtype:8,run:[0,2,3,4,7,8,9,14],run_api:[0,16,17],run_id:8,run_pipelin:9,salair:15,same:[7,8,16],sampl:5,satisfi:8,save:8,schedul:17,scratch:8,script:16,search:[8,17],second:6,second_fil:7,seconds_to_hm:6,section:17,secur:2,sed:4,see:[4,8,16,17],seem:8,select:8,self:[7,8],sens:7,sentenc:[4,7,8,15],sentence_data:7,separ:8,sept:15,serial:[0,7,17],serializ:8,serialize_output:7,serializing_funct:7,server:[0,7,16,17],serverproperti:3,set:[6,7,8,17],setup:[16,17],sever:8,shallow:[15,16],shape:17,should:[2,4,6,7,8,17],show:17,simpl:[0,4,6,8,15,17],simplereadingtask:17,simpli:4,sinc:17,singl:[2,6,7,8],sinnt:4,sint:4,sit:4,site:[16,17],size:17,slow:16,small:7,sock:[16,17],solut:8,solv:16,some:[7,14,17],someth:17,somewher:[2,4,16],sort:8,sourc:[6,9,17],special:[2,9],specif:[0,2,7,8,9,17],specifi:[2,8,9],speed:16,sphere:17,stabl:17,standard:[0,16,17],standard_task:[0,16,17],stanford:[0,3,7,15,16,17],stanford_model:[16,17],stanfordcorenlp:7,start:[2,7,8,15,17],state:[4,7,15],step:[7,15,16,17],stick:16,still:17,store:[2,15,17],str:[2,6,7,8],string:15,stringproperti:8,structur:15,structurednod:8,structuredrel:8,stuff:7,sub:8,sub_resource_lookup:8,subclass:7,subj_ent:8,subsect:7,subset:9,success:17,successfulli:17,suggest:17,summari:17,sunnt:4,sunt:4,suppli:8,support:[2,4,8,16],supported_languag:[2,4,16],suppos:17,sure:[2,4,5,7,16,17],syntax:8,system:[16,17],tabl:[7,8],tag:16,tailor:8,take:[8,16,17],taken:8,target:[2,6,8,9],task:[0,2,4,5,7,8,14,17],task_config:[2,4,7,16],task_workflow:7,techniqu:17,templat:[4,16],tempor:4,termin:17,test:8,texoo:4,text:[7,15,17],textwrapp:7,thei:[2,15],them:[7,8,17],themselv:7,theoret:15,therebi:8,therefor:4,thi:[2,3,4,5,7,8,9,15,16,17],thing:[9,17],those:[2,3,4,16,17],three:4,throughout:[0,17],thrown:2,time:[5,16,17],timestamp:8,titl:[4,15],todai:17,todo:17,toolkit:6,touch:5,transform:7,transpar:17,treat:7,trough:7,tupl:[6,7,8],turn:[6,9],two:[2,8,17],type:[2,4,6,7,8,9,15],u00e2tr:9,u00e8c:9,u00e9:9,uid:[8,9],ullamco:4,underli:8,unipesso:9,uniqu:8,uniqueidproperti:8,unserializ:8,unsupportedlanguageexcept:2,updat:8,upon:17,url:[4,8,15],usag:0,use:[0,3,4,8,9,16,17],used:[0,4,6,7,8,17],user:[2,8],uses:[0,5,17],using:[0,2,4,6,7,9,16,17],usual:[7,8,15],util:[0,8,17],uxxcoo:4,valu:[2,6,8],vari:17,variabl:[2,7],veit:4,velit:4,veniam:4,vennixx:4,veri:[4,9],version:[9,17],via:7,viabl:8,vill:15,visit:17,visual:17,volunt:17,volupt:4,vooutxt:4,wai:[2,7,8,15],want:[5,7,8,16,17],warn:8,weight:8,welcom:17,well:[7,8,9,15,17],were:[8,17],what:[2,4,16,17],when:[2,3,8],where:8,wherebi:7,whether:[7,8],which:[4,7,8,9,16,17],wiki:15,wikidata:[0,8,16,17],wikidata_id:9,wikidata_last_modifi:9,wikipedia:[0,5,7,15,17],wikipedia_task:[0,16,17],window:[16,17],with_limit_and_skip:8,within:[6,8],without:[2,6,16],won:7,word:7,work:[5,7,8,16,17],worker:[2,4,16],workflow:7,workflow_kwarg:7,workflow_resourc:7,world:[7,17],wrap:[7,8],wrapper:[0,7,8,17],write:[2,7,8,14,17],written:[7,8,15,17],www:15,xbbooe:4,xbbooi:4,xbbooux:4,xdiiscinng:4,xinnix:4,xiqui:4,xiqux:4,xixtu:4,xml:[4,15,16],xnnix:4,xooit:4,xute:4,xxet:4,xxgnnx:4,yada:[2,4,16],yet:[2,9,17],yield:7,yml:[3,17],you:[2,3,4,5,7,8,9,15,16,17],your:[0,7,8,9,14,15,17],zip:7},titles:["Main project contents","bwg.additional_tasks","bwg.config_management","bwg.corenlp_server_tasks","bwg.demo_pipeline","bwg.french_wikipedia","bwg.helpers","bwg.mixins","bwg.neo4j_extensions","bwg.run_api","bwg.standard_tasks","bwg.utilities","bwg.wikidata","bwg.wikipedia_tasks","General","Data","The Pipeline","BigWorldGraph"],titleterms:{The:16,Using:3,additional_task:1,adjust:[4,16],backstori:5,bigworldgraph:17,build:17,bwg:[1,2,3,4,5,6,7,8,9,10,11,12,13],config_manag:2,configur:[2,4,16],content:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,17],contribut:17,corenlp:3,corenlp_server_task:3,creat:2,data:[15,17],demo:17,demo_pipelin:4,descript:17,document:17,featur:9,french_wikipedia:5,gener:[14,17],get:17,helper:6,indic:17,inform:17,input:15,instal:17,main:[0,17],mixin:7,modul:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,17],motiv:8,neo4j_extens:8,output:15,own:[2,16],pipelin:[2,4,16,17],project:[0,17],quickstart:17,real:17,run:[16,17],run_api:9,seriou:17,server:3,standard_task:10,tabl:17,task:[3,15,16],test:17,toi:17,usag:[9,17],util:11,wikidata:12,wikipedia_task:13,write:16,your:[2,4,16]}})