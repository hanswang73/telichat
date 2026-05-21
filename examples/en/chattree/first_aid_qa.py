'''
- The ChatTree allows for questions and answers about first aid knowledge
- The core is the "#multi_turn_interact#" node. Users can continuously ask questions about first aid knowledge in this node. The system will search for relevant information in the "first_aid" knowledge base (pointed to in the "#start#" node) based on the user's questions and answer them.
- If the user's question does not find relevant information in the knowledge base, the system will give a default prompt to guide the user to ask other related questions.
- Finally, you can execute "python ./ichatdef/firstapp/py_chattree/fisrt_aid.py" in the server's project directory to generate "first_aid.html", download it locally and open it with a browser, you can see the topology structure of the entire ChatTree and related code information
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
# The definition part of the ChatTree node
# -------------------------------------------------------------------------------------

# start node
start_node = chattree.create_node( "#start#", {
    "chattree_title":"First aid questions and answers", # A short text describing the topic or purpose of this ChatTree
    "system_role":"Q&A robot",
    "user_role":"Questioner",
    "background_information":"You are a Q&A robot responsible for answering user questions",
    "allow_transfer_human_agent":False,
    "static_reference_information":"first_aid", # Point to the knowledge base file name (without extension)
})

# Welcome prompt word
inform_user_node = chattree.create_node( "#inform_user", {
    "inform_content":"Hello, you can ask me questions about first aid knowledge and I will try my best to answer them for you.",
})

# "Question-Answer" cyclic multi turn interaction node
multi_turn_node = chattree.create_node( "#multi_turn_interact#", {
    "notify_not_found_reference_information":"Sorry, there are currently no answers to your questions in my knowledge base. You can try asking some other questions about first aid.", # When the user's question does not find relevant information in the knowledge base, the system will give this prompt
})

# -------------------------------------------------------------------------------------
# Complete topology, ">>" represents the connection relationship between nodes, and the connection relationship here also determines the flow of the dialogue.
# -------------------------------------------------------------------------------------
 
start_node >> inform_user_node >> multi_turn_node

# -------------------------------------------------------------------------------------
# The standard code at the end of every python ChatTree file, the code that renders the ChatTree into HTML file
# -------------------------------------------------------------------------------------

if __name__ == "__main__":
    chattree.render(__file__)