import pandas as pd
import yaml
from pathlib import Path
import random

objects = pd.read_json("generate/objects.json")["objects"]
synonyms = {"nlu": []}
possible_objects = []
for object, object_dict in zip(objects.index, objects):
  synonyms["nlu"].append({"synonym": object, "examples": object_dict["synonyms"]})
  possible_objects.append(object)
  possible_objects.extend(object_dict["synonyms"])

nlu = yaml.safe_load(Path("generate/nlu.yml").open())
for intent_dict in nlu["nlu"]:
  intent, examples = intent_dict["intent"], intent_dict["examples"]
  finished_examples = ""
  if  "<object>" in examples:
    for _ in range(10):
      examples_copy = examples
      while "<object>" in examples_copy:
        examples_copy = examples_copy.replace("<object>", random.choice(possible_objects), 1)
      finished_examples += examples_copy
  else: finished_examples = examples
  intent_dict["examples"] = finished_examples[2:-1].split("\n- ")

def write_nlu(path, dictionary):
  with Path(path).open('w') as fp:
      yaml_string = yaml.safe_dump(dictionary, indent=4, default_flow_style=False, sort_keys=False, width=float("inf"))
      fp.write(yaml_string.replace("    examples:", "    examples: |").replace("   ", " ").replace("  - ", "    - "))

write_nlu('data/nlu/synonyms.yml', synonyms)
write_nlu('data/nlu/nlu.yml', nlu)