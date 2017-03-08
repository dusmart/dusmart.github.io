---
layout:     post
title:      "Python Learning Notes"
date:       2017-03-02
author:     "tinger"
tags:
    - code
---

> 记Python的数据基本类型

<!--more-->

### 1. list (列表)

n 表示要进行操作的元素位置,"XXX"表示内容

1. 添加元素：
    * ```L.insert(n,"XXX")```
    * ```L.append(x)``` 把元素 x 添加到数组的尾部
2. 删除元素:
    * ```L.pop(n)``` 删除第 n 个元素，并返回这个元素
    * ```L.pop()``` 删除最后一个元素，并返回该元素
    * ```L.remove(x)``` 表示删除第一个出现的 x 元素
3. 替换元素：
    * ```L[n]="xxx"``` 对准元素位置，对此直接进行赋值
4. 排序元素：
    * ```L.sort()``` 对列表中的元素进行排序
5. 查找元素：
    * ```L.index(x)``` 返回数组中的第一个值为 x 的位置，若无匹配元素则报错

### 2. tuple (元组)

元组里的元素是有序的，不能进行改变，但是当 tuple 里边包含 list 时，此 list 里的元素是可变的。

### 3. set (集合)

1. 无序不重复元素集，基本功能包括关系测试和消除重复元素。
2. 支持```x in set```, ```len(set)``` 和 ```for x in set``` 等操作。作为一个无序的集合， set 不记录元素位置或者插入点。

* 特点： set 的内部结构和 dict 很像，唯一区别是不存储 value ，因此，判断一个元素是否在 set 中速度很快。 set 存储的元素和 dict 的 key 类似，必须是不变对象，因此，任何可变对象是不能放入set中的。

### 4. dict (字典)

* 字典是由无序的“键值对（key-value）”组成。可以简单地使用 ```d[key]``` 的形式来查找对应的 value ，这和 list 很像，不同之处是， list 必须使用索引返回对应的元素，而 dict 使用 key。

1. dict 的第一个特点是查找速度快，无论 dict 有10个元素还是10万个元素，查找速度都几乎一样。而 list 的查找速度随着元素增加而逐渐下降。不过 dict 的查找速度快不是没有代价的， dict 的缺点是占用内存大，还会浪费很多内容， list 正好相反，占用内存小，但是查找速度慢。由于 dict 是按 key 查找，所以，在一个 dict 中， key 不能重复。
2. dict 的第二个特点就是存储的 key-value 序对是没有顺序的！
3. dict 的第三个特点是作为 key 的元素必须不可变， Python 的基本类型如字符串、整数、浮点数都是不可变的，都可以作为 key 。但是 list 是可变的，就不能作为 key。