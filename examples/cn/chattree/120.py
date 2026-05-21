'''
- 该对话树模拟一个120急救电话服务的对话流程
- 用户通过拨打120急救电话寻求帮助，系统需要快速获取用户的相关信息（如伤情或病情、具体地点、联系电话号码等），并根据这些信息提供相应的建议或者将信息传递给后端系统以派遣救护车
- 同时在整个过程中，系统可以根据用户的输入，随时提供 “急救知识” 知识库的相关知识，并根据 “#开始#” 节点中的 “应对话术” 属性进行反馈，而不会打断对话流程的逻辑
- 该对话树的设计重点在于如何快速有效地获取用户的相关信息，并在用户提供的信息不够具体或者不符合要求时，能够通过合理的提示引导用户提供更具体或者正确的信息，同时也要注意在适当的时候转接人工服务以保证用户的需求能够得到满足
- 同时该对话树的很多节点都有 “执行前” 或 “执行后” 属性函数可以设置断点，方便调试
- 最后，可以在服务器的项目目录下，执行 “python ./ichatdef/firstapp/py_chattree/120.py” 生成 “120.html”，下载到本地用浏览器打开，即可看到整个对话树的拓扑结构及相关代码信息
'''

# -------------------------------------------------------------------------------------
# 每个 python 对话树文件的标准代码头部
# -------------------------------------------------------------------------------------

import sys, os

project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)
from chattree_def import *

chattree = ChatTree()

# -------------------------------------------------------------------------------------
# 对话树节点的定义部分
# -------------------------------------------------------------------------------------

import re

# “#开始#” 节点及其相关函数
def start_node_after_execution(ctx): # 这个函数会在 “#开始#” 节点执行后被调用，你可以在这里添加一些调试输出或者其他逻辑
    print("DEBUG OUTPUT : start_node 执行后") 
    pass
start_node = chattree.create_node( "#开始#", {
    "对话树标题":"120急救电话服务",     # 一段简短的文本，描述这个对话树的主题或者用途
    "系统角色":"120急救中心的坐席客服",
    "用户角色":"来电人员",
    "背景信息":
        "你需要用专业知识来回答用户的问题，并快速获取用户相关信息\n"
        "你具有耐心和爱心，能够理解并安抚用户\n"
        "你具备基础的急救知识，经验丰富、非常专业\n"
        "语言尽量简短准确\n"
        "联系电话号码可能是来电号码、也可能不是",
    "是否允许转接人工":True,
    "启动信息项":"{_电话号码_}",
    "静态参考信息":"急救知识", # 指向知识库文件名（不带扩展名）
    "应对话术":[              # 当用户的输入匹配到对应的意图时，系统会根据这里定义的话术进行反馈，注意这里的意图和话术只是示例，你可以根据实际情况进行调整和补充
        { "意图":"期望结束对话", "话术":"不要着急，我们会尽快赶到您那里" },
        { "意图":"期望转接人工", "话术":"<礼貌地说自己就是人工，不需要再转接人工了>" },
        { "意图":"要求稍等一下", "话术":"不着急" },
        { "意图":"表示感谢", "话术":"您别客气，都是我们该做的。" },
        { "意图":"期望了解急救方法", "话术":"<根据医学常识和急救常识给出建议，给出简短有效的回复，问题过于复杂时，要求用户等待医生到现场处理，注意用温和的方式表达>" },
    ],
    "执行前" : lambda ctx : ( # 这个 lambda 函数会在 “#开始#” 节点执行前被调用，你可以在这里添加一些调试输出或者其他逻辑
        print("DEBUG OUTPUT : start_node 执行前"),
        _:=0
    ),
    "执行前" : start_node_after_execution,
})

# 询问需要什么帮助，及相关函数
def welcome_node_before_execution(ctx): # 同上，下面不再解释
    print("DEBUG OUTPUT : welcome_node 执行前")
    pass
welcome_node = chattree.create_node( "#单次交互#", {
    "信息项":"{需要帮助的事情}",
    "信息项修饰":["固定","必需"],
    "系统问题": "您好，这里是120急救中心，有什么需要帮助的？",
    "执行前" : welcome_node_before_execution,
    "执行后" : lambda ctx : ( # 同上，下面不再解释
        print("DEBUG OUTPUT : welcome_node 执行后"),
        _:=0
    ),
})

