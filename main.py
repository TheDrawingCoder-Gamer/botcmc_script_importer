import json
import os
import argparse

parser = argparse.ArgumentParser(prog='botcmc_script_importer')
parser.add_argument('input')

args = parser.parse_args()

if not os.path.exists('data/roles.json'):
    import fetch_data
    fetch_data.download_all()

with open("data/roles.json") as t: 
    roles = json.load(t)

with open("data/role_description.json") as t:
    token_types = json.load(t)

for role in roles:
    if role["id"] not in token_types:
        # ???
        token_types[role["id"]] = {
            "group": role["roleType"],
            "name": role["roleType"]
        }
        continue
    token_types[role["id"]]["group"] = role["roleType"]
    token_types[role["id"]]["name"] = role["name"]

with open("data/jinx.json") as t:
    jinx_pre = json.load(t)

jinxes = {}
for jinx in jinx_pre:
    jinxes[jinx["id"]] = jinx["jinx"]
with open("data/nightsheet.json") as t:
    nightsheet = json.load(t)

with open(args.input) as t:
    custom_list = json.load(t)

meta = custom_list[0]
custom_list = custom_list[1:]

grouped_lists = {
    "townsfolk": [],
    "outsider": [],
    "minion": [],
    "demon": [],
    "travellers": [],
}
group_colors = {
    "townsfolk": "blue",
    "outsider": "dark_blue",
    "minion": "red",
    "demon": "dark_red",
    "travellers": "dark_purple",
    "jinxes": "gold"
}
group_names = {
    "townsfolk": "Townsfolk",
    "outsider": "Outsiders",
    "minion": "Minions",
    "demon": "Demons",
    "travellers": "Travellers",
    "jinxes": "Jinxes"
}

for item in custom_list:
    token = token_types[item]
    if token["name"] == "djinn":
        # ignore djinn, we handle jinxes seperately
        continue
    if token["group"] in grouped_lists:
        grouped_lists[token["group"]].append(token)
    else:
        print("unseen group?")

jinxes_in_script = []
for char in custom_list:
    if char in jinxes:
        for jinx in jinxes[char]:
            if jinx["id"] in custom_list:
                jinxes_in_script.append({"host": token_types[char], "target": token_types[jinx["id"]], "reason": jinx["reason"]})

pages = []
group_indexes = {}

pages.append('["",{bold:true,text:"   BLOOD ON THE"},"\\n",{bold:true,text:"    CLOCKTOWER"},"\\n",{bold:true,text:"       SCRIPT"}]')

line_len = 20
line_count = 13
max_chars = line_len * line_count

# due to some weird bug, i must include this to get formatting to work without undue jank
page = ['""']
char_count = 0

def submit_page():
    global page
    global char_count
    if page:
        pages.append('[{}]'.format(','.join(page)))
        page = ['""']
        char_count = 0

def append_token(token,color):
    global page
    global char_count
    if char_count + line_len + len(token["description"]) > max_chars:
        submit_page()
    page.append('{{underlined:true,color:"{}",text:"{}"}}'.format(color,token["name"]))
    page.append('"\\n"')
    char_count += line_len
    page.append('"{}"'.format(token["description"]))
    page.append('"\\n\\n"')
    char_count += len(token["description"])
    char_count += line_len
def handle_group(group_id):
    global page
    global char_count
    group_list = grouped_lists[group_id]
    color = group_colors[group_id]
    name = group_names[group_id]
    if group_list:
        group_indexes[group_id] = len(pages) + 1
        page.append('{{bold:true,color:"{}",text:"{}"}}'.format(color,name))
        page.append('"\\n\\n"')
        char_count += line_len * 2
        for item in group_list:
            append_token(item, color)
    if char_count > 0:
        submit_page()


handle_group("townsfolk")
handle_group("outsider")
handle_group("minion")
handle_group("demon")
handle_group("travellers")



