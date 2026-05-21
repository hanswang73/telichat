'''
- This ChatTree simulates the dialogue flow of a 911 emergency phone service.
- User seeks help by calling the 911 emergency phone service, and the system needs to quickly gather relevant information from the user (such as injury or illness, specific location, contact phone number, etc.) and provide corresponding advice based on this information or pass the information to the backend system to dispatch an ambulance.
- At the same time, the system can provide relevant knowledge from the "first_aid" knowledge base based on the user's input at any time during the dialogue, and respond according to the "response_scripts" defined in the "#start#" node, without interrupting the logic of the dialogue flow.
- This ChatTree is designed to quickly and effectively gather relevant information from the user, and when the information provided by the user is not specific enough or does not meet the requirements, it can guide the user to provide more specific or correct information through reasonable prompts. At the same time, it is also important to transfer to manual service at the appropriate time to ensure that the user's needs can be met.
- At the same time, many nodes in this ChatTree have "before_execution" or "after_execution" functions where you can set breakpoints for debugging.
- Finally, you can execute "python ./ichatdef/firstapp/py_chattree/911.py" in the project directory of the server to generate "911.html". Download it to your local machine and open it with a browser to see the topology structure of the entire ChatTree and related code information.
'''

# -------------------------------------------------------------------------------------
# Every python ChatTree file should start with the following standard code header
# -------------------------------------------------------------------------------------

import sys, os

project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)
from chattree_def import *

chattree = ChatTree()

# -------------------------------------------------------------------------------------
# ChatTree node definition part
# -------------------------------------------------------------------------------------

import re

# "#start#" node and its related functions
def start_node_after_execution(ctx): # Note: This function will be called after the "#start#" node is executed, you can add some debug output or other logic here.
    print("DEBUG OUTPUT : start_node_after_execution")
    pass
start_node = chattree.create_node( "#start#", {
    "chattree_title":"911 emergency phone service", # a brief text describing the theme or purpose of this ChatTree
    "system_role":"911 Emergency Center's seat customer service",
    "user_role":"911 caller",
    "background_information":
        "You must answer with professional knowledge and quickly gather relevant user information.\n"
        "Be patient and caring—understand and reassure.\n"
        "Skilled in first aid, experienced, highly professional.\n"
        "Keep language brief and precise.\n"
        "The contact phone number may or may not be the calling number.",
    "allow_transfer_human_agent":True,
    "static_reference_information":"first_aid", # Point to the knowledge base file name (without extension)
    "startup_infoitem":"{_phone_number_}",
    "response_scripts":[                       # When the user's input matches the corresponding intention, the system will provide feedback based on the words defined here. Note that the intentions and words here are just examples. You can adjust and supplement them according to the actual situation.
        { "intent":"Expects to end the dialogue", "response":"Please don't worry, we'll get to you as soon as possible." },
        { "intent":"Expects to be transferred to a human agent", "response":"<To politely say that you yourself are the 'human agent' and there's no need to transfer to one.>" },
        { "intent":"Asks to wait a moment", "response":"No rush." },
        { "intent":"Expresses thanks", "response":"You're very welcome, we're just doing our job." },
        { "intent":"Wants to know first aid methods", "response":"<Provide advice based on common medical and first-aid knowledge with brief and effective replies. If the issue is too complex, ask the user to wait for the doctor to handle it on-site. Be sure to use a gentle tone.>" },
    ],
    "before_execution" : lambda ctx : ( # This lambda function will be called before the "#start#" node is executed. You can add some debugging output or other logic here
        print("DEBUG OUTPUT : start_node_before_execution"),
        _:=0
    ),
    "after_execution"  : start_node_after_execution,
})

# Ask what help is needed and related functions
def welcome_node_before_execution(ctx):  # Same as above, no explanation below
    print("DEBUG OUTPUT : welcome_node_before_execution")
    pass
