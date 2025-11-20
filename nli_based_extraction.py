import os
import sys
from transformers import pipeline

from util import *

working_dir_path = sys.argv[1]
nli_model_name = sys.argv[2] #available models are bart-large-mnli and roberta-large-mnli
hypo_type = sys.argv[3] #allowed options are simple, patterns

nli_input_dir_path = os.path.join(working_dir_path, 'entity_premise_hypothesis_pairs_' + hypo_type)
nli_output_dir_path = os.path.join(working_dir_path, 'nli_predictions_' + hypo_type)
os.makedirs(nli_output_dir_path, exist_ok = True)

#loading the NLI model
print ('Loading the NLI model')
nli_model_path = os.path.join('resources', 'transformers', nli_model_name)
nli_model_pipeline = pipeline("zero-shot-classification", model = nli_model_path)
print ('Loaded the NLI model')

entity_ph_file_paths = os.listdir(nli_input_dir_path)
for entity_ph_file_path in entity_ph_file_paths:
	curr_entity_file_path = os.path.join(nli_input_dir_path, entity_ph_file_path)
	curr_entity_file = codecs.open(curr_entity_file_path, 'r', encoding = 'utf-8', errors = 'ignore')
	curr_entity_name = entity_ph_file_path[0:entity_ph_file_path.rfind('.')].replace('_', ' ')
	print('Processing ' + curr_entity_name)

	curr_ph_pred_file_path = os.path.join(nli_output_dir_path, entity_ph_file_path)
	curr_ph_pred_file = codecs.open(curr_ph_pred_file_path, 'w', encoding = 'utf-8', errors = 'ignore')

	for line in curr_entity_file:
		line = line.strip()
		if(len(line) == 0):
			continue

		line_parts = line.split('\t')
		curr_obj_entity = line_parts[0]
		premise = line_parts[1]
		curr_hypothesis_template = line_parts[2]
		gold_reverse = line_parts[-1]

		if(curr_hypothesis_template.find('{}') < 0):
			continue

		output = nli_model_pipeline(premise, list_directions_simple, hypothesis_template = curr_hypothesis_template, multi_label = True)

		premise_hypothesis_to_score = {}
		for k in range(len(output['labels'])):
			curr_label = output['labels'][k]
			curr_label_score = output['scores'][k]
			curr_hyp = curr_hypothesis_template.replace('{}', curr_label)
			#premise_hypothesis_to_score[curr_hyp] = curr_label_score
			premise_hypothesis_to_score[curr_label] = curr_label_score

		sorted_premise_hypothesis = sorted(premise_hypothesis_to_score, key = premise_hypothesis_to_score.get, reverse = True)
		curr_ph_pred_file.write(premise + '\n')
		#for ph in sorted_premise_hypothesis:
		#	curr_ph_pred_file.write('\t' + ph + '\t' + str(premise_hypothesis_to_score[ph])  + '\t' + '\n')
		for label in sorted_premise_hypothesis:
			if(premise_hypothesis_to_score[label] >= 0.5):
				curr_ph_pred_file.write('\t' + curr_entity_name + '\t' + label + '\t' + curr_obj_entity + '\t' + str(premise_hypothesis_to_score[label])  + '\t' + gold_reverse + '\n')
		curr_ph_pred_file.write('\n')

	curr_entity_file.close()
	curr_ph_pred_file.close()
