import os
import sys
import codecs

input_dir_path = sys.argv[1]
output_dir_path = sys.argv[2]

input_file_list = os.listdir(input_dir_path)
for file_path in input_file_list:
	input_file_path = os.path.join(input_dir_path, file_path)
	curr_input_file = codecs.open(input_file_path, 'r', encoding = 'utf-8', errors = 'ignore')
	list_golds = []
	"""curr_best = []
	for line in curr_input_file:
		if(not line.startswith('\t') and len(curr_best) != 0 and len(line) > 1):
			list_golds.append('; '.join(curr_best))
			curr_best = []
		else:
			line = line.strip()
			if(len(line) == 0):
				continue
			
			line_parts = line.split('\t')
			if(len(line_parts) > 2 and line_parts[2] == '1'):
				curr_best.append(line_parts[0].strip())

	if(len(curr_best) != 0):
		list_golds.append('; '.join(curr_best))"""

	for line in curr_input_file:
		if(line.startswith('\t')):
			line = line.strip()
			if(len(line) == 0):
				continue

			line_parts = line.split('\t')
			if(len(line_parts) == 5 and line_parts[4] == '1'):
				list_golds.append(line_parts[0] + '\t' + line_parts[1] + '\t' + line_parts[2])

	curr_input_file.close()
	
	output_file_path = os.path.join(output_dir_path, file_path)
	curr_output_file = codecs.open(output_file_path, 'w', encoding = 'utf-8', errors = 'ignore')
	for line in list_golds:
		curr_output_file.write(line + '\n')

	curr_output_file.close()