welcome_node = chattree.create_node( "#single_turn_interact#", {
    "infoitem":"{things_that_need_help}",
    "infoitem_modifier":["fixed","required"],
    "system_question": "Hello, this is the 911 emergency center. How can we assist you?",
    "before_execution": welcome_node_before_execution,
    "after_execution" : lambda ctx : (  # Same as above, no explanation below
        print("DEBUG OUTPUT : welcome_node_after_execution"),
        _:=0
    ),
})

# Determine whether it is within the processing range of 911. Note that this is a "description" type "#condition#" node. The system will call a large model to make the judgment. You need to describe the judgment criteria of this condition as clearly and specifically as possible in the "description" field.
def judge_if_in_911_scope_node_before_execution(ctx):
    print("DEBUG OUTPUT : judge_if_in_911_scope_node_before_execution")
    pass
def judge_if_in_911_scope_node_after_execution(ctx):
    print("DEBUG OUTPUT : judge_if_in_911_scope_node_after_execution")
    pass
judge_if_in_911_scope_node = chattree.create_node( "#condition#description", {
    "description":"[{things_that_need_help}] is not within the scope of the 911 emergency hotline.",
    "before_execution": judge_if_in_911_scope_node_before_execution,
    "after_execution": judge_if_in_911_scope_node_after_execution,
})

# If it is not within the processing range of 911, prompt the user ----- For the topological connection relationship, see the last code based on “>>”, the same below
inform_user_out_of_scope_of_911_node = chattree.create_node( "#inform_user#", {
    "inform_content":"<Explain to the user that this is the 911 emergency number and recommend other phone numbers that can be called.>"
})

# After the above prompts, ask again what help is needed
go_back_to_welcome_node = chattree.create_node( "#activity#ask_again", {
    "infoitem":"{things_that_need_help}",
    "before_execution" : lambda ctx : (
        print("DEBUG OUTPUT : go_back_to_welcome_node_before_execution"),
        _:=0
    ),
    "after_execution" : lambda ctx : (
        print("DEBUG OUTPUT : go_back_to_welcome_node_after_execution"),
        _:=0
    ),
})

# If it is within the processing range of 911, continue to ask about the specific injury or illness or physical condition
ask_illness_node = chattree.create_node( "#single_turn_interact#", {
    "infoitem":"{specific_injury_condition_or_physical_state}",
    "infoitem_constraint":"descriptions of asymptomatic physical conditions are also considered",
    "infoitem_modifier":["incremental","required"], # Note that there is an "incremental" in the modifier of the infoitem here, because the patient may continue to add {specific_injury_condition_or_physical_state} ----- The same below
    "system_question": "<Ask for details about the injury, illness, or physical condition based on the context>", # The question text here is enclosed by greater than or less signs, indicating that it needs to be generated based on context rather than fixed text.
})

# Determine whether the description of the injury, illness or physical condition provided by the patient is specific enough. Note that this is also a "description" type "#condition#" node.
judge_if_illness_description_specific_enough_node = chattree.create_node( "#condition#description", {
    "description":"'{specific_injury_condition_or_physical_state}' does not clearly describe the patient's state of consciousness, duration of symptoms, location and extent of the trauma (or illness), etc."
})

# If the description of the injury or illness or physical condition provided by the patient is not specific enough, prompt the user to provide a more specific description.
inform_user_provide_more_specific_illness_desciption_node = chattree.create_node( "#inform_user#", {
    "inform_content":"<Use appropriate reasons (not too many) according to the context in terms of state of consciousness, duration of symptoms, location and extent of the trauma (or illness), etc. Ask the user to provide more specific injuries or illnesses or physical conditions>"
})

# After the above prompts, ask again {specific_injury_condition_or_physical_state}
go_back_to_ask_illness_node = chattree.create_node( "#activity#ask_again", {
    "infoitem":"{specific_injury_condition_or_physical_state}"
})

