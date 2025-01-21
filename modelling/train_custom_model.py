import random
import spacy
from spacy.training.example import Example
import json

# Load the base model
nlp = spacy.load("en_core_web_sm")

with open("C:/Users/Owner/Desktop/新しいフォルダー/files/train_data.json", 'r') as file:
    TRAIN_DATA = json.load(file)
# Add a new entity recognizer
if "ner" not in nlp.pipe_names:
    ner = nlp.add_pipe("ner", last=True)
else:
    ner = nlp.get_pipe("ner")

# Add new entity labels
for _, annotations in TRAIN_DATA:
    for ent in annotations.get("entities"):
        ner.add_label(ent[2])

# Disable other components for training
other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
with nlp.disable_pipes(*other_pipes):  # only train NER
        optimizer = nlp.create_optimizer()
        for itn in range(10):
            print("Starting iteration " + str(itn))
            random.shuffle(TRAIN_DATA)
            losses = {}
            index = 0
            for text, annotations in TRAIN_DATA:
                try:
                    example = Example.from_dict(nlp.make_doc(text), annotations)
                    nlp.update([example], sgd=optimizer)
                except Exception as e:
                    print(e)
                
            print(losses)
    

# Save the model
nlp.to_disk("custom_ner_model")