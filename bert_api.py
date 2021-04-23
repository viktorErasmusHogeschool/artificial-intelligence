import os
os.system('python -m pip install transformers')
os.system('python -m pip install notebook')
os.system('python -m pip install ipywidgets')
os.system('python -m pip install nltk')
os.system('python -m pip install numpy')
os.system('python -m pip install requests')

# Model definition
import pandas as pd
import requests
import json
import numpy as np
from transformers import *
from transformers import BertTokenizer
from tqdm.notebook import tqdm
import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize

### Docker command
# sudo docker run -p 8501:8501   --mount type=bind,source=/home/ubuntu/colbert,target=/models/colbert   -e MODEL_NAME=colbert -t tensorflow/serving &

class colbert:

    def __init__(self, sentence):
        self.MAX_SENTENCE_LENGTH = 20
        self.MAX_SENTENCES = 5
        self.MAX_LENGTH = 100
        self.sentence = sentence

    def predict(self):

        def return_id(str1, str2, truncation_strategy, length):
            inputs = tokenizer.encode_plus(str1, str2,
                add_special_tokens=True,
                max_length=length,
                truncation_strategy=truncation_strategy)

            input_ids =  inputs["input_ids"]
            input_masks = [1] * len(input_ids)
            input_segments = inputs["token_type_ids"]
            padding_length = length - len(input_ids)
            padding_id = tokenizer.pad_token_id
            input_ids = input_ids + ([padding_id] * padding_length)
            input_masks = input_masks + ([0] * padding_length)
            input_segments = input_segments + ([0] * padding_length)

            return [input_ids, input_masks, input_segments]

        def compute_input_arrays(df, columns, tokenizer):
            model_input = []
            for xx in range((self.MAX_SENTENCES*3)+3):
                model_input.append([])
            
            for _, row in tqdm(df[columns].iterrows()):
                i = 0
                
                # sent
                sentences = sent_tokenize(row.text)
                for xx in range(self.MAX_SENTENCES):
                    s = sentences[xx] if xx<len(sentences) else ''
                    ids_q, masks_q, segments_q = return_id(s, None, 'longest_first', self.MAX_SENTENCE_LENGTH)
                    model_input[i].append(ids_q)
                    i+=1
                    model_input[i].append(masks_q)
                    i+=1
                    model_input[i].append(segments_q)
                    i+=1
                
                # full row
                ids_q, masks_q, segments_q = return_id(row.text, None, 'longest_first', self.MAX_LENGTH)
                model_input[i].append(ids_q)
                i+=1
                model_input[i].append(masks_q)
                i+=1
                model_input[i].append(segments_q)
            
                for xx in range((self.MAX_SENTENCES*3)+3):
                    model_input[xx] = np.asarray(model_input[xx], dtype=np.int32)
                    
                print(model_input[0].shape)
                return model_input

        MODEL_TYPE = 'bert-base-uncased'
        tokenizer = BertTokenizer.from_pretrained(MODEL_TYPE)

        sentence = [{'text':self.sentence}]
        sentence = pd.DataFrame(sentence)
        sentence_input = compute_input_arrays(sentence, ['text'], tokenizer)


        data=json.dumps({"signature_name":"serving_default",

            "instances":[
                {'input_19':sentence_input[0][0].tolist(),
                'input_20':sentence_input[1][0].tolist(),
                'input_21': sentence_input[2][0].tolist(),
                'input_22': sentence_input[3][0].tolist(),
                'input_23': sentence_input[4][0].tolist(),
                'input_24': sentence_input[5][0].tolist(),
                'input_25': sentence_input[6][0].tolist(),
                'input_26': sentence_input[7][0].tolist(),
                'input_27': sentence_input[8][0].tolist(),
                'input_28': sentence_input[9][0].tolist(),
                'input_29': sentence_input[10][0].tolist(),
                'input_30': sentence_input[11][0].tolist(),
                'input_31': sentence_input[12][0].tolist(),
                'input_32': sentence_input[13][0].tolist(),
                'input_33': sentence_input[14][0].tolist(),
                'input_34': sentence_input[15][0].tolist(),
                'input_35': sentence_input[16][0].tolist(),
                'input_36': sentence_input[17][0].tolist()
                    }
                ]
            })

        headers = {"content-type":"application/json"} 
        json_response =requests.post('http://3.16.153.99:8501/v1/models/colbert:predict',
                                    data=data,headers=headers) 
    
        result = json.loads(json_response.text)
        result = result['predictions'][0][0]*100

        return result

model = colbert("During sex, I like to think about becoming a blueberry")
result = model.predict()
print(result)