# If the description of the injury or illness or physical condition provided by the patient is specific enough, continue to ask for the specific location
ask_location_node = chattree.create_node( "#single_turn_interact#", {
    "infoitem":"{caller_current_specific_location}",
    "infoitem_modifier":["incremental","required"], # There is also "incremental" here
    "system_question": "May I ask where you are currently located?",
})

# Determine whether the location description provided by the patient is specific enough. Note that this is also a "description" type "#condition#" node.
judge_if_location_description_specific_enough_node = chattree.create_node( "#condition#description", {
    "description":"In terms of house numbers or landmarks, '{caller_current_specific_location}' is not specific enough as a destination for the 911 ambulance (a house number or a specific reference is specific enough)."
})

# If the location description provided by the patient is not specific enough and has been asked many times (greater than or equal to 5), the user will be prompted and transferred to manual service (see below)
judge_if_location_description_not_specific_enough_too_many_times_node = chattree.create_node( "#condition#script", {
    "function": lambda ctx : ctx['{_curr_node_exec_count_}'].as_num() >= 5
})

# That is the prompt after asking multiple times above
inform_user_when_ask_location_too_many_times_node = chattree.create_node( "#inform_user#", {
    "inform_content":"<Indicates that the location provided by the user is still not specific enough and will be transferred to manual service>",
})

# That is, the transfer manual service after asking multiple times above
transfer_human_agent_when_ask_location_too_many_times_node = chattree.create_node( "#activity#transfer_human_agent", {})

# If the location description provided by the patient is not specific enough and the maximum number of queries has not been reached, prompt the user to provide a more specific location description.
inform_user_provide_more_specific_location_desciption_node = chattree.create_node( "#inform_user#", {
    "inform_content":"<From aspects such as the house number or landmarks, use appropriate reasons based on the context to ask the user to provide a detailed and specific location.>"
})

# After the above prompts, ask again {caller_current_specific_location}
go_back_to_ask_loction_node = chattree.create_node( "#activity#ask_again", {
    "infoitem":"{caller_current_specific_location}"
})

# After the location description provided by the patient is specific enough, continue to ask if the caller number can be contacted (because the caller number may not be the contact phone number)
ask_if_is_the_calling_number_node = chattree.create_node( "#single_turn_interact#", {
    "infoitem":"{can_the_calling_number_be_contacted}",
    "infoitem_modifier":["explicit","required"],
    "system_question": "Your calling number is {_phone_number_}, is it okay to contact this number?",
})

# Intent branch: Contact the incoming call number / and related functions
def is_calling_number_node_before_execution(ctx):
    print("DEBUG OUTPUT : is_calling_number_node_before_execution")
    pass
is_calling_number_node = chattree.create_node( "#user_intent#", {
    "intent":"Contact the incoming call number",
    "before_execution": is_calling_number_node_before_execution,
    "after_execution" : lambda ctx : (
        print("DEBUG OUTPUT : is_calling_number_node_after_execution"),
        _:=0
    ),
})

# Intent branch: Not contact the incoming call number
not_calling_number_node = chattree.create_node( "#user_intent#", {
    "intent":"Not contact the incoming call number",
})

# After the "Contact the incoming call number" intent branch, assign the value of the infoitem {_phone_number_} passed in when the ChatTree started to {contact_phone_number}, which is the standard infoitem name we use in subsequent dialogues.
def assign_contact_phone_number_node_function(ctx):
    ctx['{contact_phone_number}'] = ctx['{_phone_number_}'].as_str()
assign_contact_phone_number_node = chattree.create_node( "#activity#execute_script", {
    "function": assign_contact_phone_number_node_function,
    "before_execution" : lambda ctx : (
        print("DEBUG OUTPUT : assign_contact_phone_number_node_before_execution"),
        _:=0
    ),
    "after_execution" : lambda ctx : (
        print("DEBUG OUTPUT : assign_contact_phone_number_node_after_execution"),
        _:=0
    ),
})

