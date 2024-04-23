import json

from rag_classification.prompt.prompt_buy_car import REACT_PROMPT_BUY_CAR, TOOL_DESC_BUY_CAR, TOOL_BUY_CAR
from rag_classification.prompt.prompt_classification import TOOLS, TOOL_DESC, REACT_PROMPT
from rag_classification.prompt.prompt_no_scene import REACT_PROMPT_NO_SCENE
from rag_classification.prompt.prompt_the_car_appointment import TOOL_THE_CAR_APPOINTMENT, \
    TOOL_DESC_THE_CAR_APPOINTMENT, REACT_PROMPT_THE_CAR_APPOINTMENT
from rag_classification.prompt.prompt_used_car_valuation import REACT_PROMPT_USED_CAR_VALUATION, \
    TOOL_USED_CAR_VALUATION, TOOL_DESC_USED_CAR_VALUATION


def build_planning_prompt(query, already_known_user):
    #  ensure_ascii=False：非ascii不会被转义
    tool_descs = []
    tool_names = []
    if 'no_scene' == already_known_user['scene']:
        print('无预置场景')
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
    elif 'buy_car' == already_known_user['scene']:
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
    elif "used_car_valuation" == already_known_user['scene']:
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
    elif "the_car_appointment" == already_known_user['scene']:
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
    elif 'no_scene' == already_known_user['scene']:
        prompt = REACT_PROMPT_NO_SCENE.format(query=query)
        return prompt
