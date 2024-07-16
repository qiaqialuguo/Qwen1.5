import random
from http import HTTPStatus
from dashscope import Generation


def call_stream_with_messages():
    messages = [
        {'role': 'user', 'content': '你是谁'}]
    responses = Generation.call(
        'qwen1.5-72b-chat',
        messages=messages,
        seed=random.randint(1, 10000),  # set the random seed, optional, default to 1234 if not set
        result_format='message',  # set the result to be "message"  format.
        stream=True,
        api_key='sk-777003151b354aa6889b598f9ff666b4',
        output_in_full=True,  # get streaming output incrementally
    )
    full_content = ''
    for response in responses:
        if response.status_code == HTTPStatus.OK:
            full_content += response.output.choices[0]['message']['content']
            print(response)
        else:
            print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                response.request_id, response.status_code,
                response.code, response.message
            ))
    print('Full content: \n' + full_content)


def call_with_messages():
    messages = [
        {'role': 'user', 'content': '你是谁'}]
    response = Generation.call(
        'qwen1.5-72b-chat',
        messages=messages,
        # set the random seed, optional, default to 1234 if not set
        seed=random.randint(1, 10000),
        result_format='message',  # set the result to be "message" format.
        api_key='sk-777003151b354aa6889b598f9ff666b4',
    )
    if response.status_code == HTTPStatus.OK:
        print(response)
    else:
        print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
            response.request_id, response.status_code,
            response.code, response.message
        ))


if __name__ == '__main__':
    # call_stream_with_messages()
    call_with_messages()