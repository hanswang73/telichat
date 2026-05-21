ssl_verify  = True # Can be set to False depending on the situation
web_api_url = "<your_server_url>"  # Remove the trailing "/" character from the URL
user_name   = "<your_user_name>"
access_key  = "<your_access_key>"
infoitem_params = "{...}=..."  # Set as an empty string if there are no parameters
start_tree  = "<your_start_chat_tree>"

import requests
import urllib
import json
import os
os.system("clear")
try:
    result = requests.get(
        web_api_url + "/sapi/intentchat_begin" +
        "?user_name=" + urllib.parse.quote(user_name, safe="") +
        "&access_key=" + urllib.parse.quote(access_key, safe="") +
        "&infoitem_params=" + urllib.parse.quote(infoitem_params, safe="") +
        "&start_tree=" + urllib.parse.quote(start_tree, safe=""),
        verify=ssl_verify
    ).text
    if result.startswith("<"):
        print("Internal error : " + result)
    else:
        result = json.loads(result)
        # json.loads() automatically handles escape characters such as \n, \r, ", and ' in the returned JSON text
        if result["return_code"] == "error":
            print("Internal error : " + result["return_code"] + ", " + result["return_content"])
        else:
            session_id = result["session_id"]
            return_code = result["return_code"]
            return_content = result["return_content"]
            # If the return_content (including subsequent return_content) is to be displayed on a web page, 
            # you may need to process characters like <, >, ', ", \n, and \ to avoid conflicts with HTML tags or display issues.
            while True:
                if return_code == "error":
                    print("Internal error : " + return_code + ", " + return_content)
                    break
                elif return_code == "wait_result":
                    return_content_delta = result["return_content_delta"]
                    print("---|AI|---------------------------------------------")
                    if return_content_delta!="":
                        print(return_content_delta)
                    should_outter_break = False
                    while True:
                        result = requests.get( \
                            web_api_url + "/sapi/intentchat_result" + \
                            "?user_name=" + urllib.parse.quote(user_name, safe="") + \
                            "&access_key=" + urllib.parse.quote(access_key, safe="") + \
                            "&session_id=" + urllib.parse.quote(session_id, safe=""),
                            verify=ssl_verify
                        ).text
                        result = json.loads(result) 
                        return_code    = result["return_code"]
                        return_content = result["return_content"]
                        if return_code == "error":
                            print("Internal error : " + return_code + ", " + return_content)
                            should_outter_break = True
                            break
                        return_content_delta = result["return_content_delta"]
                        if return_code == "wait_result":
                            if return_content_delta!="":
                                print(return_content_delta)
                        elif return_code == "go_on_chat":
                            if return_content_delta!="":
                                print(return_content_delta)
                            break
                        elif return_code in ["end_chat","end_chat_by_redirect_to_human"]:
                            if return_content_delta!="":
                                print(return_content_delta)
                            should_outter_break = True
                            break
                        else:
                            raise Exception("Should not happen")
                    if should_outter_break:
                        break
                else:
                    print("return_code = " + return_code)
                    raise Exception("Should not happen")
                print("---|You|-----------------------------------------------")
                user_input = input().strip() # Input current question
                if user_input == "":         # Press Enter directly to terminate the program
                    break
                result = requests.get( \
                    web_api_url + "/sapi/intentchat_chat" + \
                    "?user_name=" + urllib.parse.quote(user_name, safe="") + \
                    "&access_key=" + urllib.parse.quote(access_key, safe="") + \
                    "&session_id=" + urllib.parse.quote(session_id, safe="") + \
                    "&user_input=" + urllib.parse.quote(user_input, safe=""),
                    verify=ssl_verify
                ).text
                result = json.loads(result) 
                return_code    = result["return_code"]
                return_content = result["return_content"]
except KeyboardInterrupt: # you can press Ctrl+C to cancel the answer generation process at any time
    print("\n\n(You Canceled)")
