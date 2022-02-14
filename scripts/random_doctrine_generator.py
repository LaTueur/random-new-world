import regex
import os
import apply_script as pdx_parser
import codecs

doctrine_pattern = regex.compile(r"(\w+)\s*=\s*{\s*(((?:\w+\s*=\s*{(?3)}|[^{}])*))}")
piety_cost_pattern = regex.compile(r"piety_cost\s*=\s*{(\s*((?:\w+\s*=\s*{(?2)}|[^{}])*))}")
piety_cost_alternative_pattern = regex.compile(r"piety_cost\s*=\s(\w+)")
is_shown_pattern = regex.compile(r"is_shown\s*=\s*{(\s*((?:\w+\s*=\s*{(?2)}|[^{}])*))}")
can_pick_pattern = regex.compile(r"can_pick\s*=\s*{(\s*((?:\w+\s*=\s*{(?2)}|[^{}])*))}")
comment_pattern = regex.compile(r"(#)[^\n]*")
religion_doctrine_preference_pattern = regex.compile(r"has_doctrine = (\w+)")
religion_doctrine_preference_replacement = r"is_target_in_variable_list = { name = religion_doctrine_preferences target = flag:\1 }"

game_path = "C:\Program Files (x86)\Steam\steamapps\common\Crusader Kings III\game" # Can be mod path too

cost_chance_conversion = (
    ("low", "high"),
    ("mid", "averange"),
    ("high", "low"),
    ("massive", "very_low")
)
cost_chance_conversion_syncretism = (
    ("low", "averange"),
    ("mid", "low"),
    ("high", "very_low"),
    ("massive", "really_low")
)
body_replacements = (
    (r"custom_description\s*=\s*{(\s*((?:\w+\s*=\s*{(?2)}|[^{}])*))}", r"\1"),
    (r"text\s*=\s*\w+", r""),
    (r"divide\s*=\s*\w+\s*ceiling\s*=\s*\w+\s*multiply\s*=\s*\w+", r""),
    (r"flag:(\w+)\s*=\s*{\s*is_in_list\s*=\s*selected_doctrines\s*}", r"has_doctrine = \1"),
    (r"if\s*=\s*{\s*limit\s*=\s*{\s*has_doctrine\s*=\s*\w+\s*}\s*multiply\s*=\s*faith_unchanged_doctrine_cost_mult\s*}\s*((?:else_if|else)\s*=\s*{\s*((?:\w+\s*=\s*{(?2)}|[^{}])*)}\s*)*", r"")
)
doctrine_groups_to_skip = (
    "is_christian_faith",
    "is_islamic_faith",
    "is_jewish_faith",
    "special_tolerance",
    "heresy_hostility",
    "nudity_doctrine",
    "unreformed_faith",
    "divine_destiny",
    "full_tolerance",
    "hostility_group",
    "is_eastern_faith",
    "is_gnostic_faith"
)
extra_modifiers = {
    "doctrine_theocracy_temporal": "multiply = rnw_doctrine_theocracy_temporal_multiplier\n",
    "doctrine_gender_male_dominated": "multiply = rnw_doctrine_gender_male_dominated_multiplier\n",
    "doctrine_gender_equal": "multiply = rnw_doctrine_gender_equal_multiplier\n",
    "doctrine_gender_female_dominated": "multiply = rnw_doctrine_gender_female_dominated_multiplier\n",
}

def dumpfiles(path, ending = ".txt"):
    full_text = ""
    for file in os.listdir(path):
        if file.endswith(ending):
            full_text += read_with_removed_comments(path, file)
    return(full_text)

def read_with_removed_comments(path, file):
    file_content = open(os.path.join(path, file)).read()
    return(comment_pattern.sub("", file_content))

def write_output(path, file, text):
    temporary_output_file = open(os.path.join(path, file), "w")
    temporary_output_file.write(text)
    temporary_output_file.close()
    parsed_file = pdx_parser.parse_file(os.path.join(path, file))
    output_file = open(os.path.join(path, file), "wb")
    byte_text = bytes(pdx_parser.reconstruct(parsed_file).encode())
    output_file.write(codecs.BOM_UTF8)
    output_file.write(byte_text)
    output_file.close()

