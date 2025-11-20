import os
import re
import sys
import codecs

list_directions = ['east', 'north', 'west', 'south', 'northeast', 'north-east', 'northwest', 'north-west', 'southwest', 'south-west', 'southeast', 'south-east']
list_directions_simple = ['east', 'north', 'west', 'south', 'northeast', 'northwest', 'southwest', 'southeast']
dir_regex = re.compile(r'\b(east|north|west|south|northeast|north\-east|northwest|north\-west|southwest|south\-west|southeast|south\-east)\b')

def get_list_of_entities_present(input_text, entity_list):
	list_entities_found = []
	for entity in entity_list:
		entity_re = r'\b' + re.escape(entity) + r'\b'
		re_match = re.search(entity_re, input_text)
		if(re_match is not None):
			list_entities_found.append(entity)
	return list_entities_found

def get_direction_specification_style_old(input_text):
	possible_direction_specification_styles = [(r'shares land borders with', 'post', None), (r'bordering', 'post', 'is'), (r'borders', 'post', None), (r'lying', 'pre', 'is'), (r'lies', 'pre', None), (r'lie', 'pre', None), ('bordered by', 'post', 'is'), (r'border', 'post', None), ('bounded by', 'post', 'is'), (r'bounds', 'post', None), ('located', 'pre', None)]
	style_found = None
	for style in possible_direction_specification_styles:
		style_re = r'\b' + re.escape(style[0]) + r'\b'
		re_match = re.search(style_re, input_text)
		if(re_match is not None):
			style_found = style
			break
	return style_found

def get_direction_specification_style(input_text):
	direction_specification_style_file_path = os.path.join('resources', 'misc', 'hypothesis_template_types.txt')
	direction_specification_style_file = codecs.open(direction_specification_style_file_path, 'r', encoding = 'utf-8', errors = 'ignore')
	possible_direction_specification_styles = []
	header = True
	for line in direction_specification_style_file:
		if(header):
			header = False
			continue

		line = line.strip()
		if(len(line) == 0):
			continue
		
		possible_direction_specification_styles.append(line)
	direction_specification_style_file.close()
	
	style_found = None
	for style in possible_direction_specification_styles:
		style_parts = style.split('\t')
		style_re_parts = []
		for style_part in style_parts:
			if(style_part.startswith('0') or style_part.startswith('1') or style_part.startswith('SUB') or style_part.startswith('OBJ') or style_part.startswith('DIR') or style_part.startswith('None')):
				continue
			else:
				style_re_parts.append(style_part)

		style_re = r'\b' + r'\b.*?\b'.join(style_re_parts) + r'\b'
		re_match = re.search(style_re, input_text)
		if(re_match is not None):
			style_found = style
			break
	return style_found

def perform_input_text_replacements(curr_sent, curr_entity_name):
	premise = curr_sent

	#pronoun / common noun mentions of SUB entity name replacement
	if(curr_sent.find(' it ') > 0):
		premise = curr_sent.replace(' it ', ' ' + curr_entity_name + ' ', 1)
	elif(curr_sent.find('It ') >= 0):
		premise = curr_sent.replace('It ', curr_entity_name + ' ', 1)
	elif(curr_sent.find('Its ') >= 0):
		premise = curr_sent.replace('Its ', curr_entity_name + '\'s ', 1)
	elif(curr_sent.find(' the country ') > 0):
		premise = curr_sent.replace(' the country ', ' ' + curr_entity_name + ' ', 1)
	elif(curr_sent.find('The country ') >= 0):
		premise = curr_sent.replace('The country ', curr_entity_name + ' ', 1)

	#specific common noun mentions of SUB entity replacement
	#specifically for Venezuela
	if(curr_sent.find('The continental territory ') == 0 and curr_entity_name == 'Venezuela'):
		premise = curr_sent.replace('The continental territory ', curr_entity_name + ' ', 1)
	#specifically for Columbia
	elif(curr_sent.find('The Colombian mainland ') == 0 and curr_entity_name == 'Columbia'):
		premise = curr_sent.replace('The Colombian mainland ', curr_entity_name + ' ', 1)
	#specifically for Marshall Islands
	elif(curr_sent.find('The islands ') == 0 and curr_entity_name == 'Marshall Islands'):
		premise = curr_sent.replace('The islands ', curr_entity_name + ' ', 1)
	#specifically for Vanuatu
	elif(curr_sent.find('The archipelago') == 0 and curr_entity_name == 'Vanuatu'):
		premise = curr_sent.replace('The archipelago', curr_entity_name, 1)
	#specifically for The Bahamas
	elif(curr_sent.find('The archipelagic state ') == 0 and curr_entity_name == 'The Bahamas'):
		premise = curr_sent.replace('The archipelagic state ', curr_entity_name + ' ', 1)
	#specifically for Mozambique
	elif(curr_sent.find('The sovereign state ') == 0 and curr_entity_name == 'Mozambique'):
		premise = curr_sent.replace('The sovereign state ', curr_entity_name + ' ', 1)
	#specifically for Nepal
	elif(curr_sent.find('It ') == 0 and curr_entity_name == 'Nepal'):
		premise = curr_sent.replace('It ', curr_entity_name + ' ', 1)
	#specifically for Federated States of Micronesia
	elif(curr_sent.find('They ') >= 0 and curr_entity_name == 'Federated States of Micronesia'):
		premise = curr_sent.replace('They ', curr_entity_name + ' ', 1)

	#directions with hyphen normalized to ones without hyphens
	if(premise.find('south-west') >= 0):
		premise = premise.replace('south-west', 'southwest')

	if(premise.find('south-east') >= 0):
		premise = premise.replace('south-east', 'southeast')

	if(premise.find('north-west') >= 0):
		premise = premise.replace('north-west', 'northwest')

	if(premise.find('north-east') >= 0):
		premise = premise.replace('north-east', 'northeast')

	return premise

def get_reverse_direction(curr_direction):
	if(curr_direction == 'north'):
		return 'south'
	if(curr_direction == 'south'):
		return 'north'
	if(curr_direction == 'west'):
		return 'east'
	if(curr_direction == 'east'):
		return 'west'
	if(curr_direction == 'northwest'):
		return 'southeast'
	if(curr_direction == 'southeast'):
		return 'northwest'
	if(curr_direction == 'northeast'):
		return 'southwest'
	if(curr_direction == 'southwest'):
		return 'northeast'
	return None