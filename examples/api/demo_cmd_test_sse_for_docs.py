ssl_verify  = True # Can be set to False depending on the situation
web_api_url = "<your_server_url>"  # Remove the trailing "/" character from the URL
user_name   = "<your_user_name>"
access_key  = "<your_access_key>"
infoitem_params = "{...}=..."  # Set as an empty string if there are no parameters
start_tree  = "<your_start_chat_tree>"

import requests
import urllib
import json
import sys
import os
os.system("clear")
try:
    session_id  = ""
    result      = {}
    with requests.get(
        web_api_url + "/sapi/intentchat_begin" +
        "?user_name=" + urllib.parse.quote(user_name, safe="") +
        "&access_key=" + urllib.parse.quote(access_key, safe="") +
        "&infoitem_params=" + urllib.parse.quote(infoitem_params, safe="") +
        "&start_tree=" + urllib.parse.quote(start_tree, safe="") +
        "&sse=" + urllib.parse.quote("True", safe=""),
        headers = {
            'Accept'        : 'text/event-stream',
            'Cache-Control' : 'no-cache',
            'Connection'    : 'keep-alive'
        },
        stream=True,
        verify=ssl_verify
    ) as resp:
        resp.raise_for_status()
        print("---|AI|---------------------------------------------")
        for raw_line in resp.iter_lines(decode_unicode=True):
            if not raw_line: # empty line, the end of a piece of message
                continue
            if raw_line.startswith("<"):
                print("Internal error : " + raw_line)
                sys.exit(1)
            if raw_line.startswith('data:'):
                payload = raw_line[5:].lstrip()
                result = json.loads(payload)    # json.loads() automatically handles escape characters such as \n, \r, ", and ' in the returned JSON text
                if result["return_code"] == "error":
                    print("Internal error : " + result["return_code"] + ", " + result["return_content"])
                    sys.exit(1)
                if "session_id" in result:
                    session_id = result["session_id"]
                # If the return_content (including subsequent return_content) is to be displayed on a web page, 
                # you may need to process characters like <, >, ', ", \n, and \ to avoid conflicts with HTML tags or display issues.
                assert result["return_code"] in ["wait_result","go_on_chat","end_chat","end_chat_by_redirect_to_human"]
                if result["return_content_delta"]!="":
                    print(result["return_content_delta"])
                if result["return_code"] != "wait_result":
                    break
    assert result["return_code"] in ["go_on_chat","end_chat","end_chat_by_redirect_to_human"]
    if result["return_code"] in ["end_chat","end_chat_by_redirect_to_human"]:
        sys.exit(0)
    while True:
        print("---|You|-----------------------------------------------")
        user_input = input().strip() # Input current question
        if user_input == "":         # Press Enter directly to terminate the program
            break
        with requests.get( 
            web_api_url + "/sapi/intentchat_chat" +
            "?user_name="  + urllib.parse.quote(user_name, safe="") +
            "&access_key=" + urllib.parse.quote(access_key, safe="") +
            "&session_id=" + urllib.parse.quote(session_id, safe="") +
            "&user_input=" + urllib.parse.quote(user_input, safe="") +
            "&sse=" + urllib.parse.quote("True", safe=""),
            stream=True,
            verify=ssl_verify
        ) as resp:
            resp.raise_for_status()
            print("---|AI|---------------------------------------------")
            for raw_line in resp.iter_lines(decode_unicode=True):
                if not raw_line: # empty line, the end of a piece of message
                    continue
                if raw_line.startswith("<"):
                    print("Internal error : " + raw_line)
                    sys.exit(1)
                if raw_line.startswith('data:'):
                    payload = raw_line[5:].lstrip()
                    result = json.loads(payload)     # json.loads() automatically handles escape characters such as \n, \r, ", and ' in the returned JSON text
                    if result["return_code"] == "error":
                        print("Internal error : " + result["return_code"] + ", " + result["return_content"])
                        sys.exit(1)
                    assert result["return_code"] in ["wait_result","go_on_chat","end_chat","end_chat_by_redirect_to_human"]
                    if result["return_content_delta"]!="":
                        print(result["return_content_delta"])
                    if result["return_code"] != "wait_result":
                        break
        assert result["return_code"] in ["go_on_chat","end_chat","end_chat_by_redirect_to_human"], "Unknown return_code: " + result["return_code"]
        if result["return_code"] in ["end_chat","end_chat_by_redirect_to_human"]:
            sys.exit(0)
except KeyboardInterrupt: # you can press Ctrl+C to cancel the answer generation process at any time
    print("\n\n(You Canceled)")
