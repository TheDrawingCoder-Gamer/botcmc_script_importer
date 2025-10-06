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
    roles_json = json.load(t)

with open("data/role_description.json") as t:
    token_types = json.load(t)

class Role:
    def __init__(self, role_json):
        global token_types
        self.id = role_json["id"]
        self.group = role_json["roleType"]
        self.name = role_json["name"]
        self.lore_desc = None
        self.changes_character_setup = False
        self.first_night_token = False
        self.other_nights_token = False
        self.count = 1
        if self.id not in token_types:
            self.desc = ""
        else:
            token = token_types[self.id]
            self.desc = token["description"]
            if "lore_desc" in token:
                self.lore_desc = token["lore_desc"]
            if "changes_character_setup" in token:
                self.changes_character_setup = token["changes_character_setup"]
            if "first_night_token" in token:
                self.first_night_token = token["first_night_token"]
            if "other_nights_token" in token:
                self.other_nights_token = token["other_nights_token"]
            if "count" in token:
                self.count = token["count"]
            

roles = {}

for role in roles_json:
    roles[role["id"]] = Role(role)



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
    token = roles[item]
    if token.name == "djinn":
        # ignore djinn, we handle jinxes seperately
        continue
    if token.group in grouped_lists:
        grouped_lists[token.group].append(token)
    else:
        print("unseen group?")

jinxes_in_script = []
for char in custom_list:
    if char in jinxes:
        for jinx in jinxes[char]:
            if jinx["id"] in custom_list:
                jinxes_in_script.append({"host": roles[char], "target": roles[jinx["id"]], "reason": jinx["reason"]})

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
    if char_count + line_len + len(token.desc) > max_chars:
        submit_page()
    page.append('{{underlined:true,color:"{}",text:"{}"}}'.format(color,token.name))
    page.append('"\\n"')
    char_count += line_len
    page.append('"{}"'.format(token.desc.replace('"', '\\"')))
    page.append('"\\n\\n"')
    char_count += len(token.desc)
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
        page.append('{{color:"{}",text:"{}"}}'.format(group_colors[host.group],host.name))
        page.append('"\\n"')
        char_count += line_len
        page.append('"/ "')
        page.append('{{color:"{}",text:"{}"}}'.format(group_colors[target.group], target.name))
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


night_sheet_pages = []
night_page = '"'
char_count = 0

def submit_night_page():
    global night_page
    global char_count
    global night_sheet_pages
    night_page += '"'
    night_sheet_pages.append(night_page)
    night_page = '"'
    char_count = 0

def add_night_state(night_state):
    global night_page
    global char_count
    if char_count + line_len > max_chars:
        submit_night_page()
    if night_state == "DUSK":
        night_page += 'Dusk\\n'
    elif night_state == "DAWN":
        night_page += 'Dawn\\n'
    elif night_state == "MINION":
        night_page += 'Minion Info\\n'
    elif night_state == "DEMON":
        night_page += 'Demon Info\\n'
    elif night_state not in custom_list:
        return
    else:
        night_page += '{}\\n'.format(roles[night_state].name)
    char_count += line_len
    
night_page += 'First Night:\\n'
char_count += line_len

for night_state in nightsheet["firstNight"]:
    add_night_state(night_state)

if char_count > 0:
    submit_night_page()

night_page += 'Other Nights:\\n'
char_count += line_len

for night_state in nightsheet["otherNight"]:
    add_night_state(night_state)

if char_count > 0:
    submit_night_page()

pages_txt = '[{}]'.format(','.join(night_sheet_pages))

give_txt = '/give @p minecraft:writable_book[writable_book_content={{pages:{}}}]'.format(pages_txt)

print(give_txt)
print("")

def split_lore(desc):
    res = []
    char_count = 0
    lore_line_len = 30
    words = desc.split(" ")
    cur_line = ""
    for word in words:
        if char_count + len(word) > lore_line_len:
            res.append(cur_line)
            char_count = 0
            cur_line = ""
        cur_line += word.replace('"', '\\"')
        cur_line += " "
        char_count += len(word) + 1
    if len(cur_line) > 0:
        res.append(cur_line)
    return res


slots = []
slot = 0
travellers = []
for item in custom_list:
    token = roles[item]
    if token.group == "townsfolk":
        color = "blue"
    elif token.group == "outsider":
        color = "dark_blue"
    elif token.group == "minion":
        color = "red"
    elif token.group == "demon":
        color = "dark_red"
    elif token.group == "travellers":
        color = "dark_purple"
    else:
        continue
    
    lore = []

    lore_desc = split_lore(token.desc)
    for text in lore_desc:
        lore.append('{{text: "{}",italic:false,color:"white"}}'.format(text))

    if token.changes_character_setup:
        lore.append('{text:"✿",italic:false,color:"gold"}')

    stack_slot = '{{id:"minecraft:paper",components:{{"minecraft:enchantment_glint_override":true,"minecraft:item_name":{{text:"{}",color:"{}"}},lore:[{}] }}}}'.format(token.name, color,','.join(lore))
    if token.group == "travellers":
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