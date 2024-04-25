import json
from typing import Tuple, List, Iterable
import torch
import numpy as np

import requests
from transformers.generation import LogitsProcessor

from rag.prompt.buy_car.buy_car import TOOL_BUY_CAR, TOOL_DESC_BUY_CAR, REACT_PROMPT_BUY_CAR
from rag.prompt.buy_car.the_car_appointment import TOOL_THE_CAR_APPOINTMENT, TOOL_DESC_THE_CAR_APPOINTMENT, \
    REACT_PROMPT_THE_CAR_APPOINTMENT
from rag.prompt.buy_car.used_car_valuation import TOOL_USED_CAR_VALUATION, TOOL_DESC_USED_CAR_VALUATION, \
    REACT_PROMPT_USED_CAR_VALUATION
from rag.rag_handler import tool_wrapper_for_qwen_buy_car, tool_wrapper_for_qwen_used_car_valuation, \
    tool_wrapper_for_qwen_appointment


def tool_wrapper_for_qwen(tool):
    def tool_(query):
        query = json.loads(query)["query"]
        return tool.run(query)

    return tool_


def tool_wrapper_for_qwen_name():
    def tool_(query, already_known_user, user_id):
        query = json.loads(query)["query"]
        return '你是智能机器人BAVA，你是ubiai开发的', already_known_user

    return tool_

def tool_wrapper_for_qwen_vehicle_issues():
    def tool_(query, already_known_user, user_id):
        query = json.loads(query)["query"]
        return '请咨询优必爱客服', already_known_user

    return tool_




