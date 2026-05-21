'''
- 该对话树是 “商旅平台.py” 对话树的子树，负责具体实现 “预订机票” 业务
- 可以在服务器的项目目录下，执行 “python ./ichatdef/firstapp/py_chattree/商旅平台_预订机票.py” 生成 “商旅平台_预订机票.html”，下载到本地用浏览器打开，即可看到整个对话树的拓扑结构及相关代码信息
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
# 数据定义和辅助函数
# -------------------------------------------------------------------------------------

import re, datetime, random

'''
必需条件字段
    航班日期
    航班起飞城市
    航班降落城市
可选条件字段
    航班起飞机场     --- “不限起飞机场” 表示不限或均可的意思
    航班降落机场     --- “不限降落机场” 表示不限或均可的意思
    航空公司         --- “不限航空公司” 表示不限或均可的意思
    航班直飞还是转机  --- “不限直飞还是转机” 表示不限或均可的意思，有个意图分支是 “不限直飞还是转机”
    航班起飞时段     --- “不限起飞时段” 表示不限或均可的意思，有个意图分支是 “不限起飞时段”
特殊字段（既是条件也是目标）
    航班舱位等级 --- 作为条件，无值时表示不限或均可的意思；作为目标，是必需字段
目标字段
    航班号
(其它)结果字段
    航班起飞时间
    航班降落时间
    价格
辅助字段
    乘机人数
    乘机人信息
