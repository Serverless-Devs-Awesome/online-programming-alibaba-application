# -*- coding: utf-8 -*-

import os
import oss2
import json
import uuid
import random

# 基本配置信息
AccessKey = {
    "id": os.environ.get('AccessKeyId'),
    "secret": os.environ.get('AccessKeySecret')
}

OSSCodeConf = {
    'endPoint': os.environ.get('OSSConfEndPoint'),
    'bucketName': os.environ.get('OSSConfBucketCodeName'),
    'objectSignUrlTimeOut': int(os.environ.get('OSSConfObjectSignUrlTimeOut'))
}

OSSTargetConf = {
    'endPoint': os.environ.get('OSSConfEndPoint'),
    'bucketName': os.environ.get('OSSConfBucketTargetName'),
    'objectSignUrlTimeOut': int(os.environ.get('OSSConfObjectSignUrlTimeOut'))
}

# 获取获取/上传文件到OSS的临时地址
auth = oss2.Auth(AccessKey['id'], AccessKey['secret'])
codeBucket = oss2.Bucket(auth, OSSCodeConf['endPoint'], OSSCodeConf['bucketName'])
targetBucket = oss2.Bucket(auth, OSSTargetConf['endPoint'], OSSTargetConf['bucketName'])

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


def handler(environ, start_response):
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0
    requestBody = json.loads(environ['wsgi.input'].read(request_body_size).decode("utf-8"))

    reqType = requestBody.get("type", None)

    if reqType == "run":
        # 运行代码
        code = requestBody.get("code", None)
        runId = randomStr(10)
        codeBucket.put_object(runId, code.encode("utf-8"))
        responseData = runId
    elif reqType == "input":
        # 输入内容
        inputData = requestBody.get("input", None)
        runId = requestBody.get("id", None)
        targetBucket.put_object(runId + "-input", inputData.encode("utf-8"))
        responseData = 'ok'
    elif reqType == "output":
        # 获取结果
        runId = requestBody.get("id", None)
        targetBucket.get_object_to_file(runId + "-output", '/tmp/' + runId)
        with open('/tmp/' + runId) as f:
            responseData = f.read()
    else:
        responseData = "Error"

    print(responseData)

    return Response(start_response, {"result": responseData})
