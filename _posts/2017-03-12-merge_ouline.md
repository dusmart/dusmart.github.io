---
layout:     post
title:      "Algorithm Project2 -- Merge Outline"
author:     "dusmart"
tags:
    - project
---

> A simple O(nlogn) algorithm

<!--more-->

---

### Problem
给定城市里几座矩形建筑的外形和位置，利用分治法求出这些建筑的(两维)轮廓，并消去隐藏线。建筑Bi通过三元组(Li，Hi，Ri)来表示。Li和Ri分别表示建筑的左右x坐标，而Hi表示建筑的高度。一个轮廓是一列x坐标以及与它们相连的高度，按照从左到右排列。要求从输入文件in.dat读入建筑数目和各个三元组，结果写入文件out.dat。
### Solution
创建递归函数merge(structure)
其中structure为多个建筑轮廓的数组，比如[[1,11,5],[2,6,7],[3,13,9],[12,7,16]]
返回值为总的structure,对应上一行的例子，如[1, 11, 3, 13, 9, 0, 12, 7, 16, 0]
其中若structure只有一个元素，给他末尾添加上一个0，从而使所有单个的structure都有这样的形式：[x1,height_of_x1,x2,height_of_x2, ... ,xn,height_of_xn]
函数merge把输入的structure分为两部分，分别合并为一个structure之后，对他们进行合并
合并时需要把左边的structure和右边的structure分别扫描一遍，复杂度为Θ(n)
于是T(n) = 2T(n/2) + Θ(n)， 总体复杂度为Θ(nlogn)


```python
# the example from book(算法引论：一种创造性方法 Chapter5 Lesson6)
import matplotlib.pyplot as plt
origin_structure = [[1,11,5],[2,6,7],[3,13,9],[12,7,16],[14,3,25],[19,18,22],[23,13,29],[24,4,28]]
plt.plot([1,29],[0,0])
for i in origin_structure:
    plt.plot([i[0],i[0],i[2],i[2]],[0,i[1],i[1],0])
plt.show()
final_structure = merge(origin_structure)
plt.plot([1,29],[0,0])
final_x=[]
final_y=[0]
for i in range(0,len(final_structure),2):
    final_x.append(final_structure[i])
    final_x.append(final_structure[i])
    final_y.append(final_structure[i+1])
    final_y.append(final_structure[i+1])
final_y = final_y[:-1]
plt.plot(final_x,final_y)
plt.show()
```


![img](/assets/img/2017-03-12-1.png)

![img](/assets/img/2017-03-12-2.png)



```python
def merge(structure):
    if len(structure) == 1:
        # to make every structure looks like this [x1,height(x1),x2,height(x2),...,xn,height(xn)]
        structure[0].append(0)
        return structure[0]
    middle = len(structure)//2
    left = merge(structure[:middle])
    right = merge(structure[middle:])
    # put every x in left and right to the result and generate the height for them
    i, j = 0, 0
    result = []
    while(i<len(left) and j<len(right)):
        result.append(left[i])
        if(j>1 and left[i+1] < right[j-1]):
            result.append(right[j-1])
        else:
            result.append(left[i+1])
        while(i+2<len(left) and j<len(right) and right[j]<left[i+2]):
            result.append(right[j])
            if(right[j+1] < left[i+1]):
                result.append(left[i+1])
            else:
                result.append(right[j+1])
            j += 2
        i += 2
    while(i<len(left)):
        result.append(left[i])
        i += 1
    while(j<len(right)):
        result.append(right[j])
        j += 1
    # throw out those extra feature, eg. [1,11,2,11,3,0] --> [1,11,3,0]
    final = [result[0],result[1]]
    i = 2
    while(i<len(result)):
        if(result[i+1]!=final[-1]):
            final.append(result[i])
            final.append(result[i+1])
        i += 2
    return final
```


```python
def main():
    # read from a file(in.dat), write the final answer to a file(out.dat)
    with open("./in.dat", 'r') as fin:
        # the test file "./in.dat" looks like this
        #2
        #1 1 4
        #3 3 6
        with open("./out.dat", 'w') as fout:
            num = int(fin.readline().strip())
            origin_structure = []
            for i in range(num):
                x1, height, x2 = fin.readline().strip().split(' ')
                origin_structure.append([int(x1),int(height),int(x2)])
            origin_structure.sort(key = lambda obj:obj[0], reverse=False)
            final_structure = merge(origin_structure)[:-1]# throw out the last 0
            print(final_structure)
            for i in final_structure:
                fout.write(str(i)+'\n')
if __name__ == "__main__":
    main()
```