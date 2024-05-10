import datetime
import json
from typing import Tuple

from rag_classification.prompt.final_answer.prompt_buy_car_final import TOOL_BUY_CAR_FINAL, REACT_PROMPT_BUY_CAR_FINAL, \
    TOOL_DESC_BUY_CAR_FINAL
from rag_classification.prompt.final_answer.prompt_the_car_appointment_final import TOOL_THE_CAR_APPOINTMENT_FINAL, \
    TOOL_DESC_THE_CAR_APPOINTMENT_FINAL, REACT_PROMPT_THE_CAR_APPOINTMENT_FINAL
from rag_classification.prompt.final_answer.prompt_used_car_valuation_final import TOOL_USED_CAR_VALUATION_FINAL, \
    TOOL_DESC_USED_CAR_VALUATION_FINAL, REACT_PROMPT_USED_CAR_VALUATION_FINAL
from rag_classification.prompt.final_answer.prompt_vehicle_issues_final import TOOL_VEHICLE_ISSUES_FINAL, \
    TOOL_DESC_VEHICLE_ISSUES_FINAL, REACT_PROMPT_VEHICLE_ISSUES_FINAL
from rag_classification.prompt.prompt_buy_car import REACT_PROMPT_BUY_CAR, TOOL_DESC_BUY_CAR, TOOL_BUY_CAR
from rag_classification.prompt.prompt_change_scene import TOOL_DESC_CHANGE_SCENE, TOOLS_CHANGE_SCENE, \
    REACT_PROMPT_CHANGE_SCENE
from rag_classification.prompt.prompt_classification import TOOLS, TOOL_DESC, REACT_PROMPT
from rag_classification.prompt.prompt_name import TOOL_NAME, TOOL_DESC_NAME, REACT_PROMPT_NAME
from rag_classification.prompt.prompt_no_scene import REACT_PROMPT_NO_SCENE
from rag_classification.prompt.prompt_search_web import TOOL_SEARCH_WEB, TOOL_DESC_SEARCH_WEB, REACT_PROMPT_SEARCH_WEB
from rag_classification.prompt.prompt_the_car_appointment import TOOL_THE_CAR_APPOINTMENT, \
    TOOL_DESC_THE_CAR_APPOINTMENT, REACT_PROMPT_THE_CAR_APPOINTMENT
from rag_classification.prompt.prompt_used_car_valuation import REACT_PROMPT_USED_CAR_VALUATION, \
    TOOL_USED_CAR_VALUATION, TOOL_DESC_USED_CAR_VALUATION
from rag_classification.prompt.prompt_vehicle_issues import TOOL_VEHICLE_ISSUES, TOOL_DESC_VEHICLE_ISSUES, \
    REACT_PROMPT_VEHICLE_ISSUES
from rag_classification.prompt.prompt_what_scenes import TOOL_WHAT_SCENES, REACT_PROMPT_WHAT_SCENES, \
    TOOL_DESC_WHAT_SCENES
from logging_xianyi.logging_xianyi import logging_xianyi


