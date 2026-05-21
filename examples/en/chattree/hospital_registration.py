'''
- This ChatTree simulates medical treatment registration. The user communicates with the hospital registration robot to provide relevant medical treatment information (such as visiting department, visit date, visit time, etc.)
- The core of the ChatTree is the "#multi_turn_interact#" node, especially the check_registered_info() function pointed to by the "execution function" attribute: This function will be executed during each round of dialogue, verify the information provided by the user, and give corresponding prompts (through the {_multi_turn_interact_dynamic_prompt_} system InfoItem) to guide the user to provide correct or more specific information until the registration conditions are met or a system exception occurs and the user needs to exit.
- This kind of business logic implemented with the "#multi_turn_interact#" node as the core is only suitable for situations where there are relatively few infoitems that need to be collected (for example, there are only 3 in this ChatTree). If there are more infoitem that need to be collected, or the logical relationship between the infoitem is more complex, you need to use several "#single_turn_interact#" nodes to implement it. For details, see "TMC.py" / "TMC_book_flight.py" ChatTree
- At the same time, during the entire process, the system can provide relevant knowledge of the "first aid knowledge, hospital treatment and registration guide" knowledge base at any time based on the user's input without interrupting the logic of the dialogue process.
- Finally, you can execute "python ./ichatdef/firstapp/py_chattree/hospital_registration.py" in the server's project directory to generate "hospital_registration.html", download it locally and open it with a browser, you can see the topology structure of the entire ChatTree and related code information
'''

# -------------------------------------------------------------------------------------
# Standard code header for every python ChatTree file
# -------------------------------------------------------------------------------------

import sys, os

project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)
from chattree_def import *

chattree = ChatTree()

# -------------------------------------------------------------------------------------
# The definition part of the CHatTree node
# -------------------------------------------------------------------------------------

from datetime import datetime, timedelta
import random, re

department_list = [
    'Cardiovascular Medicine', 'Respiratory Medicine', 'Gastroenterology', 'Neurology', 'Endocrinology',
    'General Surgery', 'Orthopedics', 'Urology', 'Gynecology', 'Obstetrics', 'Pediatrics', 'Ophthalmology', 
    'ENT', 'Stomatology', 'Dermatology',
]

# start node
start_node = chattree.create_node( "#start#", {
    "chattree_title":"Hospital registration service", # A short text describing the topic or purpose of this ChatTree
    "system_role":"hospital registration robot",
    "user_role":"patient",
    "background_information":"You are responsible for registering patients for medical treatment and answering related questions",
    "allow_transfer_human_agent":False,
    "static_reference_information":"first_aid_and_hospital_consultation_and_registration_guide", # Point to the knowledge base file name (without extension)
})

# Before entering the following multi_turn_interact nodes, give the user a welcome prompt.
def execute_srcipt(ctx):
    ctx["{_multi_turn_interact_dynamic_prompt_}"] = "Ask the patient: 'Hello, which department and what time would you like to register for?'"
execute_srcipt_node = chattree.create_node( "#activity#execute_script#", {
    "function":execute_srcipt,
})

# The core nodes and related functions of this CHatTree
def register(register_department, register_date, register_time): # Simulated registration function (returns relevant results based on probability). In actual applications, the hospital's registration system interface will be called here.
    if random.random() < 0.1:
        return False, "system exception"
    if random.random() < 0.3:
        return False, "no appointments available"
    return True, "JZ123456"
