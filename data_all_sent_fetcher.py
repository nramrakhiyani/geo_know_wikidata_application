#This script performs the following functions to collects specified number of sentences from wikipedia pages of specific geographical entities:
#1. fires the necessary SPARQL query on wikidata
#2. Processes the wikidata query output to collect the entity names
#3. Calls the MediaWiki API to obtain sentences from the Wikipedia pages of the entities

import os
import re
import sys
import codecs
import requests
import pandas as pd

from nltk.tokenize import sent_tokenize
from SPARQLWrapper import SPARQLWrapper, JSON

from util import *

output_dir_path = sys.argv[1]

#configs
run_step1 = False
run_step2 = False
run_step3 = False

#Step 1: Firing the necessary SPARQL query on wikidata
step1_output_path = os.path.join(output_dir_path, 'wikidata_sparql_output.tsv')
if(run_step1):
	print ("Step 1: Firing the necessary SPARQL query on wikidata")
	sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
	
	#wikidata query for obtaining all entities of type 'country' (Q6456) with 'shares_land_borders' (P47) property, with the constrain that the corresponding value entity of the property also is of type 'country'.
	wikidata_query = '''
	SELECT ?item ?itemLabel ?propId ?propVal ?propValLabel
	WHERE
	{
	?item wdt:P31 wd:Q6256.
	SERVICE wikibase:label { bd:serviceParam wikibase:language "en".}
	?item ?propId ?propVal.
	VALUES ?propId {wdt:P47}.
	?propVal wdt:P31 wd:Q6256.
	}
	'''
	
	sparql.setQuery(wikidata_query)
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()
	
	results_df = pd.json_normalize(results['results']['bindings'])
	results_df[['itemLabel.value', 'propId.value', 'propValLabel.value']].to_csv(step1_output_path, sep = "\t", index = False)
else:
	print ('Skipping Step 1 as per config')

#Step 2: Process the wikidata query output to collect the entity names
step2_output_path = os.path.join(output_dir_path, 'entity_list.txt')
if(run_step2):
	print ("Step 2: Process the wikidata query output to collect the entity names")
	header = True
	unique_entity_list = {}
	step1_output_file = codecs.open(step1_output_path, 'r', encoding = 'utf-8', errors = 'ignore')
	for line in step1_output_file:
		if(header):
			header = False
			continue
	
		line = line.strip()
		if(len(line) == 0):
			continue
	
		line_parts = line.split('\t')
		unique_entity_list[line_parts[0]] = ''
		unique_entity_list[line_parts[2]] = ''
	step1_output_file.close()
	
	step2_output_file = codecs.open(step2_output_path, 'w', encoding = 'utf-8', errors = 'ignore')
	for entity in unique_entity_list:
		step2_output_file.write(entity + '\n')
	step2_output_file.close()
else:
	print ('Skipping Step 2 as per config')

#Step 3: Call the MediaWiki API to obtain sentences from the Wikipedia pages of the entities
if(run_step3):
	print ("Step 3: Call the MediaWiki API to obtain sentences from the Wikipedia pages of the entities")
	base_url = "https://en.wikipedia.org/w/api.php?action=query&exintro=&explaintext=&exsentences=10&formatversion=2&prop=extracts&redirects=&format=json&titles="
	
	unique_entity_list = []
	step2_output_file = codecs.open(step2_output_path, 'r', encoding = 'utf-8', errors = 'ignore')
	for line in step2_output_file:
		line = line.strip()
		if(len(line) > 0):
			unique_entity_list.append(line)
	step2_output_file.close()
	
	text_data_path = os.path.join(output_dir_path, 'entity_all_sents')
	os.makedirs(text_data_path, exist_ok = True)
	entity_to_all_sents = {}
	for entity in unique_entity_list:
		print("Extracting wiki sentences from: " + entity)
		entity_url = entity.replace(' ', '+')
		curr_url = base_url + entity_url
		r = requests.get(curr_url)
		page = r.json()
		try:
			text = r.json()['query']['pages'][0]['extract']
			entity_filename = entity.replace(' ', '_')
			curr_entity_file_path = os.path.join(text_data_path, entity_filename + '.txt')
			curr_entity_file = codecs.open(curr_entity_file_path, 'w', encoding = 'utf-8', errors = 'ignore')
			curr_entity_file.write(text)
			entity_to_all_sents[entity] = text
			curr_entity_file.close()
		except:
			print ('Skipping for entity: ' + entity + ' due to text unavailable')
			continue
else:
	print ('Skipping Step 3 as per config')

#Step 4: Filtering out sentences not containing any direction/orientation information
print("Step 4: Filtering out sentences not containing any direction/orientation information or not having more than one entity names")
dir_regex = re.compile(r'\b(east|north|west|south|northeast|north\-east|northwest|north\-west|southwest|south\-west|southeast|south\-east)\b')

entity_to_all_sents = {}
text_data_path = os.path.join(output_dir_path, 'entity_all_sents')
entity_text_paths = os.listdir(text_data_path)
unique_entity_list = []
for entity_text_path in entity_text_paths:
	curr_entity_file_path = os.path.join(text_data_path, entity_text_path)
	curr_entity_file = codecs.open(curr_entity_file_path, 'r', encoding = 'utf-8', errors = 'ignore')
	curr_entity_text = ''
	for line in curr_entity_file:
		curr_entity_text = curr_entity_text + ' ' + line.strip()
	curr_entity_text = curr_entity_text.strip()
	curr_entity_name = entity_text_path[0:entity_text_path.rfind('.')].replace('_', ' ')
	entity_to_all_sents[curr_entity_name] = curr_entity_text

entity_list = list(entity_to_all_sents.keys())
print (entity_list)

#entity_to_dir_sents = {}
processed_data_path = os.path.join(output_dir_path, 'entity_direction_sents')
os.makedirs(processed_data_path, exist_ok = True)
for entity in entity_to_all_sents:
	print ('Processing entity: ' + entity)
	curr_entity_text = entity_to_all_sents[entity]
	curr_sent_list = sent_tokenize(curr_entity_text)
	curr_dir_sents = []
	for sent in curr_sent_list:
		re_match = re.search(dir_regex, sent)
		list_entities_found = get_list_of_entities_present(sent, entity_list)
		if(re_match is not None and len(list_entities_found) > 1):
			curr_dir_sents.append((sent, list_entities_found))
	#entity_to_dir_sents[entity] = curr_dir_sents

	entity_filename = entity.replace(' ', '_')
	curr_entity_file_path = os.path.join(processed_data_path, entity_filename + '.txt')
	curr_entity_file = codecs.open(curr_entity_file_path, 'w', encoding = 'utf-8', errors = 'ignore')
	for sent_detail in curr_dir_sents:
		curr_entity_file.write(sent_detail[0] + '\t' + '; '.join(sent_detail[1]) + '\n')
	curr_entity_file.close()