def build_planning_prompt(query, already_known_user, user_id):
    #  ensure_ascii=False：非ascii不会被转义
    tool_descs = []
    tool_names = []
    if '' == already_known_user['scene']:
        print('无预置场景')
        logging_xianyi.debug('无预置场景', user_id)
        for info in TOOLS:
            tool_descs.append(
                TOOL_DESC.format(
                    name_for_model=info['name_for_model'],
                    name_for_human=info['name_for_human'],
                    description_for_model=info['description_for_model'],
                )
            )
            tool_names.append(info['name_for_model'])
        tool_descs = '\n\n'.join(tool_descs)
        tool_names = ','.join(tool_names)

        prompt = REACT_PROMPT.format(tool_descs=tool_descs, tool_names=tool_names, query=query)
        return prompt
    elif 'name' == already_known_user['scene']:
        print('进入身份询问场景')
        logging_xianyi.debug('进入身份询问场景', user_id)
        info = TOOL_NAME[0]
        tool_descs.append(
            TOOL_DESC_NAME.format(
                name_for_model=info['name_for_model'],
                name_for_human=info['name_for_human'],
                description_for_model=info['description_for_model'],
                parameters=json.dumps(info['parameters'], ensure_ascii=False),
            )
        )
        tool_names.append(info['name_for_model'])

        tool_descs = '\n\n'.join(tool_descs)
        tool_names = ','.join(tool_names)

        prompt = REACT_PROMPT_NAME.format(tool_descs=tool_descs, tool_names=tool_names, query=query)
        return prompt
    elif 'buy_car' == already_known_user['scene']:
        print('进入推荐车场景')
        logging_xianyi.debug('进入推荐车场景', user_id)
        info = TOOL_BUY_CAR[0]
        tool_descs.append(
            TOOL_DESC_BUY_CAR.format(
                name_for_model=info['name_for_model'],
                name_for_human=info['name_for_human'],
                description_for_model=info['description_for_model'],
                parameters=json.dumps(info['parameters'], ensure_ascii=False),
            )
        )
        tool_names.append(info['name_for_model'])

        tool_descs = '\n\n'.join(tool_descs)
        tool_names = ','.join(tool_names)

        prompt = REACT_PROMPT_BUY_CAR.format(tool_descs=tool_descs, tool_names=tool_names, query=query)
        return prompt
    elif "used_car_valuation" == already_known_user['scene']:
        print('进入二手车估值场景')
        logging_xianyi.debug('进入二手车估值场景', user_id)
        info = TOOL_USED_CAR_VALUATION[0]
        tool_descs.append(
            TOOL_DESC_USED_CAR_VALUATION.format(
                name_for_model=info['name_for_model'],
                name_for_human=info['name_for_human'],
                description_for_model=info['description_for_model'],
                parameters=json.dumps(info['parameters'], ensure_ascii=False),
            )
        )
        tool_names.append(info['name_for_model'])

        tool_descs = '\n\n'.join(tool_descs)
        tool_names = ','.join(tool_names)

        prompt = REACT_PROMPT_USED_CAR_VALUATION.format(tool_descs=tool_descs, tool_names=tool_names, query=query)
        return prompt
    elif "the_car_appointment" == already_known_user['scene']:
        print('进入预约场景')
        logging_xianyi.debug('进入预约场景', user_id)
        info = TOOL_THE_CAR_APPOINTMENT[0]
        formatted_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tool_descs.append(
            TOOL_DESC_THE_CAR_APPOINTMENT.format(
                name_for_model=info['name_for_model'],
                name_for_human=info['name_for_human'],
                description_for_model=info['description_for_model'].format(time=formatted_time),
                parameters=json.dumps(info['parameters'], ensure_ascii=False),
            )
        )
        tool_names.append(info['name_for_model'])

        tool_descs = '\n\n'.join(tool_descs)
        tool_names = ','.join(tool_names)
        prompt = REACT_PROMPT_THE_CAR_APPOINTMENT.format(tool_descs=tool_descs, tool_names=tool_names, query=query)
        return prompt
    elif "vehicle_issues" == already_known_user['scene']:
        print('进入汽车相关问题场景')
        logging_xianyi.debug('进入汽车相关问题场景', user_id)
        info = TOOL_VEHICLE_ISSUES[0]
        tool_descs.append(
            TOOL_DESC_VEHICLE_ISSUES.format(
                name_for_model=info['name_for_model'],
                name_for_human=info['name_for_human'],
                description_for_model=info['description_for_model'],
                parameters=json.dumps(info['parameters'], ensure_ascii=False),
            )
        )
        tool_names.append(info['name_for_model'])

        tool_descs = '\n\n'.join(tool_descs)
        tool_names = ','.join(tool_names)

        prompt = REACT_PROMPT_VEHICLE_ISSUES.format(tool_descs=tool_descs, tool_names=tool_names, query=query)
        return prompt
    elif 'what_scenes' == already_known_user['scene']:
        print('进入功能范围场景')
        logging_xianyi.debug('进入功能范围场景', user_id)
        info = TOOL_WHAT_SCENES[0]
        tool_descs.append(
            TOOL_DESC_WHAT_SCENES.format(
                name_for_model=info['name_for_model'],
                name_for_human=info['name_for_human'],
                description_for_model=info['description_for_model'],
                parameters=json.dumps(info['parameters'], ensure_ascii=False),
            )
        )
        tool_names.append(info['name_for_model'])

        tool_descs = '\n\n'.join(tool_descs)
        tool_names = ','.join(tool_names)

        prompt = REACT_PROMPT_WHAT_SCENES.format(tool_descs=tool_descs, tool_names=tool_names, query=query)
        return prompt
    elif 'search_web' == already_known_user['scene']:
        print('进入查询搜索引擎场景')
        logging_xianyi.debug('进入查询搜索引擎场景', user_id)
        info = TOOL_SEARCH_WEB[0]
        tool_descs.append(
            TOOL_DESC_SEARCH_WEB.format(
                name_for_model=info['name_for_model'],
                name_for_human=info['name_for_human'],
                description_for_model=info['description_for_model'],
                parameters=json.dumps(info['parameters'], ensure_ascii=False),
            )
        )
        tool_names.append(info['name_for_model'])

        tool_descs = '\n\n'.join(tool_descs)
        tool_names = ','.join(tool_names)

        prompt = REACT_PROMPT_SEARCH_WEB.format(tool_descs=tool_descs, tool_names=tool_names, query=query)
        return prompt
    elif 'no_scene' == already_known_user['scene']:
        print('进入无场景问答')
        logging_xianyi.debug('进入无场景问答', user_id)
        prompt = REACT_PROMPT_NO_SCENE.format(query=query)
        return prompt


