---
layout:     post
title:      "Python Learning Notes 2"
author:     "tinger"
tags:
    - code
---

> Python control flow tools

<!--more-->

## if语句系列

* 注意: if 语句后接表达式，然后用“:”表示代码块开始。（if语句）
* 注意: else 后面有个“:”

```
if age >= 18:
    print ‘adult'
else:
    print ‘teenager'
```

* 注意: （ if ... 多个elif ... else ...）

这一系列条件判断会从上到下依次判断，如果某个判断为 True，执行完对应的代码块，后面的条件判断就直接忽略，不再执行了。 
**此句型一定得注意判断条件的先后次序**

```
age = 8
if age >= 6:
    print 'teenager'
elif age >= 18:
    print 'adult'
else:
    print 'kid' 
```

* 注意：当age=8时，可以判断，而当age=20时，输出结果和age=8时输出结果相同，所以在这个句型中一定得注意判断条件的先后次序

当改变上面程序为以下时
```
if age >= 18:
    print 'adult'
elif age >= 6:
    print 'teenager'
else:
    print 'kid'
```
此时就不会存在上面所出现的bug。 

---

## Python之while循环

While语句用于循环执行程序，基本类型为：
      While 判断条件：
         执行语句

---

## Python之多重循环

在循环内部，还可以嵌套循环，我们来看一个例子：

for x in ['A', 'B', 'C']:
    for y in ['1', '2', '3']:
        print x + y

x 每循环一次，y 就会循环 3 次，这样，我们可以打印出一个全排列：

A1  A2  A3  B1  B2  B3  C1  C2  C3

## 补充：Python中dict的特点

1. dict的第一个特点是查找速度快，无论dict有10个元素还是10万个元素，查找速度都一样。而list的查找速度随着元素增加而逐渐下降。

2. dict的第二个特点就是存储的key-value序对是没有顺序的！这和list不一样

3. dict的第三个特点是作为 key 的元素必须不可变，Python的基本类型如字符串、整数、浮点数都是不可变的，都可以作为 key。但是list是可变的，就不能作为 key。