# After the "Not contact the incoming call number" intent branch, ask for {contact_phone_number}
ask_contact_phone_number_node = chattree.create_node( "#single_turn_interact#", {
    "infoitem":"{contact_phone_number}",
    "infoitem_constraint":"may be different from incoming call number",
    "infoitem_modifier":["repeat","required","explicit"],
    "system_question": "Please provide the contact phone number.",
})

# Judge the format of the contact phone number provided by the patient. Note that this is a "script" type "#condition#" node. You need to use code to implement the judgment logic.
def judge_phone_number_format_node_before_execution(ctx):
    print("DEBUG OUTPUT : judge_phone_number_format_node_before_execution")
    pass
def judge_phone_number_format_node_after_execution(ctx):
    print("DEBUG OUTPUT : judge_phone_number_format_node_after_execution")
    pass
judge_phone_number_format_node = chattree.create_node( "#condition#script", {
    "function": lambda ctx : not re.search(r'(^|[^0-9])((1[2-9][0-9]{2}[2-9][0-9]{2}[0-9]{4})|([2-9][0-9]{2}[2-9][0-9]{2}[0-9]{4}))([^0-9]|$)', ctx['{contact_phone_number}'].as_str().replace(' ','')),
    "before_execution": judge_phone_number_format_node_before_execution,
    "after_execution": judge_phone_number_format_node_after_execution,
})

# If the contact phone number provided by the patient is in an incorrect format, prompt the user
inform_user_invalid_phone_number_node = chattree.create_node( "#inform_user#", {
    "inform_content":"The phone number you provided ({contact_phone_number}) doesn't seem to be correct.",
})

# After the above prompts, ask again {contact_phone_number}
go_back_to_contact_phone_number_node = chattree.create_node( "#activity#ask_again", {
    "infoitem":"{contact_phone_number}"
})

# After processing {contact_phone_number}, next prompt a summary of the information provided by the previous patient
def summarize_info_node_after_execution(ctx):
    print("DEBUG OUTPUT : summarize_info_node_after_execution")
    pass
summarize_info_node = chattree.create_node( "#inform_user#", {
    "inform_content":"<Summarize the related injuries or medical conditions, specific location, and contact phone number based on the previous communication.>",
    "before_execution" : lambda ctx : (
        print("DEBUG OUTPUT : summarize_info_node_before_execution"),
        _:=0
    ),
    "after_execution": summarize_info_node_after_execution,
})

# After prompting to summarize the information, ask the user to confirm that the information is correct. Note that this is another "#single_turn_interact#" node, because we need to continue to refine the user's intention branch under this node.
confirm_info_node = chattree.create_node( "#single_turn_interact#", {
    "infoitem":"{confirm_if_all_information_is_correct}",
    "infoitem_modifier":["implicit","fixed","required"],
    "system_question": "Please confirm if all the information is correct?",
})

# Intent branch: append or change above information
append_or_change_info_node = chattree.create_node( "#user_intent#", {
    "intent":"append or change above information"
})

# Intent branch: confirm all above information is correct
confirm_correct_node = chattree.create_node( "#user_intent#", {
    "intent":"confirm all above information is correct"
})

# After the "append or change above information" intention branch, summarize the relevant information again and prompt the user
# Note: After the patient adds or corrects the relevant information here, the previous related "#single_turn_interact#" node will be automatically processed (including judging whether the content is specific), and then summarized again here.
summarize_info_again_node = chattree.create_node( "#inform_user#", {
    "inform_content": "<Based on the previous communication, summarize the user's injury or illness, specific location, and contact phone number.>"
})

# After the above summary information is prompted again, the user is asked again to confirm that the information is correct, thus forming a loop. This loop will not be broken out until the user confirms that the information is correct.
go_back_to_confirm_node = chattree.create_node( "#activity#ask_again", {
    "infoitem":"{confirm_if_all_information_is_correct}"
})