# 判断是否在 120 的处理范围内，注意这里是 “描述” 型 “#条件#” 节点，系统会调用大模型来进行判断，你需要在 “描述” 字段中尽量清晰具体地描述这个条件的判断标准
def judge_if_in_120_scope_node_before_execution(ctx):
    print("DEBUG OUTPUT : judge_if_in_120_scope_node 执行前")
    pass
def judge_if_in_120_scope_node_after_execution(ctx):
    print("DEBUG OUTPUT : judge_if_in_120_scope_node 执行后")
    pass
judge_if_in_120_scope_node = chattree.create_node( "#条件#描述", {
    "描述":"[{需要帮助的事情}]不是120急救电话的处理范围",
    "执行前": judge_if_in_120_scope_node_before_execution,
    "执行后": judge_if_in_120_scope_node_after_execution,
})

# 如果不在 120 的处理范围，提示用户 ----- 拓扑连接关系见最后的基于 “>>” 的代码，下同
inform_user_out_of_scope_of_120_node = chattree.create_node( "#提示用户#", {
    "提示内容":"<向用户解释这里是120急救电话，并推荐其它可以拨打的电话号码>"
})

# 上面提示完后，再重新提问需要什么帮助
go_back_to_welcome_node = chattree.create_node( "#动作#重新提问", {
    "信息项":"{需要帮助的事情}",
    "执行前" : lambda ctx : (
        print("DEBUG OUTPUT : go_back_to_welcome_node 执行前"),
        _:=0
    ),
    "执行后" : lambda ctx : (
        print("DEBUG OUTPUT : go_back_to_welcome_node 执行后"),
        _:=0
    ),
})

# 如果在 120 的处理范围内，继续询问具体的伤情或病情或身体状况
ask_illness_node = chattree.create_node( "#单次交互#", {
    "信息项":"{具体的伤情或病情或身体状况}",
    "信息项约束":"无症状的身体状况描述也算",
    "信息项修饰":["增量","必需"], # 注意这里的信息项修饰，有一个 “增量”，因为患者可能不断补充 {具体的伤情或病情或身体状况} ----- 下同
    "系统问题": "<根据上下文询问伤情或病情或身体状况的具体情况>", # 这里的问题文本被大于小于号括起来，表示需要根据上下文生成，而不是固定文本
})

# 判断患者提供的伤情或病情或身体状况描述是否足够具体，注意这里也是 “描述” 型 “#条件#” 节点
judge_if_illness_description_specific_enough_node = chattree.create_node( "#条件#描述", {
    "描述":"‘{具体的伤情或病情或身体状况}’ 没有清楚地描述患者的意识状态、症状持续时间、创伤（或病痛）的部位和程度等内容"
})

# 如果患者提供的伤情或病情或身体状况描述不够具体，提示用户提供更具体的描述
inform_user_provide_more_specific_illness_desciption_node = chattree.create_node( "#提示用户#", {
    "提示内容":"<从意识状态、症状持续时间、创伤（或病痛）的部位和程度等方面，根据上下文使用合适的理由（不要太多），请用户提供更具体的伤情或病情或身体状况>"
})

# 上面提示完后，再重新提问 {具体的伤情或病情或身体状况}
go_back_to_ask_illness_node = chattree.create_node( "#动作#重新提问", {
    "信息项":"{具体的伤情或病情或身体状况}"
})

# 如果患者提供的伤情或病情或身体状况描述已经够具体，则继续询问具体地点
ask_location_node = chattree.create_node( "#单次交互#", {
    "信息项":"{来电者目前所在的具体地点}",
    "信息项修饰":["增量","必需"], # 这里也有 “增量”
    "系统问题": "请问您现在具体在什么地方？",
})

# 判断患者提供的地点描述是否足够具体，注意这里也是 “描述” 型 “#条件#” 节点
judge_if_location_description_specific_enough_node = chattree.create_node( "#条件#描述", {
    "描述":"作为120救护车的目的地，‘{来电者目前所在的具体地点}’ 不够具体（门牌号或具体参照物中有一个就算够具体）"
})

# 如果患者提供的地点描述不够具体，且已经问了很多次了（大于等于5），就提示用户并转接人工服务（见下面）
judge_if_location_description_not_specific_enough_too_many_times_node = chattree.create_node( "#条件#脚本", {
    "函数": lambda ctx : ctx['{_当前节点正在执行的次数_}'].as_num() >= 5
})

# 即上面已询问多次后的提示
inform_user_when_ask_location_too_many_times_node = chattree.create_node( "#提示用户#", {
    "提示内容":"<表示用户提供的地点还是不够具体，将为其转接人工服务>", # 这里也被大于小于号括起来了，表示需要根据上下文生成，而不是固定文本
})