def check_registered_info(ctx):  # The core function of the multi_turn_interact node will be executed during each round of dialogue.
    ctx["{_multi_turn_interact_dynamic_prompt_}"] = ""
    if ctx["{visiting_department}"].state() == 1:
        if ctx["{visiting_department}"].as_str().lower() not in [department.lower() for department in department_list]:
            ctx["{visiting_department}"].clear_info()
            ctx["{_multi_turn_interact_dynamic_prompt_}"] = (
                ctx["{_multi_turn_interact_dynamic_prompt_}"].as_str() + 
                "Remind patient that he or she can only register in the following departments: " +
                str(department_list) + "\n"
            )
    else:
        ctx["{_multi_turn_interact_dynamic_prompt_}"] = (
            ctx["{_multi_turn_interact_dynamic_prompt_}"].as_str() + 
            "Ask the patient to inform the department where he or she will be admitted. "
            "If the patient is not sure which department, the relevant department can be recommended to the patient based on the symptom information provided by the patient after asking about the patient's symptoms and then you can ask the patient to confirm. "
            "Only " + str(department_list) + " departments is OK. "
            "At the same time, give the patient relevant suggestions based on the symptom information provided by the patient\n"
        )
    if ctx["{date_of_visit}"].state() == 1:
        if not re.match(r"\d{4}-\d{2}-\d{2}", ctx["{date_of_visit}"].as_str()):
            ctx["{date_of_visit}"].clear_info()
            ctx["{_multi_turn_interact_dynamic_prompt_}"] = ctx["{_multi_turn_interact_dynamic_prompt_}"].as_str() + "Prompt patients to provide correct date of visit\n"
        else:
            try:
                registered_date_obj = datetime.strptime(ctx["{date_of_visit}"].as_str(), "%Y-%m-%d")
                if registered_date_obj < datetime.now() or registered_date_obj > datetime.now() + timedelta(days=10):
                    ctx["{date_of_visit}"].clear_info()
                    ctx["{_multi_turn_interact_dynamic_prompt_}"] = ctx["{_multi_turn_interact_dynamic_prompt_}"].as_str() + "Remind patients that they can only register for appointments within 10 days.\n"
            except ValueError:
                ctx["{date_of_visit}"].clear_info()
                ctx["{_multi_turn_interact_dynamic_prompt_}"] = ctx["{_multi_turn_interact_dynamic_prompt_}"].as_str() + "Prompt patient to provide correct date of visit\n"
    else:
        ctx["{_multi_turn_interact_dynamic_prompt_}"] = ctx["{_multi_turn_interact_dynamic_prompt_}"].as_str() + "Ask the patient to provide the date of visit\n"
    if ctx["{visiting_time_is_in_the_morning_or_afternoon}"].state() == 1:
        if ctx["{visiting_time_is_in_the_morning_or_afternoon}"].as_str().lower() not in ["morning","afternoon"]:
            ctx["{visiting_time_is_in_the_morning_or_afternoon}"].clear_info()
            ctx["{_multi_turn_interact_dynamic_prompt_}"] = ctx["{_multi_turn_interact_dynamic_prompt_}"].as_str() + "Remind patient that visiting time can only be in the morning or afternoon\n"
    else:
        ctx["{_multi_turn_interact_dynamic_prompt_}"] = ctx["{_multi_turn_interact_dynamic_prompt_}"].as_str() + "Tell the patient whether the visting time is in the morning or afternoon\n"
    if ctx["{visiting_department}"].state() == 1 and ctx["{date_of_visit}"].state() == 1 and ctx["{visiting_time_is_in_the_morning_or_afternoon}"].state() == 1:
        assert ctx["{_multi_turn_interact_dynamic_prompt_}"].as_str() == ""
        if_success, ret_val = register(ctx["{visiting_department}"].as_str(), ctx["{date_of_visit}"].as_str(), ctx["{visiting_time_is_in_the_morning_or_afternoon}"].as_str())
        if if_success:
            ctx["{_multi_turn_interact_exit_reason_}"] = "Registered successfully"
            ctx["{_multi_turn_interact_dynamic_prompt_}"] = f"Tell the patient that the registration has been successful and the treatment number is {ret_val}\n"
        else:
            if ret_val == "no appointments available":
                ctx["{visiting_department}"].clear_info()
                ctx["{date_of_visit}"].clear_info()
                ctx["{visiting_time_is_in_the_morning_or_afternoon}"].clear_info()
                ctx["{_multi_turn_interact_dynamic_prompt_}"] = f"Tell patient 'no appointments available, please choose another date and time or other department'\n"
            elif ret_val == "system exception":
                ctx["{_multi_turn_interact_dynamic_prompt_}"] = f"Tell patient 'system exception, please try again later'\n"
                ctx["{_multi_turn_interact_exit_reason_}"] = "Tell patient 'system exception, please try again later'"
multi_turn_node = chattree.create_node( "#multi_turn_interact#", {
    "extract_info":[ # Each round of dialogue will extract these infoitems and store the extracted information in 'ctx' for use by the function check_registered_info()
        {
            "infoitem":"{visiting_department}",
            "infoitem_constraint":"It must be the department provided by the patient or confirmed by the patient.",
            "infoitem_options":department_list,
            "infoitem_options_modifier":['open_ended']
        },
        {"infoitem":"{date_of_visit}", "infoitem_constraint":"The format is YYYY-MM-DD"},
        {"infoitem":"{visiting_time_is_in_the_morning_or_afternoon}", "infoitem_constraint":"It can only be 'morning' or 'afternoon'"},
    ],
    "execute_function":check_registered_info, # Each round of dialogue will be executed
})

# -------------------------------------------------------------------------------------
# Complete topology, ">>" represents the connection relationship between nodes, and the connection relationship here also determines the flow of the dialogue.
# -------------------------------------------------------------------------------------

start_node >> execute_srcipt_node >> multi_turn_node

# -------------------------------------------------------------------------------------
# The standard end of every python ChatTree file, the code that renders ChatTree into an HTML file
# -------------------------------------------------------------------------------------

if __name__ == "__main__":
    chattree.render(__file__)