# 以下是给千问看的工具描述：
TOOLS = [
    # {
    #     'name_for_human':
    #         'google search',
    #     'name_for_model':
    #         'Search',
    #     'description_for_model':
    #         'useful for when you need to answer questions about current events.',
    #     'parameters': [{
    #         "name": "query",
    #         "type": "string",
    #         "description": "search query of google",
    #         'required': True
    #     }],
    #     'tool_api': tool_wrapper_for_qwen(search)
    # },
    # {
    #     'name_for_human':
    #         'python',
    #     'name_for_model':
    #         'python',
    #     'description_for_model':
    #         "A Python shell. Use this to execute python commands include Math,current time,date or day of the week. When using this tool, sometimes output is abbreviated - Make sure it does not look abbreviated before using it in your answer. "
    #         "Don't add comments to your python code.",
    #     'parameters': [{
    #         "name": "query",
    #         "type": "string",
    #         "description": "a valid python command.",
    #         'required': True
    #     }],
    #     'tool_api': tool_wrapper_for_qwen(python)
    # },
    {
        'name_for_human':
            'the_car_appointment',
        'name_for_model':
            'the_car_appointment',
        'description_for_model':
            "用这个工具记录下用户的预约信息，预约信息包括预约时间（appointment_time），车辆维护类型"
            "（vehicle_maintenance_type），车辆品牌名称（vehicle_brand_name），"
            "4s店名称（automobile_sales_service_shop_name），"
            "4s店地址（automobile_sales_service_shop_address），用户想要预约时调用这个工具。",
        'parameters': [{
            "name": "appointment_time",
            "type": "string",
            "description": "time（What day and what time）",
            'required': True
        },{
            "name": "vehicle_maintenance_type",
            "type": "string",
            "description": "保养或维修二选一",
            'required': True
        },{
            "name": "vehicle_brand_name",
            "type": "string",
            "description": "车辆品牌名称",
            'required': True
        },{
            "name": "automobile_sales_service_shop_name",
            "type": "string",
            "description": "4s店名称",
            'required': True
        },{
            "name": "automobile_sales_service_shop_address",
            "type": "string",
            "description": "4s店地址",
            'required': True
        },],
        'tool_api': tool_wrapper_for_qwen_appointment()
    },
    {
        'name_for_human':
            'name',
        'name_for_model':
            'name',
        'description_for_model': "返回AI助手的名字. 当用户问到你是谁或者你是谁开发的，或者你是不是谁时，使用这个工具，只问名字时不用说是谁开发的，根据用户是问的中英文来选择是中文还是英文回答，你是宝马智能机器人BAVA",
        'parameters': [{
            "name": "query",
            "type": "string",
            "description": "name",
            'required': True
        }],
        'tool_api': tool_wrapper_for_qwen_name()
    },
    {
        'name_for_human':
            'buy_car',
        'name_for_model':
            'buy_car',
        'description_for_model': "这是一个给用户推荐车的工具。当用户想买车或者按条件查询车的时候调用这个工具，"
                                 "请根据上下文判断是不是买车或推荐车场景，不用管上下文有没有推荐过，"
                                 "调用这个工具前需要收集用户对车的预期，尽量提取用户说的预期，"
                                 "对车的预期包含价位（price），车型分类（vehicle_classification），"
                                 "能源形式（energy_type），品牌类型（brand_type），车型级别（vehicle_size），座位数（number_of_seats），"
                                 "车门数（number_of_doors），车辆厢数（number_of_compartments），车辆品牌名称（vehicle_brand_name）。",
        'parameters': [{
            "name": "price",
            "type": "string",
            "description": "价位的形式可以是X万，X万左右，X万到Y万，X万以内，X万以上或不限.其中X和Y为价格",
            'required': False
        }, {
            "name": "vehicle_classification",
            "type": "string",
            "description": "车型分类可以是轿车，MPV，SUV，跑车或不限，可以多选，多选的话用英文逗号分隔",
            'required': False
        }, {
            "name": "energy_type",
            "type": "string",
            "description": "能源类型可以是燃油车，新能源，混合动力或不限，可以多选，多选的话用英文逗号分隔",
            'required': False
        }, {
            "name": "brand_type",
            "type": "string",
            "description": "品牌类型可以是豪华，合资，国产，新势力或不限，可以多选，多选的话用英文逗号分隔",
            'required': False
        }, {
            "name": "vehicle_size",
            "type": "string",
            "description": "车型级别可以是微型车/A00级，小型车/A0级，紧凑型车/A级，中型车/B级，中大型车/C级，"
                           "大型车/D级或不限，可以多选，多选的话用英文逗号分隔",
            'required': False
        }, {
            "name": "number_of_seats",
            "type": "string",
            "description": "座位数可以是2座，4座，5座，6座，7座，7座以上或不限，可以多选，多选的话用英文逗号分隔",
            'required': False
        }, {
            "name": "number_of_doors",
            "type": "string",
            "description": "车门数可以是两门，三门，四门，五门或不限，可以多选，多选的话用英文逗号分隔",
            'required': False
        }, {
            "name": "number_of_compartments",
            "type": "string",
            "description": "车辆厢数可以是两厢，三厢或不限，可以多选，多选的话用英文逗号分隔",
            'required': False
        }, {
            "name": "vehicle_brand_name",
            "type": "string",
            "description": "品牌名称可以是奔驰，宝马，奥迪，日产，丰田，本田，福特，凯迪拉克，别克，标志，"
                           "雪铁龙或不限，可以多选，多选的话用英文逗号分隔",
            'required': False
        }],
        'tool_api': tool_wrapper_for_qwen_buy_car()
    },
    {
        'name_for_human':
            'used_car_valuation',
        'name_for_model':
            'used_car_valuation',
        'description_for_model': "这是一个给二手车估值的工具。当用户想对车辆进行估值或卖车的时候调用这个工具，"
                                 "返回的是评估出的车辆的价格，目前不知道任何车辆信息，Action Input中的信息需要是用户说的，"
                                 "调用这个工具之前必须收集用户对车的描述，从用户描述中尽量提取用户说的车辆信息，这些信息不需要全都有"
                                 "对车的描述包含 车辆品牌名称（vehicle_brand_name），车系（vehicle_series），车辆年款（vehicle_model_year），"
                                 "车辆上牌时年份（vehicle_licensing_year），车辆上牌时月份（vehicle_licensing_month），"
                                 "车辆上牌地所在城市（vehicle_licensing_city），车辆里程数（vehicle_mileage），"
                                 "车身颜色（vehicle_exterior_color）。",
        'parameters': [{
            "name": "vehicle_brand_name",
            "type": "string",
            "description": "品牌名称可以是奔驰，奥迪，日产，丰田，本田，福特，凯迪拉克，别克，标志，"
                           "雪铁龙等任何品牌，只能有一个值",
            'required': False
        },{
            "name": "vehicle_series",
            "type": "string",
            "description": "车系名称可以是M5，i3,宏光等任何车系，只能有一个值",
            'required': False
        },{
            "name": "vehicle_model_year",
            "type": "string",
            "description": "车辆年款可以是2023款，2019款，2008款等，只能有一个值",
            'required': False
        },{
            "name": "vehicle_licensing_year",
            "type": "string",
            "description": "车辆上牌年份是一个具体年份，比如2016年,2020年,2021年,2023年等，只能有一个值",
            'required': False
        },{
            "name": "vehicle_licensing_month",
            "type": "string",
            "description": "车辆上牌月份是一个具体月份，比如1月,2月,11月等，只能有一个值",
            'required': False
        },{
            "name": "vehicle_licensing_city",
            "type": "string",
            "description": "车辆上牌地所在城市是一个城市名，问清楚用户是在哪个城市，只能有一个值",
            'required': False
        },{
            "name": "vehicle_mileage",
            "type": "string",
            "description": "车辆里程数是车辆行驶了多少万公里，比如1万公里，4万公里，单位是万公里，只能有一个值",
            'required': False
        },{
            "name": "vehicle_exterior_color",
            "type": "string",
            "description": "车身颜色是车辆的颜色，只能有一个值",
            'required': False
        }],
        'tool_api': tool_wrapper_for_qwen_used_car_valuation()
    },
    {
        'name_for_human':
            'vehicle_issues',
        'name_for_model':
            'vehicle_issues',
        'description_for_model': "当有汽车功能，汽车故障相关的问题时，调用这个工具",
        'parameters': [{
            "name": "query",
            "type": "string",
            "description": "用户的问题",
            'required': True
        }],
        'tool_api': tool_wrapper_for_qwen_vehicle_issues()
    }

]
TOOL_DESC = """{name_for_model}: Call this tool to interact with the {name_for_human} API. What is the {name_for_human} API useful for? {description_for_model}. Parameters: {parameters} Format the arguments as a JSON object."""

