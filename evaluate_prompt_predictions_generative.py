import re
import os
import sys
import codecs

from util import *

gold_dir_path = sys.argv[1]
predictions_dir_path = sys.argv[2]

total_num1 = 0
total_num3 = 0
total_instances = 0

def count_words_before_index(input_str, input_idx):
	num_spaces = 0
	for j in range(input_idx):
		if(input_str[j] == ' '):
			num_spaces += 1
	return num_spaces

lenient_direction_map = {}
lenient_direction_map_path = os.path.join('resources', 'misc', 'lenient_direction_map.txt')
lenient_direction_map_file = open(lenient_direction_map_path, 'r')
for line in lenient_direction_map_file:
	line = line.strip()
	if(len(line) == 0):
		continue

	line_parts = line.split('\t')
	lenient_direction_map[line_parts[0]] = line_parts[1]
lenient_direction_map_file.close()

gold_file_list = os.listdir(gold_dir_path)
for file_path in gold_file_list:
	pivot_entity = file_path[:file_path.rfind('.')]
	gold_file_path = os.path.join(gold_dir_path, file_path)
	curr_gold_file = codecs.open(gold_file_path, 'r', encoding = 'utf-8', errors = 'ignore')
	list_golds = []
	for line in curr_gold_file:
		line = line.strip()
		list_golds.append(line)
	curr_gold_file.close()

	num_top1 = 0
	num_top3 = 0
	num_total_instances = 0
	predictions_file_path = os.path.join(predictions_dir_path, file_path)
	curr_predictions_file = codecs.open(predictions_file_path, 'r', encoding = 'utf-8', errors = 'ignore')

	curr_obj_entity = ''
	for line in curr_predictions_file:
		line = line.strip()
		if(len(line) == 0):
			continue

		line_parts = line.split('\t')
		curr_obj_entity = line_parts[0]

		#Processing generated text
		gen_text = line_parts[1].strip()
		gen_text = re.sub(r'[ ]{2,}', ' ', gen_text)
		"""gen_text_parts = gen_text.split()
		if(len(gen_text_parts) > 2):
			gen_index_near3 = len(gen_text_parts[0]) + len(gen_text_parts[1]) + 3
		else:
			#if there are less than 3 predicted words, then any find after index 0 can be considered as in-near-3
			gen_index_near3 = 1"""

		#Old logic where only 1 direction was being used
		best_match = ''
		best_match_index = 1000
		processed_direction = 'undefined'
		for dir_type in lenient_direction_map:
			if(gen_text.find(dir_type) >= 0):
				if(len(best_match) <= len(dir_type) and best_match_index >= gen_text.find(dir_type)):
					best_match = dir_type
					best_match_index = gen_text.find(dir_type)

		if(best_match_index != 1000):
			processed_direction = lenient_direction_map[best_match]
			pred_index = count_words_before_index(gen_text, best_match_index)
		else:
			pred_index = 20

		eval_segment = pivot_entity + '\t' + processed_direction + '\t' + curr_obj_entity
		if(eval_segment in list_golds and pred_index < 3):
			num_top3 += 1

		if(eval_segment in list_golds and pred_index == 0):
			num_top1 += 1

		#New logic where all possible directions in near1 and near3 are being used for evaluation
		"""processed_direction_to_index = {}
		for dir_type in lenient_direction_map:
			if(gen_text.find(dir_type) >= 0):
				processed_direction = lenient_direction_map[dir_type]
				pred_index = count_words_before_index(gen_text, gen_text.find(dir_type))
				processed_direction_to_index[processed_direction] = pred_index

		for processed_direction in processed_direction_to_index:
			pred_index = processed_direction_to_index[processed_direction]
			eval_segment = pivot_entity + '\t' + processed_direction + '\t' + curr_obj_entity
			if(eval_segment in list_golds and pred_index < 3):
				num_top3 += 1

			if(eval_segment in list_golds and pred_index == 0):
				num_top1 += 1"""

		num_total_instances += 1
	curr_predictions_file.close()

	total_num1 += num_top1
	total_num3 += num_top3
	total_instances += num_total_instances

print (str(total_num1) + '\t' + str(total_num3) + '\t' + str(total_instances))