def get_extra_modifiers(name):
    if name in extra_modifiers:
        return(extra_modifiers[name])
    else:
        return("")


#core_doctrines_raw = read_with_removed_comments("doctrines", "00_core_tenets.txt")
#core_doctrines = doctrine_pattern.findall(core_doctrines_raw)

doctrines_raw = dumpfiles(os.path.join(game_path, "common/religion/doctrines"))
doctrine_groups = doctrine_pattern.findall(doctrines_raw)

pick_random_doctrines = ""
remove_all_doctrines = "rnw_remove_all_doctrines_effect = {"

for doctrine_group in doctrine_groups:
    group_name = doctrine_group[0].replace("ż","")
    if group_name in doctrine_groups_to_skip:
        continue
    group_body = doctrine_group[1]
    pick_group = f"rnw_pick_random_{group_name}_effect = {{\nrandom_list = {{"
    pick_group_religion = f"rnw_religion_pick_random_{group_name}_effect = {{\nrandom_list = {{"

    doctrines = doctrine_pattern.findall(group_body)
    for doctrine in doctrines:
        name = doctrine[0]
        if name == "is_available_on_create":
            continue
        body = doctrine[1]

        remove_all_doctrines += f"""
        if = {{
            limit = {{
                has_doctrine = {name}
            }}
            remove_doctrine = {name}
        }}"""

        for i in body_replacements:
            body = regex.sub(i[0], i[1], body)
        piety_cost = piety_cost_pattern.search(body)
        if not piety_cost:
            piety_cost = piety_cost_alternative_pattern.search(body)
            if not piety_cost:
                continue
            else:
                piety_cost = ("",f"value = {piety_cost[1]}")
        is_shown = is_shown_pattern.search(body)
        if not is_shown:
            is_shown = ("","")
        can_pick = can_pick_pattern.search(body)
        if not can_pick:
            can_pick = ("","")
        trigger = is_shown[1] + can_pick[1]
        weight = piety_cost[1]

        for i in (cost_chance_conversion if "_syncretism" not in name else cost_chance_conversion_syncretism):
            weight = weight.replace(f"faith_tenet_cost_{i[0]}", f"rnw_faith_doctrine_{i[1]}_chance")
            weight = weight.replace(f"faith_doctrine_cost_{i[0]}", f"rnw_faith_doctrine_{i[1]}_chance")

        pick_group += f"""
        0 = {{
            trigger = {{
                {trigger}
                NOT = {{ has_doctrine = {name} }}
            }}
            modifier = {{
                add = {{
                    {weight}
                    if = {{
                        limit = {{
                            religion = {{
                                is_target_in_variable_list = {{
                                    name = religion_doctrine_preferences
                                    target = flag:{name}
                                }}
                            }}
                        }}
                        multiply = rnw_religion_doctrine_preferences_modifier
                    }}
                }}
            }}
            add_doctrine = {name}
        }}"""

        trigger = religion_doctrine_preference_pattern.sub(religion_doctrine_preference_replacement, trigger)
        weight = religion_doctrine_preference_pattern.sub(religion_doctrine_preference_replacement, weight)

        pick_group_religion += f"""
        0 = {{
            trigger = {{
                {trigger}
            }}
            modifier = {{
                add = {{
                    {weight}
                    {get_extra_modifiers(name)}
                }}
            }}
            add_to_variable_list = {{
                name = religion_doctrine_preferences
                target = flag:{name}
            }}
        }}"""
            
    
    pick_group += "\n}\n}\n"
    pick_group_religion += "\n}\n}\n"
    pick_random_doctrines += pick_group + pick_group_religion

remove_all_doctrines += "\n}\n"
output = pick_random_doctrines + pick_group_religion + remove_all_doctrines

write_output("../Random New World/common/scripted_effects", "rnw_generated_doctrine_scripted_effects.txt", output)

    