def use_api(response, already_known_user, user_id, question=None, original_question=None):
    use_toolname, action_input = parse_latest_plugin_call(response)
    use_toolname = already_known_user['scene']
    if "name" == already_known_user['scene']:
        used_tool_meta = list(filter(lambda x: x["name_for_model"] == use_toolname, TOOL_NAME))
    elif "buy_car" == already_known_user['scene']:
        used_tool_meta = list(filter(lambda x: x["name_for_model"] == use_toolname, TOOL_BUY_CAR))
    elif "used_car_valuation" == already_known_user['scene']:
        used_tool_meta = list(filter(lambda x: x["name_for_model"] == use_toolname, TOOL_USED_CAR_VALUATION))
    elif "vehicle_issues" == already_known_user['scene']:
        used_tool_meta = list(filter(lambda x: x["name_for_model"] == use_toolname, TOOL_VEHICLE_ISSUES))
    elif "the_car_appointment" == already_known_user['scene']:
        used_tool_meta = list(filter(lambda x: x["name_for_model"] == use_toolname, TOOL_THE_CAR_APPOINTMENT))
    elif "what_scenes" == already_known_user['scene']:
        used_tool_meta = list(filter(lambda x: x["name_for_model"] == use_toolname, TOOL_WHAT_SCENES))
    elif "search_web" == already_known_user['scene']:
        used_tool_meta = list(filter(lambda x: x["name_for_model"] == use_toolname, TOOL_SEARCH_WEB))
    else:
        raise Exception("没这个工具：" + already_known_user['scene'])
    print('使用的工具：' + used_tool_meta[0]["name_for_model"])
    if question:
        action_input = question
    api_output, already_known_user = used_tool_meta[0]["tool_api"](action_input, already_known_user,
                                                                   user_id, original_question)
    return api_output, already_known_user


def parse_latest_plugin_call(text: str) -> Tuple[str, str]:
    i = text.rfind('\nAction:')
    j = text.rfind('\nExtracted_Json:')
    k = text.rfind('\nObservation:')
    if 0 <= i < j:  # If the text has `Action` and `Action input`,
        if k < j:  # but does not contain `Observation`,
            # then it is likely that `Observation` is ommited by the LLM,
            # because the output text may have discarded the stop word.
            text = text.rstrip() + '\nObservation:'  # Add it back.
            k = text.rfind('\nObservation:')
    if 0 <= i < j < k:
        plugin_name = text[i + len('\nAction:'):j].strip()
        plugin_args = text[j + len('\nExtracted_Json:'):k].strip()
        return plugin_name, plugin_args
    return '', ''


