# 在线编程

项目获取之后，可直接进行部署操作: `s deploy`

这其中包括两个项目：

- 项目1： 简单在线编程
    - ordinary
- 项目2： 复杂在线编程
    - main
    - compiler

## 详细介绍

### 项目1

- 可以执行Python代码
- 支持标准输入
- 可以返回标准输出和标准错误

该简单工具的整个过程包括：
![image.png](https://cdn.nlark.com/yuque/0/2020/png/2664883/1604894757494-bd5df30f-2c32-4e37-a64a-7cd00c094340.png#align=left&display=inline&height=210&margin=%5Bobject%20Object%5D&name=image.png&originHeight=420&originWidth=1656&size=127903&status=done&style=none&width=828)

### 项目2

- 可以执行Python代码
- 支持标准输入
- 可以返回标准输出和标准错误
- 可以实现流输入输出

为了减少这种体验不统一的问题，可以将代码和结构进行进一步的升级：
![image.png](https://cdn.nlark.com/yuque/0/2020/png/2664883/1604895340880-71fcf5e4-22ac-4f12-9899-fa533b89056d.png#align=left&display=inline&height=191&margin=%5Bobject%20Object%5D&name=image.png&originHeight=382&originWidth=1950&size=197591&status=done&style=none&width=975)
在整个项目中，包括了两个函数，两个存储桶：

- 业务逻辑函数：该函数的主要操作是业务逻辑，包括创建代码执行的任务（通过对象存储触发器进行异步函数执行），以及获取函数输出结果以及对任务函数的标准输入进行相关操作等；
- 执行器函数：该函数的主要作用是执行用户的函数代码，这部分是通过对象存储触发，通过下载代码、执行代码、获取输入、输出结果等；代码获取从代码存储桶，输出结果和获取输入从业务存储桶；
- 代码存储桶：该存储桶的作用是存储代码，当用户发起运行代码的请求， 业务逻辑函数收到用户代码后，会将代码存储到该存储桶，再由该存储桶处罚异步任务；
- 业务存储桶：该存储桶的作用是中间量的输出，主要包括输出内容的缓存、输入内容的缓存；该部分数据可以通过对象存储的本身特性进行生命周期的制定；

> 额外说明， 需要在`template.yaml`中填写自己的密钥信息，也可以将密钥信息放在环境变量，自动获取。