'''

_airline_dict = { # ["代码", 价格系数]
    "国际航空": ["CA", 1.12],
    "东方航空": ["MU", 1.05],
    "南方航空": ["CZ", 1.03],
    "海南航空": ["HU", 1.00],
    "厦门航空": ["MF", 1.05],  # 连续多年服务口碑第一
    "深圳航空": ["ZH", 1.02],
    "四川航空": ["3U", 1.02],  # 以餐食好著称
    "山东航空": ["SC", 0.98],
    "上海航空": ["FM", 1.02],  # 东航旗下，主要经营上海核心航线
    "西藏航空": ["TV", 1.10],  # 高原航线运营成本高，票价通常较贵
    "天津航空": ["GS", 0.95],
    "吉祥航空": ["HO", 1.00],  # 准全服务定位（HOK），服务较好
    "河北航空": ["NS", 0.96],
    "昆明航空": ["KY", 0.95],
    "青岛航空": ["QW", 0.94],
    "成都航空": ["EU", 0.94],
    "长龙航空": ["GJ", 0.96],  # 杭州大本营
    "华夏航空": ["G5", 1.05],  # 支线垄断航线较多，单价往往偏高
    "北部湾航空": ["GX", 0.92],
    "春秋航空": ["9C", 0.82],  # 国内LCC标杆，价格优势最明显
    "中国联合航空": ["KN", 0.85], # 北京大兴基地，常有低价
    "西部航空": ["PN", 0.84],
    "祥鹏航空": ["8L", 0.86],
    "九元航空": ["AQ", 0.83],  # 广州基地的廉航
    "乌鲁木齐航空": ["UQ", 0.88],
    "长安航空": ["9H", 0.87],
    "桂林航空": ["GT", 0.89],
    "福州航空": ["FU", 0.90],
    "江西航空": ["RY", 0.88],
    "幸福航空": ["JR", 0.85],  # 多为国产新舟机型支线
    "大新华航空": ["CN", 1.00], # 海航系
    "东海航空": ["DZ", 0.92],
    "红土航空": ["A6", 0.91],  # 现更名为湖南航空
    "多彩贵州航空": ["GY", 0.93],
    "天骄航空": ["9W", 1.00],  # 内蒙古支线
    "一二三航空": ["MU", 1.00], # 东航旗下国产机型运营（通常共用MU代码）
}
_city_airport_dict = {
    "北京": ["首都", "大兴"],
    "上海": ["浦东", "虹桥"],
    "成都": ["双流", "天府"],
    "广州": ["白云"],
    "深圳": ["宝安"],
    "天津": ["滨海"],
    "重庆": ["江北", "仙女山", "巫山", "武陵山"],
    "杭州": ["萧山"],
    "南京": ["禄口"],
    "武汉": ["天河"],
    "西安": ["咸阳"],
    "郑州": ["新郑"],
    "长沙": ["黄花"],
    "青岛": ["胶东"],
    "沈阳": ["桃仙"],
    "大连": ["周水子"],
    "哈尔滨": ["太平"],
    "长春": ["龙嘉"],
    "济南": ["遥墙"],
    "福州": ["长乐"],
    "厦门": ["高崎"],
    "昆明": ["长水"],
    "南宁": ["吴圩"],
    "贵阳": ["龙洞堡"],
    "太原": ["武宿"],
    "石家庄": ["正定"],
    "合肥": ["新桥"],
    "南昌": ["昌北"],
    "海口": ["美兰"],
    "三亚": ["凤凰"],
    "乌鲁木齐":["地窝堡"],
    "兰州": ["中川"],
    "银川": ["河东"],
    "西宁": ["曹家堡"],
    "呼和浩特": ["白塔"],
    "拉萨": ["贡嘎"],
    "宁波": ["栎社"],
    "温州": ["龙湾"],
    "无锡": ["硕放"],
    "常州": ["奔牛"],
    "徐州": ["观音"],
    "南通": ["兴东"],
    "盐城": ["南洋"],
    "连云港": ["花果山"],
    "泉州": ["晋江"],
    "三明": ["沙县"],
    "珠海": ["金湾"],
    "揭阳": ["潮汕"],
    "湛江": ["吴川"],
    "惠州": ["平潭"],
    "佛山": ["沙堤"],
    "烟台": ["蓬莱"],
    "威海": ["大水泊"],
    "临沂": ["启阳"],
    "绵阳": ["南郊"],
    "日照": ["山字河"],
    "济宁": ["曲阜"],
    "洛阳": ["北郊"],
    "南阳": ["姜营"],
    "信阳": ["明港"],
    "宜昌": ["三峡"],
    "襄阳": ["刘集"],
    "十堰": ["武当山"],
    "恩施": ["许家坪"],
    "张家界": ["荷花"],
    "常德": ["桃花源"],
    "衡阳": ["南岳"],
    "黄山": ["屯溪"],
    "阜阳": ["西关"],
    "赣州": ["黄金"],
    "九江": ["庐山"],
    "景德镇": ["罗家"],
    "吉安": ["井冈山"],
    "上饶": ["三清山"],
    "宜春": ["明月山"],
    "大同": ["云冈"],
    "运城": ["张孝"],
    "长治": ["王村"],
    "临汾": ["尧都"],
    "延安": ["南泥湾"],
    "榆林": ["榆阳"],
    "汉中": ["城固"],
    "丹东": ["浪头"],
    "牡丹江": ["海浪"],
    "佳木斯": ["东郊"],
    "齐齐哈尔": ["三家子"],
    "延吉": ["朝阳川"],
    "桂林": ["两江"],
    "柳州": ["白莲"],
    "北海": ["福成"],
    "丽江": ["三义"],
    "大理": ["荒草坝"],
    "西双版纳": ["嘎洒"],
    "腾冲": ["驼峰"],
    "遵义": ["新舟", "茅台"],
    "铜仁": ["凤凰"],
    "琼海": ["博鳌"],
    "敦煌": ["莫高"],
    "喀什": ["徕宁"],
    "林芝": ["米林"]
}

# 生成一个模拟的航班数据库
_flight_databse = []
def generate_flight_database():
    global _flight_databse
    _flight_databse = []
    rng = random.Random(20260304) # 固定 20260304 这个数，这样每次运行这个函数生成的航班数据库都是一样的，方便调试和测试
    cabin_factor = {
        "经济舱": 1.00,
        "超级经济舱": 1.20,
        "商务舱": 2.10,
        "头等舱": 3.20,
    }
    cities = list(_city_airport_dict.keys())
    base_date = datetime.date.today()
    direct_flight = True
    for day_offset in range(31):
        flight_date = base_date + datetime.timedelta(days=day_offset)
        flight_date_str = flight_date.strftime("%Y-%m-%d")
        for departure_city in cities[:4]: # 为了执行效率，仅对前4个城市生成航班数据，实际应用中可以去掉这个限制，让所有城市的航班数据都生成
            for landing_city in cities[:4]: # 为了执行效率，仅对前4个城市生成航班数据，实际应用中可以去掉这个限制，让所有城市的航班数据都生成
                if departure_city == landing_city:
                    continue
                for airline in list(_airline_dict.keys())[:4]: # 为了执行效率，仅对前4家航空公司生成航班数据，实际应用中可以去掉这个限制，让所有航空公司的航班数据都生成
                    for i in range(8): # 每个航线每天每个航空公司有 8 班航班，分布在一天中的不同时间段
                        dep_hour = rng.randint(0, 23)
                        dep_minute = rng.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
                        departure_dt = datetime.datetime.combine(
                            flight_date,
                            datetime.time(hour=dep_hour, minute=dep_minute),
                        )
                        prefix = _airline_dict.get(airline, ["XX", 1.00])[0]
                        flight_number = f"{prefix}{rng.randint(1000, 9999)}"
                        is_direct = "直飞" if direct_flight else "转机"
                        direct_flight = not direct_flight
                        duration_hours = rng.randint(2, 5) if is_direct == "直飞" else rng.randint(4, 10)
                        duration_minutes = rng.choice([0, 10, 20, 30, 40, 50])
                        arrival_dt = departure_dt + datetime.timedelta(hours=duration_hours, minutes=duration_minutes)
                        route_base_price = rng.randint(380, 1800)
                        transfer_discount = 0.92 if is_direct == "转机" else 1.00
                        cabin_infos = []
                        for cabin_name, factor in cabin_factor.items():
                            jitter = rng.uniform(0.95, 1.08)
                            price = int(route_base_price * _airline_dict.get(airline, ["XX", 1.00])[1] * factor * transfer_discount * jitter)
                            price = max(200, (price // 10) * 10)
                            if cabin_name == "超级经济舱" and rng.random() < 0.7: # 70% 的航班没有超级经济舱
                                continue
                            if cabin_name == "头等舱" and rng.random() < 0.8: # 80% 的航班没有头等舱
                                continue
                            cabin_infos.append({
                                "航班舱位等级": cabin_name,
                                "价格": price,
                            })
                        _flight_databse.append({
                            "航空公司": airline,
                            "航班号": flight_number,
                            "航班日期": flight_date_str,
                            "航班起飞时间": departure_dt.strftime("%Y-%m-%d %H:%M"),
                            "航班降落时间": arrival_dt.strftime("%Y-%m-%d %H:%M"),
                            "航班起飞城市": departure_city,
                            "航班降落城市": landing_city,
                            "航班起飞机场": rng.choice(_city_airport_dict[departure_city]),
                            "航班降落机场": rng.choice(_city_airport_dict[landing_city]),
                            "航班直飞还是转机": is_direct,
                            "舱位价格信息": cabin_infos,
                        })
generate_flight_database()

def get_time_slot_by_hhmm(hhmm):
    hour = int(hhmm.split(":")[0])
    r = []
    if hour <= 5 or hour >= 22:
        r += ["凌晨"]
    if 4 <= hour <= 9:
        r += ["早晨"]
    if 7 <= hour <= 12:
        r += ["上午"]
    if 11 <= hour <= 14:
        r += ["中午"]
    if 12 <= hour <= 18:
        r += ["下午"]
    if 16 <= hour <= 20:
        r += ["傍晚"]
    if hour >= 19 or hour <= 6:
        r += ["夜间"]
    return r

# -------------------------------------------------------------------------------------
# 对话树节点的定义部分（除了触发类节点）
# -------------------------------------------------------------------------------------

# 开始节点及相关函数
def reset_flight_carbin_class(ctx): # 用户要求取消舱位等级的限定时，进行相关处理
    if ctx["{航班舱位等级}"].state() != -1:
        del ctx["{航班舱位等级}"] 
def reset_flight_departure_airport(ctx): # 当 {航班起飞城市} 变化时，进行相关处理
    if ctx["{航班起飞城市}"].as_str() in _city_airport_dict:
        if ctx["{航班起飞机场}"].as_str() not in _city_airport_dict[ctx["{航班起飞城市}"].as_str()]:
            ctx["{航班起飞机场}"] = "不限起飞机场"
def reset_flight_landing_airport(ctx): # 当 {航班降落城市} 变化时，进行相关处理
    if ctx["{航班降落城市}"].as_str() in _city_airport_dict:
        if ctx["{航班降落机场}"].as_str() not in _city_airport_dict[ctx["{航班降落城市}"].as_str()]:
            ctx["{航班降落机场}"] = "不限降落机场"
def reset_flight_number(ctx): # 当用户要求重新选择航班号，或者{航班日期},{航班起飞城市},{航班降落城市},{航班起飞机场},{航班降落机场},{航空公司},{航班直飞还是转机},{航班起飞时段}等字段变化时，进行相关处理
    if ctx["{航班号}"].state() == 1: # 有值状态
        # 先判断如果 {航班号} 有值且其对应的航班信息和相关的信息项都一致，则不删除 {航班号}，否则再删除
        flight_number = ctx["{航班号}"].as_str()
        matched_flight = None
        for flight in _flight_databse:
            if flight["航班号"] == flight_number:
                matched_flight = flight
                break
        if matched_flight is not None:
            if (matched_flight["航班日期"] == ctx["{航班日期}"].as_str() and
                matched_flight["航班起飞城市"] == ctx["{航班起飞城市}"].as_str() and
                matched_flight["航班降落城市"] == ctx["{航班降落城市}"].as_str() and
                (ctx["{航班起飞机场}"].as_str() == "不限起飞机场" or matched_flight["航班起飞机场"] == ctx["{航班起飞机场}"].as_str()) and
                (ctx["{航班降落机场}"].as_str() == "不限降落机场" or matched_flight["航班降落机场"] == ctx["{航班降落机场}"].as_str()) and
                (ctx["{航空公司}"].as_str() == "不限航空公司" or matched_flight["航空公司"] == ctx["{航空公司}"].as_str()) and
                (ctx["{航班直飞还是转机}"].as_str() == "不限直飞还是转机" or matched_flight["航班直飞还是转机"] == ctx["{航班直飞还是转机}"].as_str()) and
                (ctx["{航班起飞时段}"].as_str() == "不限起飞时段" or ctx["{航班起飞时段}"].as_str() in get_time_slot_by_hhmm(matched_flight["航班起飞时间"].split(" ")[-1]))):
                return # 航班信息一致，不删除 {航班号}
        del ctx["{航班号}"] # 这里的删除表示用户之前提及过了，但现在信息项的值发生了变化，之前提及过的航班号可能就不适用了，所以删除它，让它回到未提及过的状态
        if ctx["{航班舱位等级}"].state() == 1:
            del ctx["{航班舱位等级}"] # 同理，如果航班号被删除了，那么之前提及过的航班舱位等级也可能不适用了，所以也删除它，让它回到未提及过的状态
start_node = chattree.create_node( "#开始#", {
    "信息项变化触发":[
        { "信息项":["{航班起飞城市}"], "函数":reset_flight_departure_airport },
        { "信息项":["{航班降落城市}"], "函数":reset_flight_landing_airport },
        { "信息项":["{航班日期}","{航班起飞城市}","{航班降落城市}","{航班起飞机场}","{航班降落机场}","{航空公司}","{航班直飞还是转机}","{航班起飞时段}"], "函数":reset_flight_number }, # 注意这里没有 {航班舱位等级}
    ],
    "意图触发":[
        {"意图":"要重新选择航班号", "意图约束":"且未指定具体的航班号", "函数":reset_flight_number},
        {"意图":"不再限定航班舱位等级", "函数":reset_flight_carbin_class},
    ]
})

# 询问航班日期
ask_flight_date_node = chattree.create_node( "#单次交互#", {
    "信息项":"{航班日期}",
    "信息项约束":"格式转换为YYYY-MM-DD",
    "信息项修饰":["必需","复述","明确"],
    "系统问题":["请问您需要预订哪一天的机票？","请问您需要预订什么日期的机票？","请问您需要预订几月几号的机票？","<询问用户需要预订的航班日期>"],
    "节点注释":"必须输入{航班日期}", # 显示在生成的 HTML 拓扑图中（下同）
})

# 判断航班日期是否合法，以及相关函数
def check_if_flight_date_invalid(ctx):
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", ctx["{航班日期}"].as_str()):
        ctx["{航班日期错误提示}"] = "航班日期 “" + ctx["{航班日期}"].as_str() + "” 的格式错误"
        return True # True 表示 invalid
    try:
        datetime.date.fromisoformat(ctx["{航班日期}"].as_str())
        curr_date = datetime.datetime.now().strftime("%Y-%m-%d")
        if ctx["{航班日期}"].as_str() < curr_date:
            ctx["{航班日期错误提示}"] = "航班日期 “" + ctx["{航班日期}"].as_str() + "” 不能是已经过去的日期"
            return True
        date1 = datetime.datetime.strptime(curr_date, "%Y-%m-%d")
        date2 = datetime.datetime.strptime(ctx["{航班日期}"].as_str(), "%Y-%m-%d")
        diff_days = (date2 - date1).days
        if diff_days > 30:
            ctx["{航班日期错误提示}"] = "航班日期 “" + ctx["{航班日期}"].as_str() + "” 不能是 30 天以后的日期"
            return True
        return False # 表示 valid
    except ValueError:
        ctx["{航班日期错误提示}"] = "航班日期 “" + ctx["{航班日期}"].as_str() + "” 的格式错误"
        return True
check_if_flight_date_invalid_node = chattree.create_node( "#条件#脚本", {
    "函数":check_if_flight_date_invalid,
    "节点注释":"检查航班日期的格式和有效性，必须是YYYY-MM-DD格式\n且不能是已经过去的日期，也不能是 30 天以后的日期",
})

# 提示用户航班日期错误
inform_user_if_flight_date_invalid_node = chattree.create_node( "#提示用户#", {
    "提示内容":"{航班日期错误提示}",
})

# 上面提示完后，重新提问航班日期
ask_flight_date_again_node = chattree.create_node( "#动作#重新提问", {
    "信息项":"{航班日期}",
})

# 询问航班起飞城市
ask_flight_departure_city_node = chattree.create_node( "#单次交互#", {
    "信息项":"{航班起飞城市}",
    "信息项修饰":["必需","复述","明确"],
    "信息项选项":list(_city_airport_dict.keys()),
    "信息项选项修饰":['开放'],
    "系统问题":"航班从哪个城市出发？",
    "节点注释":"必须输入{航班起飞城市}",
})

# 判断航班起飞城市是否合法，以及相关函数
def check_if_flight_departure_city_invalid(ctx):
    if ctx["{航班起飞城市}"].as_str() not in _city_airport_dict:
        ctx["{航班城市错误提示}"] = "抱歉，我们暂不支持 ‘" + ctx["{航班起飞城市}"].as_str() + "’ 作为航班城市"
        return True # 表示 invalid
    return False # 表示 valid
check_if_flight_departure_city_invalid_node = chattree.create_node( "#条件#脚本", {
    "函数":check_if_flight_departure_city_invalid,
    "节点注释":"检查{航班起飞城市}是否在支持的城市列表中",
})

# 提示用户航班起飞城市错误
inform_user_if_flight_departture_city_invalid_node = chattree.create_node( "#提示用户#", {
    "提示内容":"{航班城市错误提示}",
})

# 上面提示完后，重新提问航班起飞城市
ask_flight_departure_city_again_node = chattree.create_node( "#动作#重新提问", {
    "信息项":"{航班起飞城市}",
})

# 询问航班降落城市
ask_flight_landing_city_node = chattree.create_node( "#单次交互#", {
    "信息项":"{航班降落城市}",
    "信息项同义词":["{飞到哪个城市}"],
    "信息项修饰":["必需","复述","明确"],
    "信息项选项":list(_city_airport_dict.keys()), 
    "信息项选项修饰":['开放'],
    "系统问题":"飞到哪个城市？",
    "节点注释":"必须输入{航班降落城市}",
})

# 判断航班降落城市是否合法，以及相关函数
def check_if_flight_landing_city_invalid(ctx):
    if ctx["{航班降落城市}"].as_str() not in _city_airport_dict:
        ctx["{航班城市错误提示}"] = "抱歉，我们暂不支持 ‘" + ctx["{航班降落城市}"].as_str() + "’ 作为航班城市"
        return True # 表示 invalid
    return False # 表示 valid
check_if_flight_landing_city_invalid_node = chattree.create_node( "#条件#脚本", {
    "函数":check_if_flight_landing_city_invalid,
    "节点注释":"检查{航班降落城市}是否在支持的城市列表中",
})

# 提示用户航班降落城市错误
inform_user_if_flight_landing_city_invalid_node = chattree.create_node( "#提示用户#", {
    "提示内容":"{航班城市错误提示}",
})

# 上面提示完后，重新提问航班降落城市
ask_flight_landing_city_again_node = chattree.create_node( "#动作#重新提问", {
    "信息项":"{航班降落城市}",
})

# 设置用户偏好值（如果有的话）或默认值“不限XXXX”，并设置偏好提示内容（如果有的话）
def set_default_and_prefered_value(ctx):
    preference_tips = ""
    if ctx["{航班起飞机场}"].state() != 1:
        ctx["{航班起飞机场}"] = "不限起飞机场"
    if ctx["{航班降落机场}"].state() != 1:
        ctx["{航班降落机场}"] = "不限降落机场"
    if ctx["{航空公司}"].state() != 1:
        ctx["{航空公司}"] = "国际航空" # 这里假设是基于启动信息项 {用户ID} 获取用户历史订单的习惯后，经过一定的确定性规则判断而设置的默认值
        preference_tips += "国际航空，"
    if ctx["{航班直飞还是转机}"].state() != 1:
        ctx["{航班直飞还是转机}"] = "直飞" # 这里假设是基于启动信息项 {用户ID} 获取用户历史订单的习惯后，经过一定的确定性规则判断而设置的默认值
        preference_tips += "直飞，"
    if ctx["{航班起飞时段}"].state() != 1:
        ctx["{航班起飞时段}"] = "不限起飞时段"
    if preference_tips != "":
        ctx["{机票预订偏好提示}"] = "根据您之前的预订习惯我们默认：“" + preference_tips[:-1] + "”，"
    else:
        ctx["{机票预订偏好提示}"] = ""
    #-------------------------------- 以下不进行偏好提示
    if ctx["{乘机人数}"].state() != 1:
        ctx["{乘机人数}"] = 1
set_default_and_prefered_value_node = chattree.create_node( "#动作#执行脚本", {
    "函数":set_default_and_prefered_value,
    "节点注释":"设置默认值‘不限’或用户偏好值（并设置偏好提示内容）：\n{航班起飞机场}、{航班降落机场}、{航空公司}、{航班直飞还是转机}、{航班起飞时段}\n\n设置默认值：{乘机人数}=1",
})

# 判断是否有偏好提示需要告诉用户的条件节点
judge_if_has_preference_tips_node = chattree.create_node( "#条件#脚本", {
    "函数":lambda ctx: ctx["{机票预订偏好提示}"].as_str() != "",
})

# 如果有需要告诉用户的偏好提示，则告诉用户
show_preference_tips_node = chattree.create_node( "#提示用户#", {
    "提示内容":"{机票预订偏好提示}",
})

# 询问航班起飞机场
ask_flight_departure_airport_node = chattree.create_node( "#单次交互#", {
    "信息项":"{航班起飞机场}",
    "信息项修饰":["复述","明确"],
    "信息项选项" : [airport for airports in _city_airport_dict.values() for airport in airports] + ["不限起飞机场"],
    "信息项选项修饰" : ['开放'],
    "系统问题":"请问您从哪个机场出发？",
    "节点注释":"之前预设了缺省值或偏好值\nAI不会主动提问，但用户可以主动提及",
})

# 判断航班起飞机场是否合法，以及相关函数
def check_if_flight_departure_airport_invalid(ctx):
    if ctx["{航班起飞机场}"].as_str() == "不限起飞机场":
        return False # 表示 valid
    assert ctx["{航班起飞城市}"].as_str() in _city_airport_dict
    if ctx["{航班起飞机场}"].as_str() not in _city_airport_dict[ctx["{航班起飞城市}"].as_str()]:
        ctx["{航班机场错误提示}"] = "抱歉，‘" + ctx["{航班起飞城市}"].as_str() + "’目前仅支持" + str(_city_airport_dict[ctx["{航班起飞城市}"].as_str()])[1:-1] + "机场"
        return True # 表示 invalid
    return False # 表示 valid
check_if_flight_departure_airport_invalid_node = chattree.create_node( "#条件#脚本", {
    "函数":check_if_flight_departure_airport_invalid,
    "节点注释":"检查{航班起飞机场}是否在对应的{航班起飞城市}的机场列表中",
})

# 提示用户航班起飞机场错误
inform_user_if_flight_departure_airport_invalid_node = chattree.create_node( "#提示用户#", {
    "提示内容":"{航班机场错误提示}",
})

# 判断对应的{航班起飞城市}的机场列表中是否只有一个机场，如果只有一个机场了，那就直接把它设置为{航班起飞机场}的值，不需要再让用户选择了
check_if_only_one_airport_for_departure_city_node = chattree.create_node( "#条件#脚本", {
    "函数":lambda ctx: len(_city_airport_dict[ctx["{航班起飞城市}"].as_str()]) == 1,
    "节点注释":"检查对应的{航班起飞城市}的机场列表中是否只有一个机场，如果只有一个机场了，那就直接把它设置为{航班起飞机场}的值，不需要再让用户选择了",
})

# 设置对应的{航班起飞城市}的唯一一个机场为{航班起飞机场}的值
def set_only_one_airport_for_departure_city(ctx):
    ctx["{航班起飞机场}"] = _city_airport_dict[ctx["{航班起飞城市}"].as_str()][0]
set_only_one_airport_for_departure_city_node = chattree.create_node( "#动作#执行脚本", {
    "函数":set_only_one_airport_for_departure_city,
    "节点注释":"把对应的{航班起飞城市}的唯一一个机场设置为{航班起飞机场}的值",
})

# 判断对应的{航班起飞城市}的机场列表中是否不只一个机场，如果不只一个机场了，那就需要让用户选择了
check_if_not_only_one_airport_for_departure_city_node = chattree.create_node( "#条件#脚本", {
    "函数":lambda ctx: len(_city_airport_dict[ctx["{航班起飞城市}"].as_str()]) > 1,
    "节点注释":"检查对应的{航班起飞城市}的机场列表中是否不只一个机场，如果不只一个机场了，那就需要让用户选择了",
})

# 重新提问航班起飞机场
ask_flight_departure_airport_again_node = chattree.create_node( "#动作#重新提问", {
    "信息项":"{航班起飞机场}",
})

# 询问航班降落机场
ask_flight_landing_airport_node = chattree.create_node( "#单次交互#", {
    "信息项":"{航班降落机场}",
    "信息项同义词":["{飞到哪个机场}"],
    "信息项修饰":["复述","明确"],
    "信息项选项" : [airport for airports in _city_airport_dict.values() for airport in airports] + ["不限降落机场"],
    "信息项选项修饰" : ['开放'],
    "系统问题":"请问您到哪个机场降落？",
    "节点注释":"之前预设了缺省值或偏好值\nAI不会主动提问，但用户可以主动提及",
})

# 判断航班降落机场是否合法，以及相关函数
def check_if_flight_landing_airport_invalid(ctx):
    if ctx["{航班降落机场}"].as_str() == "不限降落机场":
        return False # 表示 valid
    assert ctx["{航班降落城市}"].as_str() in _city_airport_dict
    if ctx["{航班降落机场}"].as_str() not in _city_airport_dict[ctx["{航班降落城市}"].as_str()]:
        ctx["{航班机场错误提示}"] = "抱歉，‘" + ctx["{航班降落城市}"].as_str() + "’目前仅支持" + str(_city_airport_dict[ctx["{航班降落城市}"].as_str()])[1:-1] + "机场"
        return True # 表示 invalid
    return False # 表示 valid
check_if_flight_landing_airport_invalid_node = chattree.create_node( "#条件#脚本", {
    "函数":check_if_flight_landing_airport_invalid,
    "节点注释":"检查{航班降落机场}是否在对应的{航班降落城市}的机场列表中",
})

# 提示用户航班降落机场错误
inform_user_if_flight_landing_airport_invalid_node = chattree.create_node( "#提示用户#", {
    "提示内容":"{航班机场错误提示}",
})

# 判断对应的{航班降落城市}的机场列表中是否只有一个机场，如果只有一个机场了，那就直接把它设置为{航班降落机场}的值，不需要再让用户选择了
check_if_only_one_airport_for_landing_city_node = chattree.create_node( "#条件#脚本", {
    "函数":lambda ctx: len(_city_airport_dict[ctx["{航班降落城市}"].as_str()]) == 1,
    "节点注释":"检查对应的{航班降落城市}的机场列表中是否只有一个机场，如果只有一个机场了，那就直接把它设置为{航班降落机场}的值，不需要再让用户选择了",
})

# 设置对应的{航班降落城市}的唯一一个机场为{航班降落机场}的值
def set_only_one_airport_for_landing_city(ctx):
    ctx["{航班降落机场}"] = _city_airport_dict[ctx["{航班降落城市}"].as_str()][0]
set_only_one_airport_for_landing_city_node = chattree.create_node( "#动作#执行脚本", {
    "函数":set_only_one_airport_for_landing_city,
    "节点注释":"把对应的{航班降落城市}的唯一一个机场设置为{航班降落机场}的值",
})

# 判断对应的{航班降落城市}的机场列表中是否不只一个机场，如果不只一个机场了，那就需要让用户选择了
check_if_not_only_one_airport_for_landing_city_node = chattree.create_node( "#条件#脚本", {
    "函数":lambda ctx: len(_city_airport_dict[ctx["{航班降落城市}"].as_str()]) > 1,
    "节点注释":"检查对应的{航班降落城市}的机场列表中是否不只一个机场，如果不只一个机场了，那就需要让用户选择了",
})

# 重新提问航班降落机场
ask_flight_landing_airport_again_node = chattree.create_node( "#动作#重新提问", {
    "信息项":"{航班降落机场}",
})

# 询问航空公司
ask_flight_airline_node = chattree.create_node( "#单次交互#", {
    "信息项":"{航空公司}",
    "信息项修饰":["复述","明确"],
    "信息项选项":list(_airline_dict.keys()) + ["不限航空公司"],
    "信息项选项修饰": ["开放"],
    "系统问题":"选择哪个航空公司的航班？",
    "节点注释":"之前预设了缺省值或偏好值\nAI不会主动提问，但用户可以主动提及",
})

# 判断航空公司是否合法，以及相关函数
def check_if_flight_airlines_invalid(ctx):
    if ctx["{航空公司}"].as_str() == "不限航空公司":
        return False # 表示 valid
    if ctx["{航空公司}"].as_str() not in list(_airline_dict.keys()):
        ctx["{航空公司错误提示}"] = "抱歉，我们暂不支持 ‘" + ctx["{航空公司}"].as_str() + "’ 作为航空公司"
        return True # 表示 invalid
    return False # 表示 valid
check_if_flight_airlines_invalid_node = chattree.create_node( "#条件#脚本", {
    "函数":check_if_flight_airlines_invalid,
    "节点注释":"检查{航空公司}是否在支持的航空公司列表中",
})

# 提示用户航空公司错误
inform_user_if_flight_airlines_invalid_node = chattree.create_node( "#提示用户#", {
    "提示内容":"{航空公司错误提示}",
})

# 上面提示完后，重新提问航空公司
ask_flight_airlines_again_node = chattree.create_node( "#动作#重新提问", {
    "信息项":"{航空公司}",
})

# 询问航班是直飞还是转机
ask_flight_direct_or_connecting_node = chattree.create_node( "#单次交互#", {
    "信息项":"{航班直飞还是转机}",
    "信息项修饰":["复述","明确"],
    "系统问题":"那航班是直飞还是转机？",
    "节点注释":"之前预设了缺省值或偏好值\nAI不会主动提问，但用户可以主动提及",
})

# 意图分支：不限直飞还是转机
flight_direct_or_connecting_intent_node = chattree.create_node( "#用户意图#", {
    "意图":"不限直飞还是转机",
})

# 意图分支：直飞
flight_direct_intent_node = chattree.create_node( "#用户意图#", {
    "意图":"直飞",
})

# 意图分支：转机
flight_connecting_intent_node = chattree.create_node( "#用户意图#", {
    "意图":"转机",
})

# 询问航班起飞时间的时段
ask_flight_departure_time_slot_node = chattree.create_node( "#单次交互#", {
    "信息项":"{航班起飞时段}",
    "信息项修饰":["复述","明确"],
    "系统问题":"请问您希望航班的起飞时间大致在一天中的什么时段？",
    "节点注释":"之前预设了缺省值或偏好值\nAI不会主动提问，但用户可以主动提及",
})

# 意图分支：不限起飞时段
all_time_slot_intent_node = chattree.create_node( "#用户意图#", {
    "意图":"不限起飞时段",
})

# 意图分支：凌晨
early_morning_intent_node = chattree.create_node( "#用户意图#", {
    "意图":"凌晨",
})

# 意图分支：早晨
morning_intent_node = chattree.create_node( "#用户意图#", {
    "意图":"早晨",
})

# 意图分支：上午
late_morning_intent_node = chattree.create_node( "#用户意图#", {
    "意图":"上午",
})

# 意图分支：中午
noon_intent_node = chattree.create_node( "#用户意图#", {
    "意图":"中午",
})

# 意图分支：下午
afternoon_intent_node = chattree.create_node( "#用户意图#", {
    "意图":"下午",
})

# 意图分支：傍晚
evening_intent_node = chattree.create_node( "#用户意图#", {
    "意图":"傍晚",
})

# 意图分支：夜间
night_intent_node = chattree.create_node( "#用户意图#", {
    "意图":"夜间",
})

# 询问航班号，及相关函数（询问之前的准备工作：根据用户提供的条件筛选航班，生成符合条件的航班列表和提示信息等）
def before_ask_flight_number(ctx):
    matched_flights = []
    for flight in _flight_databse:
        if flight["航班日期"] != ctx["{航班日期}"].as_str():
            continue
        if flight["航班起飞城市"] != ctx["{航班起飞城市}"].as_str():
            continue
        if flight["航班降落城市"] != ctx["{航班降落城市}"].as_str():
            continue
        if ctx["{航班起飞机场}"].as_str() != "不限起飞机场" and flight["航班起飞机场"] != ctx["{航班起飞机场}"].as_str():
            continue
        if ctx["{航班降落机场}"].as_str() != "不限降落机场" and flight["航班降落机场"] != ctx["{航班降落机场}"].as_str():
            continue
        if ctx["{航空公司}"].as_str() != "不限航空公司" and flight["航空公司"] != ctx["{航空公司}"].as_str():
            continue
        if ctx["{航班直飞还是转机}"].as_str() != "不限直飞还是转机" and flight["航班直飞还是转机"] != ctx["{航班直飞还是转机}"].as_str():
            continue
        if ctx["{航班起飞时段}"].as_str() != "不限起飞时段":
            dep_hhmm = flight["航班起飞时间"].split(" ")[-1]
            if ctx["{航班起飞时段}"].as_str() not in get_time_slot_by_hhmm(dep_hhmm):
                continue
        matched_flights.append(flight)
    matched_flights.sort(key=lambda item: item["航班起飞时间"])
    # ---------
    structured_rows = []
    flight_number_list = []
    for flight in matched_flights:
        cabin_prices = []
        for cabin_item in flight["舱位价格信息"]:
            if ctx["{航班舱位等级}"].state() != -1 and cabin_item["航班舱位等级"] != ctx["{航班舱位等级}"].as_str():
                continue
            cabin_prices.append({
                "航班舱位等级": cabin_item["航班舱位等级"],
                "价格": cabin_item["价格"],
            })
        if len(cabin_prices) == 0:
            continue
        if flight["航班号"] not in flight_number_list:
            flight_number_list.append(flight["航班号"])
        for item in cabin_prices:
            structured_rows.append({
                "display": (
                    flight["航班号"] + " " + 
                    flight["航空公司"] + " " + 
                    flight["航班起飞时间"].split(" ")[-1] + "-" + 
                    flight["航班降落时间"].split(" ")[-1] + " " + 
                    flight["航班起飞城市"] + flight["航班起飞机场"] + "-" + 
                    flight["航班降落城市"] + flight["航班降落机场"] + " " + 
                    flight["航班直飞还是转机"] + " " + 
                    item["航班舱位等级"] + " " + 
                    str(item["价格"]) + "元"
                ),
                "user_input": flight["航班号"] + "，" + item["航班舱位等级"],
            })
    filter_conditions = [
        f"{ctx['{航班日期}'].as_str()} 从{ctx['{航班起飞城市}'].as_str()}飞{ctx['{航班降落城市}'].as_str()}",
    ]
    if ctx["{航班起飞机场}"].as_str() != "不限起飞机场":
        filter_conditions.append(f"起飞机场是{ctx['{航班起飞机场}'].as_str()}")
    if ctx["{航班降落机场}"].as_str() != "不限降落机场":
        filter_conditions.append(f"降落机场是{ctx['{航班降落机场}'].as_str()}")
    if ctx["{航空公司}"].as_str() != "不限航空公司":
        filter_conditions.append(f"{ctx['{航空公司}'].as_str()}")
    if ctx["{航班直飞还是转机}"].as_str() != "不限直飞还是转机":
        filter_conditions.append(f"{ctx['{航班直飞还是转机}'].as_str()}")
    if ctx["{航班起飞时段}"].as_str() != "不限起飞时段":
        filter_conditions.append(f"起飞时段是{ctx['{航班起飞时段}'].as_str()}")
    if ctx["{航班舱位等级}"].state() == 1:
        filter_conditions.append(f"{ctx['{航班舱位等级}'].as_str()}")
    ctx["{航班号选择提示信息}"] = "已按以下条件筛选航班：" + "，".join(filter_conditions) + "。"
    ctx["{航班号列表}"] = flight_number_list
    if len(flight_number_list) > 0:
        ctx["{航班号选择提示信息}"] = ctx["{航班号选择提示信息}"].as_str() + "价格不包含保险、燃油附加费、机场建设费。"
        ctx["{航班号选择结构化信息}"] = structured_rows
        ctx["{询问航班号问题}"] = "请选择一个航班号？"
    else:
        ctx["{航班号选择结构化信息}"] = ""
        ctx["{询问航班号问题}"] = "但没有满足条件的航班，请修改前面的条件。"
ask_flight_number_node = chattree.create_node( "#单次交互#", {
    "信息项":"{航班号}",
    "信息项修饰":["必需","复述","明确"],
    "系统问题":"{询问航班号问题}",
    "提问前执行脚本":before_ask_flight_number, # 注意这个属性
    "提问前提示用户":"{航班号选择提示信息}",     # 注意这个属性
    "提问前结构化输出":"{航班号选择结构化信息}", # 注意这个属性
    "节点注释":"依据下列信息项，列出符合条件的航班号及价格等相关信息供用户选择：\n"
              "{航班日期}、{航班起飞城市}、{航班降落城市}、{航班起飞机场}、{航班降落机场}\n"
              "{航空公司}、{航班直飞还是转机}、{航班起飞时段}、{航班舱位等级}\n"
              "其中{航班舱位等级}无值时（即用户到此时还未提及过）表示‘不限’，它可能会过滤掉部分航班号，也会影响价格等相关信息的展示；\n"
              "其它信息项可能为‘不限’\n"
              "然后根据情况选择返回若干行文本还是返回结构化数据让客户端生成 UI Widget",
})

# 判断用户输入的航班号是否在符合条件的航班号列表中
check_flight_number_invalid_node = chattree.create_node( "#条件#脚本", {
    "函数":lambda ctx: ctx["{航班号}"].as_str().strip() not in ctx["{航班号列表}"].as_json(),
    "节点注释":"检查用户选择的{航班号}是否在符合条件的航班号列表中",
})

# 如果用户输入的航班号不在符合条件的航班号列表中，则提示用户选择列表中的航班号
inform_user_select_listed_flight_number_node = chattree.create_node( "#提示用户#", {
    "提示内容":"您选择的航班号 ‘{航班号}’ 没有在列表中，请从列表中选择一个航班号",
})

# 如果用户输入的航班号不在符合条件的航班号列表中，再清除用户输入的航班号对应的{航班舱位等级}
exec_script_to_clear_flight_carbin_class_node = chattree.create_node( "#动作#执行脚本", {
    "函数":reset_flight_carbin_class,
    "节点注释":"用户选择的航班号不在列表中，提示用户选择列表中的航班号后，清除{航班舱位等级}",
})

# 上面提示完后，重新提问航班号
ask_again_flight_number_node = chattree.create_node( "#动作#重新提问", {
    "信息项":"{航班号}",
})

# 询问航班舱位等级
ask_flight_cabin_class_node = chattree.create_node( "#单次交互#", {
    "信息项":"{航班舱位等级}",
    "信息项修饰":["必需","复述","明确"],
    "系统问题":"选择什么等级的舱位？",
})

# 注意这里没有 “不限舱位等级” 的意图分支，{航班舱位等级} 无值时表示 “不限舱位等级”

# 意图分支：经济舱
economy_carbin_class_intent_node = chattree.create_node( "#用户意图#", {
    "意图":"经济舱",
})

# 意图分支：超级经济舱
super_economy_carbin_class_intent_node = chattree.create_node( "#用户意图#", {
    "意图":"超级经济舱",
})

# 意图分支：公务舱（商务舱）
business_carbin_class_intent_node = chattree.create_node( "#用户意图#", {
    "意图":"商务舱",
    "意图约束":"‘公务舱’就是‘商务舱’",
})

# 意图分支：头等舱（第一舱）
first_carbin_class_intent_node = chattree.create_node( "#用户意图#", {
    "意图":"头等舱",
    "意图约束":"‘一等舱’就是‘头等舱’",
})

# 判断用户输入的航班舱位等级是否在当前用户选择的航班号对应航班的舱位列表中，以及相关函数
def check_if_flight_cabin_class_invalid(ctx):
    assert ctx["{航班号}"].state() == 1
    chosen_flight = None
    for flight in _flight_databse:
        if flight["航班号"] == ctx["{航班号}"].as_str():
            chosen_flight = flight
            break
    assert chosen_flight is not None
    available_cabin_class_list = [item["航班舱位等级"] for item in chosen_flight["舱位价格信息"]]
    if ctx["{航班舱位等级}"].as_str() not in available_cabin_class_list:
        ctx["{航班舱位等级错误提示}"] = "抱歉，您选择的航班号 “" + ctx["{航班号}"].as_str() + "” 不支持 “" + ctx["{航班舱位等级}"].as_str() + "”，该航班可选舱位为：" + "、".join(available_cabin_class_list) + "，请重新选择"
        return True # 表示 invalid
    return False # 表示 valid
check_if_flight_cabin_class_invalid_node = chattree.create_node( "#条件#脚本", {
    "函数":check_if_flight_cabin_class_invalid,
    "节点注释":"检查用户输入的{航班舱位等级}是否在当前{航班号}对应航班的舱位列表中",
})

# 如果用户输入的航班舱位等级不在当前用户选择的航班号对应航班的舱位列表中，则提示用户重新选择
inform_user_if_flight_cabin_class_invalid_node = chattree.create_node( "#提示用户#", {
    "提示内容":"{航班舱位等级错误提示}",
})

# 上面提示完后，重新提问航班舱位等级
ask_flight_cabin_class_again_node = chattree.create_node( "#动作#重新提问", {
    "信息项":"{航班舱位等级}",
})

# 询问乘机人数
ask_number_of_passengers_of_flight_node = chattree.create_node( "#单次交互#", {
    "信息项":"{乘机人数}",
    "信息项约束":"不能是0，必须是正整数",
    "信息项修饰":["必需","复述"],
    "系统问题":"请问这次预订的机票需要几张？",
    "节点注释":"之前预设了缺省值1\nAI不会主动提问，但用户可以主动提及",
})

# 询问乘机人信息
ask_flight_passenger_info_node = chattree.create_node( "#单次交互#", {
    "信息项":"{乘机人信息}",
    "信息项约束":"包括如下5个字段：1.‘姓名’/如果指用户自己则内容设置为‘预订者本人’，2.‘证件类型’/内容只能是‘身份证’或‘护照’，3.‘证件号码’，4.‘证件有效期’/格式转换为YYYY-MM-DD，5.‘是否儿童’",
    "信息项修饰":["json","必需"], # 注意这里的 json 修饰
    "系统问题":"请告诉我乘机人的信息，包括姓名、证件类型、证件号码、证件有效期，如果是儿童请说明一下",
    "节点注释":"可以输入一个或多个乘机人信息",
})

# 判断乘机人数及乘机人信息的完整性和正确性，以及相关函数
def check_if_passenger_info_invalid(ctx):
    flight_passenger_info = ctx["{乘机人信息}"].as_json()
    assert len(flight_passenger_info) >= 1
    if ctx["{乘机人数}"].as_num() < len(flight_passenger_info):
        ctx["{乘机人数}"] = len(flight_passenger_info)
    elif ctx["{乘机人数}"].as_num() > len(flight_passenger_info):
        ctx["{乘机人信息错误提示}"] = "您之前输入（或默认）的乘机人数是 " + str(ctx["{乘机人数}"].as_num()) + "，但您仅提供了 " + str(len(flight_passenger_info)) + " 位乘机人信息，请补充"
        return True # 表示 inconsistency
    for passenger in flight_passenger_info:
        assert "姓名" in passenger
        if "商旅平台客户" in passenger["姓名"] or passenger["姓名"] == "预订者本人" : # “商旅平台客户”是系统识别后自动设置的 user_role，“预订者本人”是前面的信息项约束中设置的
            passenger["姓名"] = "张三" # 这里假设根据启动信息项 {用户ID} 获取的当前用户的姓名为 “张三”
        if "证件类型" not in passenger or passenger["证件类型"].strip() == "":
            if passenger["姓名"] == "赵六": # 假设的历史乘机人姓名
                passenger["证件类型"] = "身份证" # 这里假设获取的历史乘机人的相关信息
            else:
                ctx["{乘机人信息错误提示}"] = "乘机人 “" + passenger["姓名"] + "” 没有提供‘证件类型’，请重新输入（也请仔细检查其它可能的错误）"
                return True # 表示 invalid
        if "证件号码" not in passenger or passenger["证件号码"].strip() == "":
            if passenger["姓名"] == "赵六":
                passenger["证件号码"] = "110100198001011234" # 这里假设获取的历史乘机人的相关信息
            else:
                ctx["{乘机人信息错误提示}"] = "乘机人 “" + passenger["姓名"] + "” 没有提供‘证件号码’，请重新输入（也请仔细检查其它可能的错误）"
                return True # 表示 invalid
        if "证件有效期" not in passenger or passenger["证件有效期"].strip() == "":
            if passenger["姓名"] == "赵六":
                passenger["证件有效期"] = "2027-01-01" # 这里假设获取的历史乘机人的相关信息
            else:
                ctx["{乘机人信息错误提示}"] = "乘机人 “" + passenger["姓名"] + "” 没有提供‘证件有效期’，请重新输入（也请仔细检查其它可能的错误）"
                return True # 表示 invalid
        if "是否儿童" not in passenger:
            if passenger["姓名"] == "赵六": # 假设的历史乘机人姓名
                passenger["是否儿童"] = True # 也可能是 False，这里假设获取的历史乘机人的相关信息
            else:
                passenger["是否儿童"] = False # 未说明则认为不是儿童
        # 下面检查身份证的证件号码的正确性，可以依葫芦画瓢增加更多证件号码的检查规则
        if passenger["证件类型"] == "身份证" and not re.match(r"^[0-9]{17}[0-9X]{1}$", passenger["证件号码"].strip()):
            ctx["{乘机人信息错误提示}"] = "乘机人 “" + passenger["姓名"] + "” 的证件号码 “" + passenger["证件号码"] + "” 有误，请重新输入（也请仔细检查其它可能的错误）"
            return True # 表示 invalid
        # 下面检查身份证的证件有效期的有效性，可以依葫芦画瓢增加更多证件有效期的检查规则
        if passenger["证件类型"] == "身份证" and datetime.datetime.strptime(passenger["证件有效期"], "%Y-%m-%d").date() < (datetime.datetime.now().date() + datetime.timedelta(days=90)): # 这里假设身份证的有效期必须是当前日期的90天后
            ctx["{乘机人信息错误提示}"] = "乘机人 “" + passenger["姓名"] + "” 的证件有效期 “" + passenger["证件有效期"] + "” 已过期或不足，请重新输入（也请仔细检查其它可能的错误）"
            return True # 表示 invalid
        # 这里还可以有更多的检查，都可以 “依葫芦画瓢”
    ctx["{乘机人信息}"] = flight_passenger_info # 将可能修改过的乘机人信息重新写回 ctx
    return False # 表示 valid
check_if_passenger_info_invalid_node = chattree.create_node( "#条件#脚本", {
    "函数":check_if_passenger_info_invalid,
    "节点注释":"检查乘机人信息是否有错误，并做相应处理",
})

# 如果乘机人信息有错误，则提示用户具体的错误信息
inform_user_passenger_info_invalidation_node = chattree.create_node( "#提示用户#", {
    "提示内容":"{乘机人信息错误提示}",
})

# 上面提示完后，重新提问乘机人信息
ask_passenger_info_again_node = chattree.create_node( "#动作#重新提问", {
    "信息项":"{乘机人信息}",
})

# 汇总预订信息，提示用户，并向用户确认是否都正确
def get_all_flight_booking_info(ctx):
    def to_bool(value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in ["true", "1", "yes", "是", "对", "y", "t"]
        if isinstance(value, (int, float)):
            return value != 0
        return False
    passenger_count = ctx["{乘机人数}"].as_num()
    assert passenger_count >= 1
    passenger_info_list = ctx["{乘机人信息}"].as_json()
    assert len(passenger_info_list) >= 1
    assert len(passenger_info_list) == passenger_count
    chosen_flight = None
    assert ctx["{航班号}"].state() == 1
    for flight in _flight_databse:
        if flight["航班号"] == ctx["{航班号}"].as_str():
            chosen_flight = flight
            break
    assert chosen_flight is not None
    assert ctx["{航班舱位等级}"].state() == 1
    cabin_price = None
    for item in chosen_flight["舱位价格信息"]:
        if item["航班舱位等级"] == ctx["{航班舱位等级}"].as_str():
            cabin_price = int(item["价格"])
            break
    assert cabin_price is not None
    fuel_fee_adult = 100
    fuel_fee_child = 50
    airport_fee_adult = 50
    airport_fee_child = 0
    passenger_lines = []
    total_ticket_price = 0
    total_fuel_fee = 0
    total_airport_fee = 0
    for idx, passenger in enumerate(passenger_info_list, start=1):
        name = passenger.get("姓名", f"乘机人{idx}")
        is_child = to_bool(passenger.get("是否儿童", None))
        assert is_child is not None
        id_type = passenger.get("证件类型", None)
        assert id_type is not None
        id_number = passenger.get("证件号码", None)
        assert id_number is not None
        id_validity_date = passenger.get("证件有效期", None)
        assert id_validity_date is not None
        ticket_price = int(cabin_price * (0.5 if is_child else 1.0))
        fuel_fee = fuel_fee_child if is_child else fuel_fee_adult
        airport_fee = airport_fee_child if is_child else airport_fee_adult
        subtotal = ticket_price + fuel_fee + airport_fee
        total_ticket_price += ticket_price
        total_fuel_fee += fuel_fee
        total_airport_fee += airport_fee
        passenger_type = "儿童" if is_child else "成人"
        passenger_lines.append(
            f"{idx}. {name}（{passenger_type}，{id_type}，{id_number}，{id_validity_date}）：票价¥{ticket_price} + 燃油¥{fuel_fee} + 机建¥{airport_fee} = 小计¥{subtotal}"
        )
    total_price = total_ticket_price + total_fuel_fee + total_airport_fee
    summary_lines = [
        f"【航班信息】航班号：{chosen_flight['航班号']}（{chosen_flight['航空公司']}），{chosen_flight['航班日期']}，{chosen_flight['航班起飞城市']}{chosen_flight['航班起飞机场']} -> {chosen_flight['航班降落城市']}{chosen_flight['航班降落机场']}，从 {chosen_flight['航班起飞时间']} 到 {chosen_flight['航班降落时间']}，{chosen_flight['航班直飞还是转机']}，{ctx["{航班舱位等级}"].as_str()}。",
        f"【乘机人及费用明细】" + "；".join(passenger_lines) + "。",
        f"【费用汇总】票价合计：¥{total_ticket_price}，燃油附加费合计：¥{total_fuel_fee}，机场建设费合计：¥{total_airport_fee}，应付总额：¥{total_price}。",
    ]
    ctx["{机票预订信息汇总}"] = "\n".join(summary_lines)
ask_if_all_flight_booking_info_correct_node = chattree.create_node( "#单次交互#", {
    "信息项":"{是否所有机票预订信息都正确}",
    "信息项修饰":["必需","固定","隐含"],
    "系统问题":"请确认这些机票预订信息是否都正确？",
    "提问前执行脚本":get_all_flight_booking_info,
    "提问前提示用户":"{机票预订信息汇总}",
})

# 意图分支：机票预订信息不都正确
not_all_flight_booking_info_correct_intent_node = chattree.create_node( "#用户意图#", {
    "意图":"机票预订信息不都正确",
})

# 意图分支：机票预订信息都正确
all_flight_booking_info_correct_intent_node = chattree.create_node( "#用户意图#", {
    "意图":"机票预订信息都正确",
})

# 上面 “机票预订信息不都正确” 意图分支后，重新提问所有机票预订信息是否都正确
ask_again_if_all_flight_booking_info_correct_node = chattree.create_node( "#动作#重新提问", {
    "信息项":"{是否所有机票预订信息都正确}",
})

# 上面 “机票预订信息都正确” 意图分支后，提交订单并获取支付链接的函数（这里的实现只是示例，实际情况可能需要调用第三方 API 等等）
def submit_order_and_get_payment_link(ctx):
    # 提交订单
    pass
    # 获取支付链接
    ctx["{支付链接}"] = "https://www.example.com/payment_link?order_id=123456"
submit_order_and_get_payment_link_node = chattree.create_node( "#动作#执行脚本", {
    "函数":submit_order_and_get_payment_link,
})

# 提示用户订单提交成功并提供支付链接
provide_payment_link_node = chattree.create_node( "#提示用户#", {
    "提示内容":"您的订单已经提交成功，请于 3 小时内点击以下链接进行支付：{支付链接}",
})

# -------------------------------------------------------------------------------------
# （除了后继触发类节点的）拓扑结构，“>>” 表示节点之间的连接关系，这里的连接关系也决定了对话的流程走向
# -------------------------------------------------------------------------------------

start_node >> [
    ask_flight_date_node >> check_if_flight_date_invalid_node >> inform_user_if_flight_date_invalid_node >> ask_flight_date_again_node,
    ask_flight_departure_city_node >> check_if_flight_departure_city_invalid_node >> inform_user_if_flight_departture_city_invalid_node >> ask_flight_departure_city_again_node,
    ask_flight_landing_city_node >> check_if_flight_landing_city_invalid_node >> inform_user_if_flight_landing_city_invalid_node >> ask_flight_landing_city_again_node,
    set_default_and_prefered_value_node,
    judge_if_has_preference_tips_node >> show_preference_tips_node,
    ask_flight_departure_airport_node >> check_if_flight_departure_airport_invalid_node >> inform_user_if_flight_departure_airport_invalid_node >> [
        check_if_only_one_airport_for_departure_city_node >> set_only_one_airport_for_departure_city_node,
        check_if_not_only_one_airport_for_departure_city_node >> ask_flight_departure_airport_again_node
    ],
    ask_flight_landing_airport_node >> check_if_flight_landing_airport_invalid_node >> inform_user_if_flight_landing_airport_invalid_node >> [
        check_if_only_one_airport_for_landing_city_node >> set_only_one_airport_for_landing_city_node,
        check_if_not_only_one_airport_for_landing_city_node >> ask_flight_landing_airport_again_node
    ],
    ask_flight_airline_node >> check_if_flight_airlines_invalid_node >> inform_user_if_flight_airlines_invalid_node >> ask_flight_airlines_again_node,
    ask_flight_direct_or_connecting_node >> [
        flight_direct_or_connecting_intent_node,
        flight_direct_intent_node,
        flight_connecting_intent_node,
    ],
    ask_flight_departure_time_slot_node >> [
        all_time_slot_intent_node,
        early_morning_intent_node,
        morning_intent_node,
        late_morning_intent_node,
        noon_intent_node,
        afternoon_intent_node,
        evening_intent_node,
        night_intent_node,
    ],
    ask_flight_number_node >> check_flight_number_invalid_node >> inform_user_select_listed_flight_number_node >> exec_script_to_clear_flight_carbin_class_node >> ask_again_flight_number_node,
    ask_flight_cabin_class_node >> [
        economy_carbin_class_intent_node >> check_if_flight_cabin_class_invalid_node >> inform_user_if_flight_cabin_class_invalid_node >> ask_flight_cabin_class_again_node,
        super_economy_carbin_class_intent_node >> check_if_flight_cabin_class_invalid_node,
        business_carbin_class_intent_node >> check_if_flight_cabin_class_invalid_node,
        first_carbin_class_intent_node >> check_if_flight_cabin_class_invalid_node,
    ],
    ask_number_of_passengers_of_flight_node,
    ask_flight_passenger_info_node >> check_if_passenger_info_invalid_node >> inform_user_passenger_info_invalidation_node >> ask_passenger_info_again_node,
    ask_if_all_flight_booking_info_correct_node >> [
        not_all_flight_booking_info_correct_intent_node >> ask_again_if_all_flight_booking_info_correct_node,
        all_flight_booking_info_correct_intent_node >> submit_order_and_get_payment_link_node >> provide_payment_link_node,
    ],
]

# -------------------------------------------------------------------------------------
# 触发类节点定义
# -------------------------------------------------------------------------------------

# 触发节点
trigger_node = chattree.create_node( "#触发#", {})

# 触发意图：表示用户不需要预订机票了，要结束对话了
no_need_to_book_flight_intent_node = chattree.create_node( "#用户意图#", {
    "意图":"表示不需要预订所有机票了",
    "意图约束":"包括但不限于‘别人已经帮预订好了’、‘行程取消了’、‘改乘坐高铁了’等等，但不包含仅取消部分人的机票的情况",
})

# 确认是否要结束对话
confirm_really_want_to_end_dialogue_node = chattree.create_node( "#单次交互#", {
    "信息项":"{是否确认结束对话}",
    "信息项修饰":["必需","固定","明确"],
    "系统问题":"请问您确定不需要预订机票了，要结束对话吗？",
})

# 意图分支：确认结束对话
confirm_end_dialogue_intent_node = chattree.create_node( "#用户意图#", {
    "意图":"确认结束对话",
})

# 意图分支：未确认结束对话
not_confirm_end_dialogue_intent_node = chattree.create_node( "#用户意图#", {
    "意图":"未确认结束对话",
})

# 上面 “”确认结束对话” 意图分支后，实际结束对话
terminate_node = chattree.create_node( "#动作#结束", {} )

# -------------------------------------------------------------------------------------
# 触发节点的拓扑结构，“>>” 表示节点之间的连接关系，这里的连接关系也决定了对话的流程走向
# -------------------------------------------------------------------------------------

trigger_node >> [
    no_need_to_book_flight_intent_node >> confirm_really_want_to_end_dialogue_node >> [
        confirm_end_dialogue_intent_node >> terminate_node,
        not_confirm_end_dialogue_intent_node
    ]
]

# -------------------------------------------------------------------------------------
# 每个 python 对话树文件的标准代码结尾部分，即渲染对话树成为 HTML 文件的代码
# -------------------------------------------------------------------------------------

if __name__ == "__main__":
    chattree.render(__file__)