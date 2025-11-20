import re
import os
import sys
import torch
import codecs
import numpy as np
import unicodedata
from transformers import pipeline, AutoTokenizer

model_name = sys.argv[1]
mask_files_folder_path = sys.argv[2]
output_folder_path = sys.argv[3]
external_resources_path = sys.argv[4]

#structured_output_file_path = sys.argv[5]
#structured_output_file = codecs.open(structured_output_file_path, 'w', encoding = 'utf-8', errors = 'ignore')

model_path = os.path.join(external_resources_path, 'resources', 'transformers', model_name)

#slight change in the mask token for roberta
mask_token = '[MASK]'
if(model_name.startswith('roberta') or model_name.startswith('bart') or model_name.startswith('xlnet')):
	mask_token = '<mask>'
elif(model_name.startswith('xlm')):
	mask_token = '<special1>'

tokenizer = AutoTokenizer.from_pretrained(model_path)
generator = pipeline('text-generation', model = model_path, tokenizer = tokenizer, torch_dtype = torch.bfloat16, trust_remote_code = True, device_map = 'auto', pad_token_id = tokenizer.eos_token_id)

total_num_questions = 0
mask_file_list = os.listdir(mask_files_folder_path)
for j in range(len(mask_file_list)):
	mask_file_name = mask_file_list[j]

	print ('Working on (' + str(j) + ') ' + mask_file_name)
	mask_file_path = os.path.join(mask_files_folder_path, mask_file_name)
	mask_file = codecs.open(mask_file_path, 'r', encoding = 'utf-8', errors = 'ignore')

	output_file_path = os.path.join(output_folder_path, model_name, mask_file_name)
	output_file = codecs.open(output_file_path, 'w', encoding = 'utf-8', errors = 'ignore')

	mask_questions = []
	for line in mask_file:
		line = line.strip()
		if(len(line.strip()) == 0):
			continue

		line_parts = line.split('\t')
		if(line_parts[2].endswith(mask_token + '.')):
			mask_questions.append((line_parts[0], line_parts[2]))
	mask_file.close()

	#print ('Number of mask questions: ' + str(len(mask_questions)))
	total_num_questions += len(mask_questions)

	for mcq in mask_questions:
		mq = mcq[1]
		mq = mq.replace('[MASK]', mask_token)
		mq = unicodedata.normalize('NFKD', mq).encode('ascii', 'ignore').decode('utf-8')
		mq_input_for_gen = mq[0:mq.find(mask_token) - 1]

		#Adding instruction (Prompt Type 2)
		mq_input_for_gen = 'For the following sentence about geography, generate the most probable text to complete it. ' + mq_input_for_gen

		output = generator(mq_input_for_gen, do_sample = False, max_new_tokens = 10, return_full_text = False, temperature = 0.1)
		orig_gen_text = output[0]['generated_text'].strip()

		#Addition of cleaning of orig_gen_text
		gen_text = re.sub('\n', ' ', orig_gen_text)
		"""if(gen_text.find(' to the ') > 0):
			temp_location_index = gen_text.find(' to the ') + len(' to the ')
			gen_text = gen_text[temp_location_index:]
		gen_text = re.sub('^[\.\,\!\?\_\' ]+|[\.\,\!\?\_\' ]+$', '', gen_text)"""

		output_file.write(mcq[0] + '\t' + gen_text + '\n')

output_file.close()
print ('Total number of prompts: ' + str(total_num_questions))