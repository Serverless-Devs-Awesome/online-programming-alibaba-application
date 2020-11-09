# -*- coding: utf-8 -*-

import os
import json
import uuid
import random
import subprocess

# 随机字符串
randomStr = lambda num=5: "".join(random.sample('abcdefghijklmnopqrstuvwxyz', num))


# Response
class Response:
    def __init__(self, start_response, response, errorCode=None):
        self.start = start_response
        responseBody = {
            'Error': {"Code": errorCode, "Message": response},
        } if errorCode else {
            'Response': response
        }
        # 默认增加uuid，便于后期定位
        responseBody['ResponseId'] = str(uuid.uuid1())
        print("Response: ", json.dumps(responseBody))
        self.response = json.dumps(responseBody)

    def __iter__(self):
        status = '200'
        response_headers = [('Content-type', 'application/json; charset=UTF-8')]
        self.start(status, response_headers)
        yield self.response.encode("utf-8")


def WriteCode(code, fileName):
    try:
        with open(fileName, "w") as f:
            f.write(code)
        return True
    except Exception as e:
        print(e)
        return False


def RunCode(fileName, input_data=""):
    child = subprocess.Popen("python %s" % (fileName),
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             shell=True)
    output = child.communicate(input=input_data.encode("utf-8"))
    print(output)
    return output[0].decode("utf-8")


def handler(environ, start_response):
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0
    requestBody = json.loads(environ['wsgi.input'].read(request_body_size).decode("utf-8"))

    code = requestBody.get("code", None)
    inputData = requestBody.get("input", "")
    fileName = "/tmp/" + randomStr(5)

    if code and WriteCode(code, fileName):
        output = RunCode(fileName, inputData)
        responseData = output
        # 删除代码
        os.system("rm %s" % fileName)
    else:
        responseData = "Error"

    print(responseData)

    return Response(start_response, {"result": responseData})