REACT_PROMPT = """Answer the following questions as best you can. You have access to the following tools:

{tool_descs}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action with json formatted
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can be repeated zero or more times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {query}"""


def build_planning_prompt(query, already_known_user):
    #  ensure_ascii=False：非ascii不会被转义
    tool_descs = []
    tool_names = []
    # 计数有值的数量
    count_values = sum(1 for value in already_known_user.values() if value)
    if count_values > 1:
        raise Exception("already_known_user中不止一个value有值")
    elif count_values == 1:
        key = [key for key, value in already_known_user.items() if value][0]
        if "buy_car" == key:
            # query = '已知用户预期：' + already_known_user['buy_car'] + ',用户新说的预期：' + query
            print('进入推荐车场景')
            info = TOOL_BUY_CAR[0]
            tool_descs.append(
                TOOL_DESC_BUY_CAR.format(
                    name_for_model=info['name_for_model'],
                    name_for_human=info['name_for_human'],
                    description_for_model=info['description_for_model'],
                    already_known=already_known_user['{}'.format(info['name_for_model'])],
                    parameters=json.dumps(info['parameters'], ensure_ascii=False),
                )
            )
            tool_names.append(info['name_for_model'])

            tool_descs = '\n\n'.join(tool_descs)
            tool_names = ','.join(tool_names)

            prompt = REACT_PROMPT_BUY_CAR.format(tool_descs=tool_descs, tool_names=tool_names, query=query)
            return prompt
        elif "used_car_valuation" == key:
            print('进入二手车估值场景')
            info = TOOL_USED_CAR_VALUATION[0]
            tool_descs.append(
                TOOL_DESC_USED_CAR_VALUATION.format(
                    name_for_model=info['name_for_model'],
                    name_for_human=info['name_for_human'],
                    description_for_model=info['description_for_model'],
                    already_known=already_known_user['{}'.format(info['name_for_model'])],
                    parameters=json.dumps(info['parameters'], ensure_ascii=False),
                )
            )
            tool_names.append(info['name_for_model'])

            tool_descs = '\n\n'.join(tool_descs)
            tool_names = ','.join(tool_names)

            prompt = REACT_PROMPT_USED_CAR_VALUATION.format(tool_descs=tool_descs, tool_names=tool_names, query=query)
            return prompt
        elif "the_car_appointment" == key:
            print('进入预约场景')
            info = TOOL_THE_CAR_APPOINTMENT[0]
            tool_descs.append(
                TOOL_DESC_THE_CAR_APPOINTMENT.format(
                    name_for_model=info['name_for_model'],
                    name_for_human=info['name_for_human'],
                    description_for_model=info['description_for_model'],
                    already_known=already_known_user['{}'.format(info['name_for_model'])],
                    parameters=json.dumps(info['parameters'], ensure_ascii=False),
                )
            )
            tool_names.append(info['name_for_model'])

            tool_descs = '\n\n'.join(tool_descs)
            tool_names = ','.join(tool_names)

            prompt = REACT_PROMPT_THE_CAR_APPOINTMENT.format(tool_descs=tool_descs, tool_names=tool_names, query=query)
            return prompt

    else:
        print('无预置场景')
        for info in TOOLS:
            tool_descs.append(
                TOOL_DESC.format(
                    name_for_model=info['name_for_model'],
                    name_for_human=info['name_for_human'],
                    description_for_model=info['description_for_model'],
                    already_known=already_known_user['{}'.format(info['name_for_model'])],
                    parameters=json.dumps(info['parameters'], ensure_ascii=False),
                )
            )
            tool_names.append(info['name_for_model'])

        tool_descs = '\n\n'.join(tool_descs)
        tool_names = ','.join(tool_names)

        prompt = REACT_PROMPT.format(tool_descs=tool_descs, tool_names=tool_names, query=query)
        return prompt