# After the user confirms that the information is correct, call the HTTP interface to pass the relevant information to the back-end system. Note that this is an "#activity#call_http" node because it will affect the system state (call the interface and perform different prompts or transfers based on the results). You need to implement specific calling logic here.
def call_http_node_before_execution(ctx):
    print("DEBUG OUTPUT : call_http_node_before_execution")
    pass
call_http_node = chattree.create_node( "#activity#call_http", {
    "url":"http://127.0.0.1:8000/api/intentchat_call_http_test?action=dispatch_ambulance&phone_number={contact_phone_number}&address={caller_current_specific_location}&situation={things_that_need_help},{specific_injury_condition_or_physical_state}",
    "before_execution": call_http_node_before_execution,
    "after_execution" : lambda ctx : (
        print("DEBUG OUTPUT : call_http_node_after_execution"),
        _:=0
    ),
})

# Determine the result of calling the HTTP interface. If the interface call fails or the returned result indicates failure, the user will be prompted and transferred to manual service. Note that this is another "script" type "#condition#" node, which requires you to use code to implement the judgment logic.
check_http_result_node = chattree.create_node( "#condition#script", {
    "function": lambda ctx : ctx['{http_result_1}'].state() != 1 or ctx['{http_result_1}'].as_str().startswith('error')
})

# If the HTTP interface call fails or the returned result indicates failure, first prompt the user and then transfer to manual service
inform_user_when_http_result_error_node = chattree.create_node( "#inform_user#", {
    "inform_content":"Sorry, there is something wrong with the system and we are transferring to manual service."
})

# After the above prompt, transfer to manual service
transfer_human_agent_when_http_result_error_node = chattree.create_node( "#activity#transfer_human_agent", {})

# If the HTTP interface call is successful and the returned result indicates success, the user will be prompted that the relevant information has been confirmed, the ambulance is on the way, and the user will be asked to keep their mobile phone open.
last_inform_node = chattree.create_node( "#inform_user#", {
    "inform_content":"Don't worry, we will get to you as soon as possible. Please keep your phone available."
})

# -------------------------------------------------------------------------------------
# Complete topology, ">>" represents the connection relationship between nodes, and the connection relationship here also determines the flow of the dialogue.
# -------------------------------------------------------------------------------------

start_node >> [
    welcome_node >> judge_if_in_911_scope_node >> inform_user_out_of_scope_of_911_node >> go_back_to_welcome_node,
    ask_illness_node >> judge_if_illness_description_specific_enough_node >> inform_user_provide_more_specific_illness_desciption_node >> go_back_to_ask_illness_node,
    ask_location_node >> judge_if_location_description_specific_enough_node >> [
        judge_if_location_description_not_specific_enough_too_many_times_node >> inform_user_when_ask_location_too_many_times_node >> transfer_human_agent_when_ask_location_too_many_times_node,
        inform_user_provide_more_specific_location_desciption_node >> go_back_to_ask_loction_node,
    ],
    ask_if_is_the_calling_number_node >> [
        is_calling_number_node >> assign_contact_phone_number_node,
        not_calling_number_node >> ask_contact_phone_number_node >> judge_phone_number_format_node >> inform_user_invalid_phone_number_node >> go_back_to_contact_phone_number_node
    ],
    summarize_info_node >> confirm_info_node >> [
        append_or_change_info_node >> summarize_info_again_node >> go_back_to_confirm_node,
        confirm_correct_node >> call_http_node >> [
            check_http_result_node >> inform_user_when_http_result_error_node >> transfer_human_agent_when_http_result_error_node,
            last_inform_node
        ]
    ]
]

# -------------------------------------------------------------------------------------
# The standard code at the end of every python ChatTree file, the code that renders the ChatTree into HTML file
# -------------------------------------------------------------------------------------

if __name__ == "__main__":
    chattree.render(__file__)