def build_planning_prompt_final(query, scene, Extracted_Json, api_output, user_id):
    #  ensure_ascii=False：非ascii不会被转义
    tool_descs = []
    tool_names = []
    if 'buy_car' == scene:
        info = TOOL_BUY_CAR_FINAL[0]
        tool_descs.append(
            TOOL_DESC_BUY_CAR_FINAL.format(
                name_for_model=info['name_for_model'],
                name_for_human=info['name_for_human'],
                description_for_model=info['description_for_model'],
                parameters=json.dumps(info['parameters'], ensure_ascii=False),
            )
        )
        tool_names.append(info['name_for_model'])

        tool_descs = '\n\n'.join(tool_descs)
        tool_names = ','.join(tool_names)

        prompt = REACT_PROMPT_BUY_CAR_FINAL.format(tool_descs=tool_descs, tool_names=tool_names,
                                                   query=query, Extracted_Json=Extracted_Json,
                                                   api_output=api_output)
        return prompt
    elif "used_car_valuation" == scene:
        info = TOOL_USED_CAR_VALUATION_FINAL[0]
        tool_descs.append(
            TOOL_DESC_USED_CAR_VALUATION_FINAL.format(
                name_for_model=info['name_for_model'],
                name_for_human=info['name_for_human'],
                description_for_model=info['description_for_model'],
                parameters=json.dumps(info['parameters'], ensure_ascii=False),
            )
        )
        tool_names.append(info['name_for_model'])

        tool_descs = '\n\n'.join(tool_descs)
        tool_names = ','.join(tool_names)

        prompt = REACT_PROMPT_USED_CAR_VALUATION_FINAL.format(tool_descs=tool_descs,
                                                              tool_names=tool_names, query=query,
                                                              Extracted_Json=Extracted_Json,
                                                              api_output=api_output)
        return prompt
    elif "the_car_appointment" == scene:
        info = TOOL_THE_CAR_APPOINTMENT_FINAL[0]
        tool_descs.append(
            TOOL_DESC_THE_CAR_APPOINTMENT_FINAL.format(
                name_for_model=info['name_for_model'],
                name_for_human=info['name_for_human'],
                description_for_model=info['description_for_model'],
                parameters=json.dumps(info['parameters'], ensure_ascii=False),
            )
        )
        tool_names.append(info['name_for_model'])

        tool_descs = '\n\n'.join(tool_descs)
        tool_names = ','.join(tool_names)

        prompt = REACT_PROMPT_THE_CAR_APPOINTMENT_FINAL.format(tool_descs=tool_descs, tool_names=tool_names,
                                                               query=query, Extracted_Json=Extracted_Json,
                                                               api_output=api_output)
        return prompt
    elif "vehicle_issues" == scene:
        info = TOOL_VEHICLE_ISSUES_FINAL[0]
        tool_descs.append(
            TOOL_DESC_VEHICLE_ISSUES_FINAL.format(
                name_for_model=info['name_for_model'],
                name_for_human=info['name_for_human'],
                description_for_model=info['description_for_model'],
                parameters=json.dumps(info['parameters'], ensure_ascii=False),
            )
        )
        tool_names.append(info['name_for_model'])

        tool_descs = '\n\n'.join(tool_descs)
        tool_names = ','.join(tool_names)

        prompt = REACT_PROMPT_VEHICLE_ISSUES_FINAL.format(tool_descs=tool_descs, tool_names=tool_names,
                                                          query=query, Extracted_Json=Extracted_Json,
                                                          api_output=api_output)
        return prompt


def build_planning_prompt_change_scene(query, already_known_user, user_id):
    #  ensure_ascii=False：非ascii不会被转义
    tool_descs = []
    tool_names = []
    for info in TOOLS_CHANGE_SCENE:
        tool_descs.append(
            TOOL_DESC_CHANGE_SCENE.format(
                name_for_model=info['name_for_model'],
                name_for_human=info['name_for_human'],
                description_for_model=info['description_for_model'],
            )
        )
        tool_names.append(info['name_for_model'])
    tool_descs = '\n\n'.join(tool_descs)
    tool_names = ','.join(tool_names)

    prompt = REACT_PROMPT_CHANGE_SCENE.format(tool_descs=tool_descs, tool_names=tool_names,
                                              query=query,now_scene=already_known_user['scene'])
    return prompt