def handle_already_known_user(already_known_user_detail):
    if already_known_user_detail:
        already_known_described = ''
        for key, value in already_known_user_detail.items():
            already_known_described += '用户已经确定想要的' + key + '是' + value + ';'
        return already_known_described
    else:
        return already_known_user_detail


def use_api(response, already_known_user, user_id):
    use_toolname, action_input = parse_latest_plugin_call(response)
    if use_toolname == "":
        return "no tool founds", already_known_user
    # 计数有值的数量
    count_values = sum(1 for value in already_known_user.values() if value)
    used_tool_meta = []
    if count_values > 1:
        raise Exception("already_known_user中不止一个value有值")
    elif count_values == 1:
        key = [key for key, value in already_known_user.items() if value][0]
        if "buy_car" == key:
            used_tool_meta = list(filter(lambda x: x["name_for_model"] == use_toolname, TOOL_BUY_CAR))
        elif "used_car_valuation" == key:
            used_tool_meta = list(filter(lambda x: x["name_for_model"] == use_toolname, TOOL_USED_CAR_VALUATION))
    else:
        used_tool_meta = list(filter(lambda x: x["name_for_model"] == use_toolname, TOOLS))
    if len(used_tool_meta) == 0:
        return "no tool founds", already_known_user
    print('使用的工具：' + used_tool_meta[0]["name_for_model"])
    api_output, already_known_user = used_tool_meta[0]["tool_api"](action_input, already_known_user, user_id)
    return api_output, already_known_user


