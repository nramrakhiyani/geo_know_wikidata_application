# Wikipedia Geography Orientation Extraction 
This repository contains the code and data used for the paper 'Extracting Orientation Relations between Geo-political Entities from Wikipedia text', submitted to the First International Workshop on Geographic Information Extraction from Texts to be held with ECIR 2023, Dublin, Ireland.

## Environment and Resources setup
0. Create a python env and install the packages and corresponding versions mentioned in requirements.txt

1. Setting up the resources folder
* &rarr; Download the files of the huggingface transformers **bart-large-mnli**, **roberta-large-mnli**, **bart-large** and **bert-large-cased** from huggingface model hub and place them in the corresponding directories such as *transformers/bert-large-cased* for bert-large-cased.

2. Setting up the data folder
* &rarr; Obtain the dataset, placed in the folder data_appl_wikidata.zip, at the following Google Drive link (you are required to request access thru a gmail ID): [geo_data_all](https://drive.google.com/drive/folders/13s2hzDxm6tgXqPxhVK_5248edgOAwKOb?usp=sharing)

* &rarr; Unzip the downloaded file into a folder named "data" and keep as a sibling to the code files

## Commands
1. Dataset creation (already done and files are available in the data folder)

python data_all_sent_fetcher.py data

2. Experimentation Data generation

python experimentation_data_generation.py data

3. NLI based extraction

python nli_based_extraction *data_folder* *model_name* *hypothesis type (patterns/simple)*

4. Evaluate NLI predictions

python evaluate_nli_predictions *gold_path* *nli predictions folder*

5. Prompts based extraction

python prompts_based_extraction *data_folder* *model_name* *prompts_or_prompts_with_demos* 

6. Evaluate prompt predictions

python evaluate_prompt_predictions *gold_path* *predictions_path* *with_demos*