# 即上面已询问多次后的转接人工服务
transfer_human_agent_when_ask_location_too_many_times_node = chattree.create_node( "#动作#转接人工", {})

# 如果患者提供的地点描述不够具体，且还未到达询问次数上限，则提示用户提供更具体的地点描述
inform_user_provide_more_specific_location_desciption_node = chattree.create_node( "#提示用户#", {
    "提示内容":"<从门牌号或参照物等方面，根据上下文使用合适的理由，请用户提供详细具体的地点>"
})

# 上面提示完后，再重新提问 {来电者目前所在的具体地点}
go_back_to_ask_loction_node = chattree.create_node( "#动作#重新提问", {
    "信息项":"{来电者目前所在的具体地点}"
})

# 患者提供的地点描述已经够具体后，继续询问是否可以联系来电号码（因为有可能来电号码不是联系电话号码）
ask_if_is_the_calling_number_node = chattree.create_node( "#单次交互#", {
    "信息项":"{是否可以联系来电号码}",
    "信息项修饰":["必需"],
    "系统问题": "您的来电号码是{_电话号码_}，联系这个号码就可以吗？",
})

# 意图分支：联系来电号码 / 及相关函数
def is_calling_number_node_before_execution(ctx):
    print("DEBUG OUTPUT : is_calling_number_node 执行前")
    pass
is_calling_number_node = chattree.create_node( "#用户意图#", {
    "意图":"联系来电号码",
    "执行前": is_calling_number_node_before_execution,
    "执行后" : lambda ctx : (
        print("DEBUG OUTPUT : is_calling_number_node 执行后"),
        _:=0
    ),
})

# 意图分支：不联系来电号码
not_calling_number_node = chattree.create_node( "#用户意图#", {
    "意图":"不联系来电号码",
})

# 在 “联系来电号码” 意图分支之后，将对话树启动时传入的信息项 {_电话号码_} 的值赋给 {联系电话号码}，后者是我们在后续对话中使用的标准信息项名称
def assign_contact_phone_number_node_function(ctx):
    ctx['{联系电话号码}'] = ctx['{_电话号码_}'].as_str()
assign_contact_phone_number_node = chattree.create_node( "#动作#执行脚本", {
    "函数": assign_contact_phone_number_node_function,
    "执行前" : lambda ctx : (
        print("DEBUG OUTPUT : assign_contact_phone_number_node 执行前"),
        _:=0
    ),
    "执行后" : lambda ctx : (
        print("DEBUG OUTPUT : assign_contact_phone_number_node 执行后"),
        _:=0
    ),
})

# 在 “不联系来电号码” 意图分支之后，询问 {联系电话号码}
ask_contact_phone_number_node = chattree.create_node( "#单次交互#", {
    "信息项":"{联系电话号码}",
    "信息项修饰":["明确","复述","必需"],
    "系统问题": "请提供下联系电话号码",
})

# 对患者提供的联系电话号码进行格式判断，注意这里是 “脚本” 型 “#条件#” 节点，需要你用代码来实现判断逻辑
def judge_phone_number_format_node_before_execution(ctx):
    print("DEBUG OUTPUT : judge_phone_number_format_node 执行前")
    pass
def judge_phone_number_format_node_after_execution(ctx):
    print("DEBUG OUTPUT : judge_phone_number_format_node 执行后")
    pass
judge_phone_number_format_node = chattree.create_node( "#条件#脚本", {
    "函数": lambda ctx : not re.search(r'(^|[^0-9])((1[0-9]{10})|([23456789][0-9]{6,7})|(0[0-9]{10,11}))([^0-9]|$)',ctx['{联系电话号码}'].as_str().replace(' ','')),
    "执行前": judge_phone_number_format_node_before_execution,
    "执行后": judge_phone_number_format_node_after_execution,
})

# 如果患者提供的联系电话号码格式不正确，提示用户
inform_user_invalid_phone_number_node = chattree.create_node( "#提示用户#", {
    "提示内容":"您提供的电话号码（{联系电话号码}）好像不太正确",
})

# 上面提示完后，再重新提问 {联系电话号码}
go_back_to_contact_phone_number_node = chattree.create_node( "#动作#重新提问", {
    "信息项":"{联系电话号码}"
})

# 处理完 {联系电话号码} 之后，接下来提示之前患者所提供信息的总结
def summarize_info_node_after_execution(ctx):
    print("DEBUG OUTPUT : summarize_info_node 执行后")
    pass
