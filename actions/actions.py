# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import json


class ActionInteract(Action):

    def name(self) -> Text:
        return "action_interact"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if tracker.get_slot('data') is None or tracker.get_slot('data') == "null":
            data = {}
            with open('story.json') as f:
                data["objects"] = json.load(f)
        else: data = tracker.get_slot('data')

        print(tracker.latest_message["entities"])
        existing_object = False
        for entity in tracker.latest_message["entities"]:
            if entity["value"] in data["objects"].keys():
                interacted_object = data["objects"][entity["value"]]
                existing_object = True
                if entity["group"] in interacted_object:
                    action = entity["group"]
                    required_objects = []
                    if "need" in interacted_object[action]:
                        for need in interacted_object[action]["need"]:
                            if need not in data["objects"].keys():
                                required_objects.append(need)
                    if len(required_objects) > 0:
                        dispatcher.utter_message(
                            f"You can't {entity['group']} the {entity['value']}. You need: {', '.join(required_objects)}"
                        )
                        continue
                    dispatcher.utter_message(interacted_object[action]["utter"])
                    if not "objects" in interacted_object[action]: continue
                    dispatcher.utter_message(f"You find: {', '.join(interacted_object[action]['objects'].keys())}")
                    for object in interacted_object[action]["objects"].keys():
                        data["objects"][object] = interacted_object[action]["objects"][object]
                else:
                    if entity['group'] == "search":
                        dispatcher.utter_message(f"You can't find anything interesting when searching the {entity['value']}.")
                    else:
                        dispatcher.utter_message(f"You can't {entity['group']} the {entity['value']}.")
            else:
                dispatcher.utter_message(f"There is no {entity['value']}.")
        if not existing_object:
            dispatcher.utter_message(f"You can interact with: {', '.join(data['objects'].keys())}")

        return [SlotSet("data", data)]
