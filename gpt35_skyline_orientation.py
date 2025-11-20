#Installation required #pip install openai==0.28
import re
import os
import sys
import openai
import codecs
import numpy as np
import unicodedata

mask_files_folder_path = sys.argv[1]
output_folder_path = sys.argv[2]

model_name = 'gpt35'
mask_token = '[MASK]'
openai.api_key = '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'

total_num_questions = 0
mask_file_list = os.listdir(mask_files_folder_path)

input_tokens = []
output_tokens = []
for j in range(len(mask_file_list)):
	mask_file_name = mask_file_list[j]

	print ('Working on (' + str(j + 1) + ') ' + mask_file_name)
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

		response = openai.Completion.create(model = 'gpt-3.5-turbo-instruct', prompt = mq_input_for_gen, temperature = 0.1, max_tokens = 10)
		orig_gen_text = response['choices'][0]['text']

		input_tokens.append(response['usage']['prompt_tokens'])
		output_tokens.append(response['usage']['completion_tokens'])

		#Addition of cleaning of orig_gen_text
		gen_text = re.sub('\n', ' ', orig_gen_text)
		"""if(gen_text.find(' to the ') > 0):
			temp_location_index = gen_text.find(' to the ') + len(' to the ')
			gen_text = gen_text[temp_location_index:]
		gen_text = re.sub('^[\.\,\!\?\_\' ]+|[\.\,\!\?\_\' ]+$', '', gen_text)"""

		output_file.write(mcq[0] + '\t' + gen_text + '\n')

output_file.close()
print ('Total number of prompts: ' + str(total_num_questions))
input_tokens_sum = sum(input_tokens)
print (input_tokens_sum, '\t', input_tokens_sum * 0.0000015, '\t', input_tokens_sum * 0.0000015 * 83.38)
output_tokens_sum = sum(output_tokens)
print (output_tokens_sum, '\t', output_tokens_sum * 0.000002, '\t', output_tokens_sum * 0.000002 * 83.38)