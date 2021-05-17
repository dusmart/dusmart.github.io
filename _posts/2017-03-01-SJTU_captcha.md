---
layout:     post
title:      "Recognition of Simple Captcha"
author:     "dusmart"
tags:
    - project
    - code
---

> 交大统一身份认证页面验证码的识别，实际测试中的成功率92%-94%

<!--more-->

---

## 动机

交大几乎所有官方网站都通过一个名为JACCOUNT的认证网站认证身份，其页面中的验证码看起来很简单，自动识别的难度不大，并亲眼见到过王永强学长用C语言识别成功，于是自己在各种网络教程下写了这个验证码识别模块。

## 源码和使用方法

[https://github.com/dusmart/sjtu_captcha](https://github.com/dusmart/sjtu_captcha)

依赖：Python-Image，Python-numpy

下载源码，完整训练过程：
1. ```python 1.getImages.py```下载250张图片到./images中
2. ```python 2.slice.py```把250张图片分割为各个字符，并把字符放缩为10x10pix<sup>2</sup>
3. ```python 3.make_csv.py```人工识别每个字符存入列表，提取每个点的像素值和对应字母顺序号（1代表a，2代表b...）生成待训练数据
4. ```python 4.logistic_regression.py```通过梯度下降算法更新权值矩阵并给出在训练集上的准确率
5. ```python 5.predict ./images/100.jpg```识别命令参数中对应的图片
6. auto_elect是同学开发的通过模拟点击来刷课（交大第三轮选课）的代码，我加入了验证码识别模块，需要通过jaccount账号在第三轮选课期间使用，[自动刷课软件链接](http://zhuxinqi.space/project.html)

![img](/assets/img/2017-03-01-8.png)

## 代码分析

lib 中的 sliceImage 负责图片验证码的分割，其自左向右自上向下分别扫描出字符的边界，然后返回，这一步就成了识别成功率的瓶颈，因为有一定的不可分割字符存在

logistic_regression 负责训练权值矩阵，使用了梯度下降算法

第一步```train_x = train_x/train_x.max()```特别重要，这实质上是将属性值归一化，没有了这一步，sigmod函数中exp(-x)的值会超出float表示范围从而失败

for循环之前的语句主要是将标签转为向量，比如该字母是'c'，对应标签 **3** ,我们就将他转化为26维向量，其中第三维为 **1** ,其他为 **0** 。
从而使得regression可以将多类识别问题转化为2类识别问题。

关于for循环中的语句。首先是通过最大似然估计（对所有在输入的训练属性值x<sub>i</sub>下，得到相应标签y<sub>i</sub>的概率之积）得到 **负的cost function** ,为了使其值最大，对 **cost function** 求导得到一个梯度方向 train_x.transpose() * error， 结论十分优美，过程没法一步一步理解（矩阵求导没学过，直接搜到了结论）。
for循环的每一步都让weight向着梯度的方向下滑，参数alpha表示学习速率，其大小由经验得来。

alpha一般是这样试的--->1,0.1,0.01,0.001...

而最大迭代步数呢，我是通过打印error观察他是否已经收敛来决定是否停止的，这里的代码中直接使用5000步。

```
def trainLogRegres(train_x, old_train_y, opts):
    # calculate training time  
    startTime = time.time()

    train_x = train_x/train_x.max()
    numSamples, numFeatures = shape(train_x)
    maxValue,minValue = old_train_y.max(), old_train_y.min()
    numValues = maxValue - minValue + 1
    alpha = opts['alpha']; maxIter = opts['maxIter']
    weights = zeros([numFeatures, numValues])
    weights = random.uniform(0.001,0.002,size=[numFeatures, numValues])

    train_y = zeros([numSamples,numValues])
    for i in range(numSamples):
        train_y[i][old_train_y[i]-minValue] = 1

    for k in range(maxIter):  
        output = sigmoid(train_x * weights)
        error = train_y - output
        weights = weights + alpha * train_x.transpose() * error

    print('Took %fs!' % (time.time() - startTime))  
    return weights  
```

## 端到端的验证码识别

原理略过，可参考 cs231n 课程。[讲演稿 keynotes 下载](/assets/material/2021-03-25-captcha.key)，[除了训练集的代码和模型下载](/assets/material/2021-03-25-captcha_keras_no_traning.zip)。

## 主要参考网站
1. [COURSERA -- machine-learning](https://www.coursera.org/learn/machine-learning)
2. [机器学习算法与Python实践之（七）逻辑回归（Logistic Regression）](http://blog.csdn.net/zouxy09/article/details/20319673#)
3. [字符型验证码的分割与识别技术研究](http://www.doc88.com/p-8741957922524.html)
