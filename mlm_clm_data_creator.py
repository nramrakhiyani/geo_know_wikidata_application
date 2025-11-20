import os
import sys
import codecs

from util import *

gold_folder_path = sys.argv[1]
premises_folder_path = sys.argv[2]
final_output_folder_path = sys.argv[3]

gold_folder_files = os.listdir(gold_folder_path)
total_data_lines = 0
for file_name in gold_folder_files:
	gold_file_path = os.path.join(gold_folder_path, file_name)
	premises_file_path = os.path.join(premises_folder_path, file_name)
	output_file_path = os.path.join(final_output_folder_path, file_name)

	neighbour_to_dir = {}
	gold_file = codecs.open(gold_file_path, 'r', encoding = 'utf-8', errors = 'ignore')
	for line in gold_file:
		line = line.strip()
		if(len(line) == 0):
			continue

		line_parts = line.split('\t')
		neighbour_to_dir[line_parts[2]] = line_parts[1]
	gold_file.close()

	output_file = codecs.open(output_file_path, 'w', encoding = 'utf-8', errors = 'ignore')
	premises_file = codecs.open(premises_file_path, 'r', encoding = 'utf-8', errors = 'ignore')
	for line in premises_file:
		line = line.strip()
		if(len(line) == 0):
			continue

		line_parts = line.split('\t')

		reverse = False
		if(line_parts[3] == '1'):
			reverse = True

		curr_neighbour = line_parts[0]
		if(curr_neighbour in neighbour_to_dir):
			curr_direction = neighbour_to_dir[curr_neighbour]
			if(reverse):
				curr_direction = get_reverse_direction(curr_direction)

			curr_line = line_parts[2]
			curr_line = curr_line.replace('{}', '[MASK]')
			output_file.write(curr_line + '\t' + curr_direction + '\n')
			total_data_lines += 1

	output_file.close()
	premises_file.close()

print ('Total data lines: ' + str(total_data_lines))