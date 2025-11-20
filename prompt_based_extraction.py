import os
import sys
import torch
import codecs
import numpy as np
import unicodedata
from transformers import pipeline
from transformers import AutoTokenizer,  AutoModelForMaskedLM, BartTokenizer, BartForConditionalGeneration

from util import *

working_dir_path = sys.argv[1]
model_name = sys.argv[2]
prompts_or_prompts_with_demos = sys.argv[3]

prompt_input_dir_path = os.path.join(working_dir_path, 'entity_' + prompts_or_prompts_with_demos)
prompt_output_dir_path = os.path.join(working_dir_path, prompts_or_prompts_with_demos + '_predictions')
os.makedirs(prompt_output_dir_path, exist_ok = True)

#loading the transformers model
print ('Loading the transformers model')
model_path = os.path.join('resources', 'transformers', model_name)
if(model_name.startswith('bart')):
	tokenizer = BartTokenizer.from_pretrained(model_path)
	model = BartForConditionalGeneration.from_pretrained(model_path)
else:
	tokenizer = AutoTokenizer.from_pretrained(model_path)
	model = AutoModelForMaskedLM.from_pretrained(model_path)
print ('Loaded the transformers model')

mask_token = '[MASK]'
if(model_name.startswith('roberta') or model_name.startswith('bart')):
	mask_token = '<mask>'
elif(model_name.startswith('xlm')):
	mask_token = '<special1>'

entity_pr_file_paths = os.listdir(prompt_input_dir_path)
for entity_pr_file_path in entity_pr_file_paths:
	curr_entity_file_path = os.path.join(prompt_input_dir_path, entity_pr_file_path)
	curr_entity_file = codecs.open(curr_entity_file_path, 'r', encoding = 'utf-8', errors = 'ignore')
	curr_entity_name = entity_pr_file_path[0:entity_pr_file_path.rfind('.')].replace('_', ' ')
	print('Processing ' + curr_entity_name)

	curr_pr_pred_file_path = os.path.join(prompt_output_dir_path, entity_pr_file_path)
	curr_pr_pred_file = codecs.open(curr_pr_pred_file_path, 'w', encoding = 'utf-8', errors = 'ignore')

	for line in curr_entity_file:
		line = line.strip()
		if(len(line) == 0):
			continue

		line_parts = line.split('\t')
		curr_obj_entity = line_parts[0]
		original_sentence = line_parts[1]
		prompt = line_parts[2].replace('[MASK]', mask_token)
		prompt = unicodedata.normalize('NFKD', prompt).encode('ascii', 'ignore').decode('utf-8')
		inputs = tokenizer(prompt, return_tensors = "pt")
		with torch.no_grad():
			logits = model(**inputs).logits

		# retrieve index of [MASK]
		mask_token_index = (inputs.input_ids == tokenizer.mask_token_id)[0].nonzero(as_tuple = True)[0]
		probs = logits[0, mask_token_index].softmax(dim = -1)
		try:
			values, predictions = probs.topk(3)
			top_3_answers = tokenizer.decode(predictions[0]).split()

			curr_pr_pred_file.write(original_sentence + '\n')
			for answer in top_3_answers:
				#prompt_answered = line.replace(mask_token, answer)
				#curr_pr_pred_file.write('\t' + prompt_answered + '\n')
				curr_pr_pred_file.write('\t' + curr_entity_name + '\t' + answer + '\t' + curr_obj_entity + '\t' + line_parts[3] + '\n')
			curr_pr_pred_file.write('\n')
		except:
			print('Skipping entity: ' + curr_entity_name)

	curr_entity_file.close()
	curr_pr_pred_file.close()