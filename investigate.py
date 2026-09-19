## Import the necessary modules
import json
from ollama import chat

## Import the function from the module parse_data
from parse_data import load_items, get_unclaimed_items, save_result

## Build your prompt based on the description the user provides 
## and the items that are available in the lost-and-found database.
## The model must follow the rules listed in the README file
## The function should return the system prompt and the user prompt.
## You may need to use json.dumps() to convert the available_items list into a JSON string.

def build_prompt(description, available_items):
    system_prompt ="""You are a campus lost-and-found assistant.
Your job is to find all possible matches for a user's lost item.

Follow these rules:
- Use only the available items provided by the user.
- Not all details of an item must match to be a possible match.
- Return only one valid JSON object.
- Do not include explanations, markdown, or any extra text.
- The JSON object must contain exactly these two keys:
  "matches" and "confidence".
- "matches" must be a list containing all possible matching item IDs.
- "confidence" must be exactly one of: LOW, MEDIUM, HIGH.
- If there is no possible match, "matches" must be an empty list.

The required JSON format is:
{
    "matches": ["ITEM_ID"],
    "confidence": "LOW"
}"""

    items_json =json.dumps(available_items)

    user_prompt =f"""Lost item description:
{description}

Available items:
{items_json}

Find all possible matches."""

    return system_prompt, user_prompt
    

## Logic to ask Qwen for all the possible matches based on the system prompt and user prompt.
## The function should return the response from Qwen.
def ask_qwen(system_prompt, user_prompt):
    response = chat(
        model="qwen3:8b",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )

    return response.message.content

## Logic to parse the response from Qwen and return the result. 
## You may need to use json.loads() to convert the response string into a suitable Python data structure.
def parse_response(response_text):
    result = json.loads(response_text)
    return result


## Logic to validate the result returned by Qwen.
## It should check if the result is a dictionary, contains the keys "matches" and "confidence", and that the values are of the correct type.
## If everything is correct, then it should check if the item IDs in the "matches" list are valid IDs .
def validate_result(result, available_items):
    if not isinstance(result, dict):
        return False

    if "matches" not in result or "confidence" not in result:
        return False

    if len(result) != 2:
        return False

    if not isinstance(result["matches"], list):
        return False

    if not isinstance(result["confidence"], str):
        return False

    if result["confidence"] not in ["LOW","MEDIUM","HIGH"]:
        return False

    valid_ids =[]

    for item in available_items:
        valid_ids.append(item["id"])

    for item_id in result["matches"]:
        if item_id not in valid_ids:
            return False

    return True


## Logic to display the matches found by Qwen in a user-friendly format.
## It should look something like this:
""" 
CAMPUS LOST-AND-FOUND ASSISTANT
==================================================

Describe the item you lost: I lost a black bag somewhere

Searching for possible matches...

MATCH RESULT
--------------------------------------------------
Confidence: MEDIUM

Possible matches:

ID: F101
Item: backpack
Color: black
Location: Library 2nd floor
Date found: 2026-09-15

Result saved to output/match_result.json
 """
## If no matches are found, it should display a message indicating that no matches were found, along with the empty list
def display_matches(result, available_items):
    print("\nMATCH RESULT")
    print("-" * 50)
    print("Confidence:", result["confidence"])

    if len(result["matches"]) ==0:
        print("\nNo matches found.")
        print("Possible matches:", result["matches"])
        return

    print("\nPossible matches:")

    for item_id in result["matches"]:
        for item in available_items:
            if item["id"] == item_id:
                print()
                print("ID:",item["id"])
                print("Item:",item["item"])
                print("Color:",item["color"])
                print("Location:",item["location"])
                print("Date found:",item["date"])
    

## Control center for the entire program.
def main():
    print("CAMPUS LOST-AND-FOUND ASSISTANT")
    print("=" * 50)

    description = input("\nDescribe the item you lost: ")

    items =load_items("found_items.json")
    available_items =get_unclaimed_items(items)

    system_prompt, user_prompt =build_prompt(description, available_items)

    print("\nSearching for possible matches...")

    response_text =ask_qwen(system_prompt,user_prompt)
    result =parse_response(response_text)

    if not validate_result(result,available_items):
        print("\nInvalid response from Qwen.")
        return

    display_matches(result,available_items)

    save_result(result,"output/match_result.json")
    print("\nResult saved to output/match_result.json")


if __name__ == "__main__":
    main()