import os
import re
import sys
import codecs

from util import *

working_dir_path = sys.argv[1]
style_type = sys.argv[2] #allowed options are simple, patterns

input_dir_path = os.path.join(working_dir_path, 'entity_direction_sents')
nli_output_dir_path = os.path.join(working_dir_path, 'entity_premise_hypothesis_pairs_' + style_type)
prompt_output_dir_path = os.path.join(working_dir_path, 'entity_prompts')
prompt_demo_output_dir_path = os.path.join(working_dir_path, 'entity_prompts_with_demos')
os.makedirs(nli_output_dir_path, exist_ok = True)
os.makedirs(prompt_output_dir_path, exist_ok = True)
os.makedirs(prompt_demo_output_dir_path, exist_ok = True)

entity_text_paths = os.listdir(input_dir_path)
for entity_text_path in entity_text_paths:
	curr_entity_file_path = os.path.join(input_dir_path, entity_text_path)
	curr_entity_file = codecs.open(curr_entity_file_path, 'r', encoding = 'utf-8', errors = 'ignore')
	curr_entity_name = entity_text_path[0:entity_text_path.rfind('.')].replace('_', ' ')
	
	curr_entity_ph_file_path = os.path.join(nli_output_dir_path, entity_text_path)
	curr_entity_ph_file = codecs.open(curr_entity_ph_file_path, 'w', encoding = 'utf-8', errors = 'ignore')
	curr_entity_pr_file_path = os.path.join(prompt_output_dir_path, entity_text_path)
	curr_entity_pr_file = codecs.open(curr_entity_pr_file_path, 'w', encoding = 'utf-8', errors = 'ignore')
	curr_entity_pd_file_path = os.path.join(prompt_demo_output_dir_path, entity_text_path)
	curr_entity_pd_file = codecs.open(curr_entity_pd_file_path, 'w', encoding = 'utf-8', errors = 'ignore')
	
	for line in curr_entity_file:
		line = line.strip()
		if(len(line) == 0):
			continue

		premise_hypothesis_pairs = []
		line_parts = line.split('\t')
		curr_sent = line_parts[0]

		premise = perform_input_text_replacements(curr_sent, curr_entity_name)

		list_entities = line_parts[1].split('; ')
		style = None
		if(style_type.lower() == 'patterns'):
			style = get_direction_specification_style(premise)

		if(style is None):
			#print ('Style Unknown\t' + curr_entity_name + '\t' + '\t' + curr_sent + '\t' + premise + '\tFailsafe to default style\n')
			for obj_entity in list_entities:
				if(obj_entity.strip() == curr_entity_name):
					continue

				hypothesis = curr_entity_name + ' shares borders with ' + obj_entity + ' to the {}.'
				prompt = curr_entity_name + ' shares borders with ' + obj_entity + ' to the [MASK].'
				premise_hypothesis_pairs.append((obj_entity, premise, hypothesis, prompt, '0'))
		else:
			for obj_entity in list_entities:
				if(obj_entity.strip() == curr_entity_name):
					continue
				
				style_parts = style.split('\t')
				hypothesis_parts = []
				prompt_parts = []
				for k in range(len(style_parts)):
					style_part = style_parts[k]
					if(style_part.startswith('0') or style_part.startswith('1') or style_part.startswith('None')):
						continue

					if(style_part.startswith('SUB')):
						hypothesis_parts.append(curr_entity_name)
						prompt_parts.append(curr_entity_name)
					elif(style_part.startswith('DIR')):
						hypothesis_parts.append('{}')
						prompt_parts.append('[MASK]')
					elif(style_part.startswith('OBJ')):
						hypothesis_parts.append(obj_entity)
						prompt_parts.append(obj_entity)
					else:
						hypothesis_parts.append(style_part)
						prompt_parts.append(style_part)

				hypothesis = ' '.join(hypothesis_parts) + '.'
				prompt = ' '.join(prompt_parts) + '.'
				premise_hypothesis_pairs.append((obj_entity, premise, hypothesis, prompt, style_parts[0]))

		for ph in premise_hypothesis_pairs:
			curr_entity_ph_file.write(ph[0] + '\t' + ph[1] + '\t' + ph[2] + '\t' + ph[4] + '\n')
			curr_entity_pr_file.write(ph[0] + '\t' + ph[1] + '\t' + ph[3] + '\t' + ph[4] + '\n')
			curr_entity_pd_file.write(ph[0] + '\t' + ph[1] + '\t' + ph[1] + ' [SEP] ' + ph[3] + '\t' + ph[4] + '\n')

	curr_entity_ph_file.close()
	curr_entity_pr_file.close()
	curr_entity_pd_file.close()
	curr_entity_file.close()