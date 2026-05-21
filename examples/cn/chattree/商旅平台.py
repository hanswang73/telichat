'''
- 该对话树模拟进行商旅平台进行机票、酒店、火车的预订、改签和退订等服务
- 其中主要具体实现了最复杂的机票预订业务，通过子对话树 “商旅平台_机票预订.py” 实现，本文件中主要基于具有 “主题” 信息项修饰的节点 first_question_node 完成用户具体业务的划分和分别处理
- 其余的业务都只进行了简单的示意处理
- 同时在整个过程中，系统可以根据用户的输入，随时提供 “商旅平台产品预订及退改签规则说明书” 知识库的相关知识、以及 “#开始#” 节点中定义的 “动态参考信息” 的知识，并根据 “#开始#” 节点中的 “应对话术” 进行反馈，而不会打断对话流程的逻辑
- 最后，可以在服务器的项目目录下，执行 “python ./ichatdef/firstapp/py_chattree/商旅平台.py” 生成 “商旅平台.html”，下载到本地用浏览器打开，即可看到整个对话树的拓扑结构及相关代码信息
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

# 开始节点
def get_points(ctx):
    return "用户目前一共有 1500 积分"
start_node = chattree.create_node( "#开始#", {
    "对话树标题":"商旅平台服务",  # 一段简短的文本，描述这个对话树的主题或者用途
    "系统角色":"商旅平台客服人员",
    "用户角色":"商旅平台客户",
    "背景信息":
        "商旅平台是为客户提供酒店、机票、火车票预订服务的电商平台。你作为商旅平台客服人员，需要高效解决用户的差旅预订、变更、政策咨询及行程管理问题，在确保符合企业差旅政策的前提下，提升用户体验，减少人工客服介入；"
        "同时需要：专业干练（回答简洁明了、不拖泥带水、体现商务属性），礼貌热情（使用敬语、保持耐心、展现服务意识），客观准确（涉及价格、退改规则时必须严谨，不提供模棱两可的信息），同理心（当用户遇到航班延误、取消等焦急情况时，先安抚情绪，再提供解决方案）",
    "是否允许转接人工":True,
    "启动信息项":"{用户ID}",
    "静态参考信息":"商旅平台产品预订及退改签规则说明书", # 指向知识库文件名（不带扩展名）
    "动态参考信息":[                                  # 相对静态参考信息（知识库），动态参考信息是用户输入匹配相关意图时，动态调用相应的函数而生成的文本信息
        { "意图":"想了解目前自己的积分有多少", "函数":get_points},
        { "意图":"想了解目前自己的会员里程有多少", "函数":lambda ctx: (
            "用户目前的会员里程是 32000 公里"
            if ctx["{用户想办理的业务}"].as_str() in ["预订机票", "改签机票", "退订机票"] else
            "用户目前的会员里程是 32000 公里（只有机票业务才涉及会员里程）"
        )},
    ],
    "应对话术":[                                      # 当用户的输入匹配到对应的意图时，系统会根据这里定义的话术进行反馈，注意这里的意图和话术只是示例，你可以根据实际情况进行调整和补充
        { "意图":"询问自己的用户ID", "话术":"<告诉用户，他的用户ID是{用户ID}>" }, # 注意这里的 “话术” 两端用大于小于号括了起来，表示这是一个 “提示词”，同事系统会动态地将 “{用户ID}” 替换成 ctx 中对应的值
        { "意图":"抱怨或质疑相关改签或退订的费用太高", "话术":"非常理解您的心情，看到扣这么多钱确实让人很难接受。不过我需要向您解释一下，本平台作为预订服务方，所有的退改签收费标准都是严格同步航空公司/铁路局/酒店的底层系统的，我们平台不会额外加收任何退票或改签费的。"},
        { "意图":"质疑小孩半价机票价格跟大人全价机票价格差别不大、甚至小孩半价价格还高一些", "话术":"<根据情况向用户解释：确实有时候会出现儿童票价格和成人票价格差别不大的情况，主要是因为各航空公司定价策略不同，儿童票虽然是按全价的一半收取，但在淡季时成人票的折扣力度较大，所以有时候儿童票的价格反而会比成人票高一些。这种情况在行业内是比较常见的>"},
        { "意图":"要求几张机票的机舱座位都挨在一起", "话术":"您可以在手机 App 上几人一起值机并选中相邻的座位，系统会尽量安排在一起，但最终的座位安排还是以航空公司系统的实际情况为准。可尽快出票并支付，然后尽早值机"},
    ],
})

# 做为主题的 “#单次交互#” 节点
first_question_node = chattree.create_node( "#单次交互#", {
    "信息项": "{用户想办理的业务}",
    "信息项修饰": ["主题","必需"], # 注意这里有个 “主题” 修饰
    "系统问题": "请问您需要办理什么业务？",
    "问题修饰": ["绝不反复提问"],
})

# 意图分支：预订机票
book_flight_ticket_intent_node = chattree.create_node( "#用户意图#", {
    "意图":"预订机票",
    "重入意图":"重新另外预订机票",
    "重入意图约束":"更改起点、终点、航空公司的情况不算",
})

# 调用预订机票的子对话树
call_book_flight_ticket_sub_tree_node = chattree.create_node( "#动作#调用子树", {
    "子树":"商旅平台_预订机票.py",
})

# 意图分支：改签机票
change_flight_ticket_intent_node = chattree.create_node( "#用户意图#", {
    "意图":"改签机票",
    "重入意图":"重新另外改签机票"
})

# 询问改签机票的具体需求（示意）
get_change_flight_ticket_requirement_node = chattree.create_node( "#单次交互#", {
    "信息项": "{改签机票的具体需求}",
    "信息项修饰": ["必需"],
    "系统问题": "请问您改签机票的具体需求是什么？",
})

# 提示已收到改签机票的需求（示意）
inform_user_after_get_change_flight_ticket_requirement_node = chattree.create_node( "#提示用户#", {
    "提示内容": "已收到您的改签机票需求",
})

# 意图分支：退订机票
cancel_flight_ticket_intent_node = chattree.create_node( "#用户意图#", {
    "意图":"退订机票",
    "意图约束":"预订机票过程中取消预订的情况不算", # 注意这个约束
    "重入意图":"重新另外退订机票"
})

# 询问退订机票的具体需求（示意）
get_cancel_flight_ticket_requirement_node = chattree.create_node( "#单次交互#", {
    "信息项": "{退订机票的具体需求}",
    "信息项修饰": ["必需"],
    "系统问题": "请问您退订机票的具体需求是什么？",
})

# 提示已收到退订机票的需求（示意）
inform_user_after_get_cancel_flight_ticket_requirement_node = chattree.create_node( "#提示用户#", {
    "提示内容": "已收到您的退订机票需求",
})

# 意图分支：预订火车票
book_train_ticket_intent_node = chattree.create_node( "#用户意图#", {
    "意图":"预订火车票",
    "重入意图":"重新另外预订火车票"
})

# 询问预订火车票的具体需求（示意）
get_book_train_ticket_requirement_node = chattree.create_node( "#单次交互#", {
    "信息项": "{预订火车票的具体需求}",
    "信息项修饰": ["必需"],
    "系统问题": "请问您预订火车票的具体需求是什么？",
})

# 提示已收到预订火车票的需求（示意）
inform_user_after_get_book_train_ticket_requirement_node = chattree.create_node( "#提示用户#", {
    "提示内容": "已收到您的预订火车票需求",
})

# 意图分支：改签火车票
change_train_ticket_intent_node = chattree.create_node( "#用户意图#", {
    "意图":"改签火车票",
    "重入意图":"重新另外改签火车票"
})

# 询问改签火车票的具体需求（示意）
get_change_train_ticket_requirement_node = chattree.create_node( "#单次交互#", {
    "信息项": "{改签火车票的具体需求}",
    "信息项修饰": ["必需"],
    "系统问题": "请问您改签火车票的具体需求是什么？",
})

# 提示已收到改签火车票的需求（示意）
inform_user_after_change_train_ticket_requirement_node = chattree.create_node( "#提示用户#", {
    "提示内容": "已收到您的改签火车票需求",
})

# 意图分支：退订火车票
cancel_train_ticket_intent_node = chattree.create_node( "#用户意图#", {
    "意图":"退订火车票",
    "重入意图":"重新另外退订火车票"
})

# 询问退订火车票的具体需求（示意）
get_cancel_train_ticket_requirement_node = chattree.create_node( "#单次交互#", {
    "信息项": "{退订火车票的具体需求}",
    "信息项修饰": ["必需"],
    "系统问题": "请问您退订火车票的具体需求是什么？",
})

# 提示已收到退订火车票的需求（示意）
inform_user_after_cancel_train_ticket_requirement_node = chattree.create_node( "#提示用户#", {
    "提示内容": "已收到您的改签火车票需求",
})

# 意图分支：预订酒店
book_hotel_intent_node = chattree.create_node( "#用户意图#", {
    "意图":"预订酒店",
    "重入意图":"重新另外预订酒店"
})

# 询问预订酒店的具体需求（示意）
get_book_hotel_requirement_node = chattree.create_node( "#单次交互#", {
    "信息项": "{预订酒店的具体需求}",
    "信息项修饰": ["必需"],
    "系统问题": "请问您预订酒店的具体需求是什么？",
})

# 提示已收到预订酒店的需求（示意）
inform_user_after_book_hotel_requirement_node = chattree.create_node( "#提示用户#", {
    "提示内容": "已收到您的预订酒店需求",
})

# 意图分支：修改酒店预订
change_hotel_intent_node = chattree.create_node( "#用户意图#", {
    "意图":"修改酒店预订",
    "重入意图":"重新另外修改酒店预订"
})

# 询问修改酒店预订的具体需求（示意）
get_change_hotel_requirement_node = chattree.create_node( "#单次交互#", {
    "信息项": "{修改酒店预订的具体需求}",
    "信息项修饰": ["必需"],
    "系统问题": "请问您修改酒店预订的具体需求是什么？",
})

# 提示已收到修改酒店预订的需求（示意）
inform_user_after_change_hotel_requirement_node = chattree.create_node( "#提示用户#", {
    "提示内容": "已收到您的修改酒店预订需求",
})

# 意图分支：退订酒店
cancel_hotel_intent_node = chattree.create_node( "#用户意图#", {
    "意图":"退订酒店",
    "重入意图":"重新另外退订酒店"
})

# 询问退订酒店的具体需求（示意）
get_cancel_hotel_requirement_node = chattree.create_node( "#单次交互#", {
    "信息项": "{退订酒店的具体需求}",
    "信息项修饰": ["必需"],
    "系统问题": "请问您退订酒店的具体需求是什么？",
})

# 提示已收到退订酒店的需求（示意）
inform_user_after_cancel_hotel_requirement_node = chattree.create_node( "#提示用户#", {
    "提示内容": "已收到您的退订酒店需求",
})

# -------------------------------------------------------------------------------------
# 完整的拓扑结构，“>>” 表示节点之间的连接关系，这里的连接关系也决定了对话的流程走向
# -------------------------------------------------------------------------------------

start_node >> first_question_node >> [
    book_flight_ticket_intent_node   >> call_book_flight_ticket_sub_tree_node,
    change_flight_ticket_intent_node >> get_change_flight_ticket_requirement_node >> inform_user_after_get_change_flight_ticket_requirement_node,
    cancel_flight_ticket_intent_node >> get_cancel_flight_ticket_requirement_node >> inform_user_after_get_cancel_flight_ticket_requirement_node,
    book_train_ticket_intent_node    >> get_book_train_ticket_requirement_node >> inform_user_after_get_book_train_ticket_requirement_node,
    change_train_ticket_intent_node  >> get_change_train_ticket_requirement_node >> inform_user_after_change_train_ticket_requirement_node,
    cancel_train_ticket_intent_node  >> get_cancel_train_ticket_requirement_node >> inform_user_after_cancel_train_ticket_requirement_node,
    book_hotel_intent_node   >> get_book_hotel_requirement_node >> inform_user_after_book_hotel_requirement_node,
    change_hotel_intent_node >> get_change_hotel_requirement_node >> inform_user_after_change_hotel_requirement_node,
    cancel_hotel_intent_node >> get_cancel_hotel_requirement_node >> inform_user_after_cancel_hotel_requirement_node,
]

# -------------------------------------------------------------------------------------
# 每个 python 对话树文件的标准代码结尾部分，即渲染对话树成为 HTML 文件的代码
# -------------------------------------------------------------------------------------

if __name__ == "__main__":
    chattree.render(__file__)