if len(jinxes_in_script) > 0:
    group_indexes["jinxes"] = len(pages) + 1
    page.append('{text:"Jinxes",bold:true,color:"gold"}')
    page.append('"\\n\\n"')
    char_count += line_len * 2
    for jinx in jinxes_in_script:
        host = jinx["host"]
        target = jinx["target"]
        reason = jinx["reason"]
        if char_count + line_len * 2 + len(reason) > max_chars:
            submit_page()
        page.append('{{color:"{}",text:"{}"}}'.format(group_colors[host["group"]],host["name"]))
        page.append('"\\n"')
        char_count += line_len
        page.append('"/ "')
        page.append('{{color:"{}",text:"{}"}}'.format(group_colors[target["group"]], target["name"]))
        page.append('"\\n"')
        char_count += line_len
        page.append('"{}\\n"'.format(reason))
        char_count += len(reason)
if char_count > 0:
    submit_page()

page.append('{bold:true,text:"Index"}')
page.append('"\\n\\n"')
for key in ["townsfolk", "outsider", "minion", "demon", "travellers", "jinxes"]:
    if key in group_indexes:
        page_n = group_indexes[key]
        page.append('{{underlined:true,text:"{}",color:"{}",click_event:{{action:"change_page",page:{}}}}}'.format(group_names[key],group_colors[key],page_n + 1))
        page.append('"\\n"')

pages.insert(1, '[{}]'.format(','.join(page)))


pages_txt = '[{}]'.format(','.join(pages))

give_txt = '/give @p minecraft:written_book[written_book_content={{pages:{},author:"",title:"Script"}}]'.format(pages_txt)

print(give_txt)
print("")


pages = []
page = ['""']
char_count = 0

def add_night_state(night_state):
    global page
    global char_count
    if char_count + line_len > max_chars:
        submit_page()
    if night_state == "DUSK":
        page.append('"Dusk\\n"')
    elif night_state == "DAWN":
        page.append('"Dawn\\n"')
    elif night_state == "MINION":
        page.append('"Minion Info\\n"')
    elif night_state == "DEMON":
        page.append('"Demon Info\\n"')
    elif night_state not in custom_list:
        return
    else:
        page.append('"{}\\n"'.format(token_types[night_state]["name"]))
    char_count += line_len
    
page.append('{text:"First Night:",bold:true}')
page.append('{text:"\\n",bold:false}')
char_count += line_len

for night_state in nightsheet["firstNight"]:
    add_night_state(night_state)

if char_count > 0:
    submit_page()

page.append('{text:"Other Nights:",bold:true}')
page.append('{text:"\\n",bold:false}')
char_count += line_len

for night_state in nightsheet["otherNight"]:
    add_night_state(night_state)

if char_count > 0:
    submit_page()

pages_txt = '[{}]'.format(','.join(pages))

give_txt = '/give @p minecraft:written_book[written_book_content={{pages:{},author:"",title:"Nightsheet"}}]'.format(pages_txt)

print(give_txt)
print("")

slots = []
slot = 0
travellers = []
for item in custom_list:
    token = token_types[item]
    if token["group"] == "townsfolk":
        color = "blue"
    elif token["group"] == "outsider":
        color = "dark_blue"
    elif token["group"] == "minion":
        color = "red"
    elif token["group"] == "demon":
        color = "dark_red"
    elif token["group"] == "travellers":
        color = "dark_purple"
    else:
        continue
    
    lore = []

    if "lore_desc" in token:
        for text in token["lore_desc"]:
            lore.append('{{text: "{}",italic:false,color:"white"}}'.format(text))
    else:
        lore.append('{{text: "{}",italic:false,color:"white"}}'.format(token["description"]))

    stack_slot = '{{id:"minecraft:paper",components:{{"minecraft:enchantment_glint_override":true,"minecraft:item_name":{{text:"{}",color:"{}"}},lore:[{}] }}}}'.format(token["name"], color,','.join(lore))
    if token["group"] == "travellers":
        travellers.append(stack_slot)
    else:
        slots.append('{{slot:{},item:{}}}'.format(slot,stack_slot))
        slot += 1

if len(travellers) > 0:
    bundle = '{{id:"minecraft:bundle",components:{{"minecraft:item_name":"Traveller tokens", "minecraft:bundle_contents":[{}]}}}}'.format(','.join(travellers))
    slots.append('{{slot:{},item:{}}}'.format(slot, bundle))

slots_txt = ','.join(slots)

chest_txt = '/give @p minecraft:shulker_box[container=[{}]]'.format(slots_txt)
print(chest_txt)