def parse_latest_plugin_call(text: str) -> Tuple[str, str]:
    i = text.rfind('\nAction:')
    j = text.rfind('\nAction Input:')
    k = text.rfind('\nObservation:')
    if 0 <= i < j:  # If the text has `Action` and `Action input`,
        if k < j:  # but does not contain `Observation`,
            # then it is likely that `Observation` is ommited by the LLM,
            # because the output text may have discarded the stop word.
            text = text.rstrip() + '\nObservation:'  # Add it back.
            k = text.rfind('\nObservation:')
    if 0 <= i < j < k:
        plugin_name = text[i + len('\nAction:'):j].strip()
        plugin_args = text[j + len('\nAction Input:'):k].strip()
        return plugin_name, plugin_args
    return '', ''


def trim_stop_words(response, stop_words):
    if stop_words:
        for stop in stop_words:
            idx = response.find(stop)
            if idx != -1:
                response = response[:idx]
    return response


class StopWordsLogitsProcessor(LogitsProcessor):
    """
    :class:`transformers.LogitsProcessor` that enforces that when specified sequences appear, stop geration.
    Args:
        stop_words_ids (:obj:`List[List[int]]`):
            List of list of token ids of stop ids. In order to get the tokens of the words
            that should not appear in the generated text, use :obj:`tokenizer(bad_word,
            add_prefix_space=True).input_ids`.
        eos_token_id (:obj:`int`):
            The id of the `end-of-sequence` token.
    """

    def __init__(self, stop_words_ids: Iterable[Iterable[int]], eos_token_id: int):

        if not isinstance(stop_words_ids, List) or len(stop_words_ids) == 0:
            raise ValueError(
                f"`stop_words_ids` has to be a non-emtpy list, but is {stop_words_ids}."
            )
        if any(not isinstance(bad_word_ids, list) for bad_word_ids in stop_words_ids):
            raise ValueError(
                f"`stop_words_ids` has to be a list of lists, but is {stop_words_ids}."
            )
        if any(
                any(
                    (not isinstance(token_id, (int, np.integer)) or token_id < 0)
                    for token_id in stop_word_ids
                )
                for stop_word_ids in stop_words_ids
        ):
            raise ValueError(
                f"Each list in `stop_words_ids` has to be a list of positive integers, but is {stop_words_ids}."
            )

        self.stop_words_ids = list(
            filter(
                lambda bad_token_seq: bad_token_seq != [eos_token_id], stop_words_ids
            )
        )
        self.eos_token_id = eos_token_id
        for stop_token_seq in self.stop_words_ids:
            assert (
                    len(stop_token_seq) > 0
            ), "Stop words token sequences {} cannot have an empty list".format(
                stop_words_ids
            )

    def __call__(
            self, input_ids: torch.LongTensor, scores: torch.FloatTensor
    ) -> torch.FloatTensor:
        stopped_samples = self._calc_stopped_samples(input_ids)
        for i, should_stop in enumerate(stopped_samples):
            if should_stop:
                scores[i, self.eos_token_id] = float(2 ** 15)
        return scores

    def _tokens_match(self, prev_tokens: torch.LongTensor, tokens: List[int]) -> bool:
        if len(tokens) == 0:
            # if bad word tokens is just one token always ban it
            return True
        elif len(tokens) > len(prev_tokens):
            # if bad word tokens are longer then prev input_ids they can't be equal
            return False
        elif prev_tokens[-len(tokens):].tolist() == tokens:
            # if tokens match
            return True
        else:
            return False

    def _calc_stopped_samples(self, prev_input_ids: Iterable[int]) -> Iterable[int]:
        stopped_samples = []
        for prev_input_ids_slice in prev_input_ids:
            match = False
            for stop_token_seq in self.stop_words_ids:
                if self._tokens_match(prev_input_ids_slice, stop_token_seq):
                    # if tokens do not match continue
                    match = True
                    break
            stopped_samples.append(match)

        return stopped_samples