summarize_info_node = chattree.create_node( "#提示用户#", {
    "提示内容":"<根据前面的沟通总结相关的伤情或者病情、具体的地点以及联系电话>",
    "执行前" : lambda ctx : (
        print("DEBUG OUTPUT : summarize_info_node 执行前"),
        _:=0
    ),
    "执行后": summarize_info_node_after_execution,
})

# 在提示完总结信息之后，询问用户是否确认这些信息都是正确的，注意这里又是一个 “#单次交互#” 节点，因为我们需要在这个节点下面继续细化用户的意图分支
confirm_info_node = chattree.create_node( "#单次交互#", {
    "信息项":"{是否确认信息全部正确}",
    "信息项修饰":["隐含","固定","必需"],
    "系统问题": "请确认下信息是否都正确？",
})

# 意图分支：需要补充或修正信息
append_or_change_info_node = chattree.create_node( "#用户意图#", {
    "意图":"需要补充或修正信息"
})

# 意图分支：信息都正确
confirm_correct_node = chattree.create_node( "#用户意图#", {
    "意图":"信息都正确"
})

# 在 “需要补充或修正信息” 意图分支后，再次总结相关信息并提示用户
# 注意：患者在这里补充或修正相关信息后，前面的相关 “#单次交互#” 节点会自动进行处理（包括判断内容是否具体），然后再到这里再次进行总结
summarize_info_again_node = chattree.create_node( "#提示用户#", {
    "提示内容": "<根据前面的沟通总结用户的伤情或者病情、具体的地点以及联系电话>"
})

# 上面再次提示完总结信息之后，再次询问用户是否确认这些信息都是正确的，这样就形成了一个循环，直到用户确认信息都正确了才会跳出这个循环
go_back_to_confirm_node = chattree.create_node( "#动作#重新提问", {
    "信息项":"{是否确认信息全部正确}"
})

# 在用户确认信息都正确后，调用 HTTP 接口将相关信息传给后端系统，注意这里是一个 “#动作#调用HTTP” 节点，因为它会对系统状态产生影响（调用接口并根据结果进行不同的提示或者转接），你需要在这里实现具体的调用逻辑
def call_http_node_before_execution(ctx):
    print("DEBUG OUTPUT : call_http_node 执行前")
    pass
call_http_node = chattree.create_node( "#动作#调用HTTP", {
    "链接":"http://127.0.0.1:8000/api/intentchat_call_http_test?action=派遣救护车&phone_number={联系电话号码}&address={来电者目前所在的具体地点}&situation={需要帮助的事情}，{具体的伤情或病情或身体状况}",
    "执行前": call_http_node_before_execution,
    "执行后" : lambda ctx : (
        print("DEBUG OUTPUT : call_http_node 执行后"),
        _:=0
    ),
})

# 判断调用 HTTP 接口的结果，如果接口调用失败或者返回的结果表示失败，则提示用户并转接人工服务，注意这里又是一个 “脚本” 型 “#条件#” 节点，需要你用代码来实现判断逻辑
check_http_result_node = chattree.create_node( "#条件#脚本", {
    "函数": lambda ctx : ctx['{http结果1}'].state() != 1 or ctx['{http结果1}'].as_str().startswith('error')
})

# 如果 HTTP 接口调用失败或者返回的结果表示失败，先提示用户，然后再转接人工服务
inform_user_when_http_result_error_node = chattree.create_node( "#提示用户#", {
    "提示内容":"抱歉，系统出了些问题，正在转接人工服务"
})

# 上面提示完后，转接人工服务
transfer_human_agent_when_http_result_error_node = chattree.create_node( "#动作#转接人工", {})

# 如果 HTTP 接口调用成功且返回的结果表示成功，则提示用户相关信息已经确认，救护车正在赶来，并让用户保持手机畅通
last_inform_node = chattree.create_node( "#提示用户#", {
    "提示内容":"不要着急，我们会尽快赶到您那里，请您保持手机畅通"
})

# -------------------------------------------------------------------------------------
# 完整的拓扑结构，“>>” 表示节点之间的连接关系，这里的连接关系也决定了对话的流程走向
# -------------------------------------------------------------------------------------

start_node >> [
    welcome_node >> judge_if_in_120_scope_node >> inform_user_out_of_scope_of_120_node >> go_back_to_welcome_node,
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
# 每个 python 对话树文件的标准代码结尾部分，即渲染对话树成为 HTML 文件的代码
# -------------------------------------------------------------------------------------

if __name__ == "__main__":
    chattree.render(__file__)