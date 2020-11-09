# -*- coding: utf-8 -*-

import os
import re
import oss2
import json
import time
import pexpect

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


def handler(event, context):
    event = json.loads(event.decode("utf-8"))

    for eveEvent in event["events"]:

        # 获取object
        print("获取object")
        code = eveEvent["oss"]["object"]["key"]
        localFileName = "/tmp/" + event["events"][0]["oss"]["object"]["eTag"]

        # 下载图片
        print("下载代码")
        print("code: ", code)
        codeBucket.get_object_to_file(code, localFileName)

        # 执行代码
        foo = pexpect.spawn('python %s' % localFileName)

        outputData = ""

        startTime = time.time()

        # timeout可以通过文件名来进行识别
        try:
            timeout = int(re.findall("timeout(.*?)s", code)[0])
        except:
            timeout = 60

        while (time.time() - startTime) / 1000 <= timeout:
            try:
                tempOutput = foo.read_nonblocking(size=999999, timeout=0.01)
                tempOutput = tempOutput.decode("utf-8", "ignore")

                if len(str(tempOutput)) > 0:
                    outputData = outputData + tempOutput

                # 输出数据存入oss
                targetBucket.put_object(code + "-output", outputData.encode("utf-8"))

            except Exception as e:

                print("Error: ", e)

                # 有输入请求被阻塞
                if str(e) == "Timeout exceeded.":

                    try:
                        # 从oss读取数据
                        targetBucket.get_object_to_file(code + "-input", localFileName + "-input")
                        with open(localFileName + "-input") as f:
                            inputData = f.read()
                        if inputData:
                            foo.sendline(inputData)
                    except:
                        pass

                # 程序执行完成输出
                elif "End Of File (EOF)" in str(e):
                    targetBucket.put_object(code + "-output", outputData.encode("utf-8"))
                    return True

                # 程序抛出异常
                else:

                    outputData = outputData + "\n\nException: %s" % str(e)
                    targetBucket.put_object(code + "-output", outputData.encode("utf-8"))

                    return False
