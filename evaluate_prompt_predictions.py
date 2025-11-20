import os
import sys
import codecs

from util import *

gold_dir_path = sys.argv[1]
predictions_dir_path = sys.argv[2]
with_demos = sys.argv[3]

total_num1 = 0
total_num3 = 0
total_instances = 0

def endswith_items_in_list(input_str, list_items):
	for item in list_items:
		if(input_str.endswith(item)):
			return True
	return False

gold_file_list = os.listdir(gold_dir_path)
for file_path in gold_file_list:
	gold_file_path = os.path.join(gold_dir_path, file_path)
	curr_gold_file = codecs.open(gold_file_path, 'r', encoding = 'utf-8', errors = 'ignore')
	list_golds = []
	"""for line in curr_gold_file:
		line = line.strip()
		if(len(line) > 0 and line.find(';') < 0):
			list_golds.append([line])
		elif(len(line) > 0 and line.find(';') >= 0):
			list_golds.append(line.split('; '))
	curr_gold_file.close()"""
	for line in curr_gold_file:
		line = line.strip()
		list_golds.append(line)
	curr_gold_file.close()

	num_top1 = 0
	num_top3 = 0
	num_total_instances = 0
	predictions_file_path = os.path.join(predictions_dir_path, file_path)
	curr_predictions_file = codecs.open(predictions_file_path, 'r', encoding = 'utf-8', errors = 'ignore')
	
	#sent_index = -1
	pred_index = -1
	top3_seen = False
	curr_obj_entity = ''
	for line in curr_predictions_file:
		if(not line.startswith('\t') and len(line) > 1):
			#sent_index += 1
			num_total_instances += 1
			pred_index = 0
			top3_seen = False
		else:
			line = line.strip()
			if(len(line) == 0):
				continue

			line_parts = line.split('\t')
			curr_obj_entity = line_parts[1]
			#eval_segment = line_parts[0] + '\t' + line_parts[1] + '\t' + line_parts[2]
			gold_reverse = line_parts[-1]
			if(gold_reverse == '1'):
				if(get_reverse_direction(line_parts[1]) is not None):
					eval_segment = line_parts[0] + '\t' + get_reverse_direction(line_parts[1]) + '\t' + line_parts[2]
				else:
					eval_segment = line_parts[0] + '\tundefined\t' + line_parts[2]
			else:
				eval_segment = line_parts[0] + '\t' + line_parts[1] + '\t' + line_parts[2]

			"""if(with_demos.lower() == 'true'):
				if(endswith_items_in_list(eval_segment, list_golds[sent_index]) and pred_index < 3 and top3_seen is False):
					num_top3 += 1
					top3_seen = True

				if(endswith_items_in_list(line_parts[0], list_golds[sent_index]) and pred_index == 0):
					num_top1 += 1
			else:"""
			if(eval_segment in list_golds and pred_index < 3 and top3_seen is False):
				num_top3 += 1
				top3_seen = True

			if(eval_segment in list_golds and pred_index == 0):
				num_top1 += 1
			pred_index += 1

	curr_predictions_file.close()

	total_num1 += num_top1
	total_num3 += num_top3
	total_instances += num_total_instances

print (str(total_num1) + '\t' + str(total_num3) + '\t' + str(total_instances))
