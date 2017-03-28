---
layout:     post
title:      "Find K Smallest Numbers"
author:     "dusmart"
tags:
    - project
---

> Several solutions for finding k smallest numbers from an unsorted list whose length is n.

<!--more-->

---

### Problem

从长度为n的无序数组list中找出k个最小的数，这k个数的顺序不做规定。因为如果需要最后结果是有序的而返回的k个数是无序的，只需要对输出结果排序即可。

另外，我们可以假设k < n/2,否则我们可以把题目改为找出前n-k个最大数的等价题目。

```
输入 长度为n的数组list，正整数k
输出 长度为k的数组result，存储数组list中最小的k个数
```

### Solutions

solution                | 结果有序时的时间复杂度             | 空间复杂度
----------------------- | ------------------------------- | ---------
计数排序 有限制条件        | O(y),y为取值范围                 | O(y)
全体排序                 | 取决于排序的复杂度                 | 同排序的复杂度
改编选择排序=改编冒泡排序   | O(k\*n)                        |  O(1)
改编堆排序一              | O(nlogk)                        | O(k)
改编堆排序二              | O(n+klogn)                      | O(n)
改编快速排序一             | 平均O(n+klogk)，最坏O(k*n)       | O(1)
BFPRT 改编快速排序二       | O(n+klogk)                      | O(n)

#### Solution 1 对n个数有限制条件的情况，计数排序

若已知n个数落在一定的范围内，即x <= list[i] < x+y对任意0 <= i < n成立，可以用计数排序对整个数组排序后返回前k个数。最终返回的结果是有序的。时间复杂度和空间复杂度都为O(y),y是这n个数分布的区间长度。

```
result[k];
count[y];
for i = 0 to y-1 do: count[i] = 0;
for j = 0 to list.length do: count[list[i]-x] += 1;
i = 0;
j = 0;
while i<k do:
    if count[j] > 0 then: 
        for index = 1 to count[j] do:
            result[i] = j + x;
            i += 1;
    j += 1;
```

#### Solution 2 全体排序

对数组进行排序，然后输出前k个数，最终结果是有序的，复杂度取决于排序算法。

```
result[k];
sort(list);
result = list[0:k];
```

#### Solution 3 由选择/冒泡排序改编

由于我们只需要找出前k个最小数，所以完全不必像Solution 2一样对后n-k个数进行排序，因此对选择排序法改进得到如下算法。

依次找出数组中最小的数，把他在list中删除并加入到result中，重复k次。最终结果是有序的。时间复杂度为k\*O(n)=O(k*n)。空间复杂度为O(1)。

同理，也可以由冒泡排序算法改编，只进行k次向左的冒泡。

```
result[k];
for i = 0 to k-1 do:
    min_index = 0;
    for j = 1 to list.length-1 do:
        if list[j] < list[min_index] then:
            min_index = j;
    result[i] = list[min_index];
    list[min_index] = Integer.MAXIMUM;
```

#### Solution 4 由堆排序改编 v1

由于Solution 3中由选择排序改进的算法中，获取的每一个最小数都需要和其他所有数进行比较。而这并不是必须的，因为只要有一个数num1大于某个k个数组中的最大数num2，那么该数num1必然不在最终结果中，否则那个k个数中最大的数num2必然不在最终结果中，所以根据堆排序改进后得到如下算法。

维护一个k个元素的最大堆，不断从list中取出新的元素，如果该元素大于堆的最大值，则直接丢弃，否则丢弃堆中的最大值并插入该元素到堆中。建堆时间复杂度为O(k),堆的插入或删除操作为O(logk),最多有n-k次插入。得到无序的结果的时间复杂度为O(nlogk),空间复杂度O(k)。得到有序的结果的时间复杂度为O(nlogk)+O(klogk)=O(nlogk),空间复杂度为O(k)。实质上最后如果按顺序弹出结果，则相当于对k个数进行堆排序。

```
result[k];
heap = makeHeap(list[0:k]);//最大堆
for i = k to n-1 do:
    if list[i] < heap.top() then:
        heap.top = list[i];s
        heap.sortTop();//把堆顶向下过滤
//直接生成无序result
//result = list(heap);
或者通过堆排序生成有序result
for i = 0 to k-1 do:  
    result[i] = heap.pop();
```

#### Solution 5 由堆排序改编 v2

由于当k特别小（比如k=n/10）时，像Solution 4一样建堆并不能减少特别多的比较次数。因为大多数未入堆的数之间相互比较较少的次数便可直接排除好多不在最终结果中的数，使他们不必入堆。于是考虑直接对n个数进行建堆，然后逐个弹出前k个数。最终结果是有序的。该算法时间复杂度为O(n+klogn),空间复杂度为O(n)。

输出有序结果的Solution4的最坏情况步数为k+(n-k)logk+klogk=**k+nlogk**，Solution5的最坏情况步数为**n+klogn**。当k=n/100时，前者化简为**n/100 + nlogn - nlog100**,后者化简为**n+(nlogn)/100**。显然后者性能更好。

```
result[k];
heap = makeHeap(list);//最小堆
for i = 0 to k-1 do:
    result[i] = heap.pop();
```

#### Solution 6 由快速排序改编 v1

由于Solution5总是使结果中的k个元素变得有序，而我们并不一定需要，因此考虑快速排序的分割思想。随机抽取一个元素将数组划分为两部分，如果该元素所在位置为第k个或者第k+1个则直接返回list[0:k]。如果该元素位置s小于k，返回list[0:s+1]以及后半部分的k-s-1个最小元素。如果s大于k，则返回前s个元素中的k个最小元素。这样的话，平均每次都可以将问题规模减半，即T(n) = T(n/2) + n。该算法的平均时间复杂度为O(n),空间复杂度为O(1),最坏情况下退化为选择排序的改编算法，时间复杂度为O(k*n)，空间复杂度O(1)。如果要求有序，则最终时间复杂度需要加上O(klogk)。

```
define int[] min_k(start, end, k):
    //if(k < 0 or k > end-start) then: exit(1);
    swap(list, random(start,end), start);//随机选取这段元素中的一个交换到第一个
    i = start;
    j = end - 1;
    while (i < j) do:
        while list[i] < list[j] do:
            j--;
        swap(list, i, j);
        while list[i] < list[j] do:
            i++;
        swap(list, i, j);
    if (i == k) then: return list[start:start+k];
    else if (i < k) then: return list[start:i+1] + min_k(i+1, end,  k-i-1);
    else then: return min_k(start, i, k);
result = min_k(list, 0, list.length, k);
```

#### Solution 7 BFPRT 由快速排序改编 v2

它是由Blum、Floyd、Pratt、Rivest、Tarjan提出。该算法的思想是修改上一个算法的中间元素选取方法，提高算法在最坏情况下的时间复杂度。最坏的时间复杂度和平均时间复杂度一样，是O(n)，空间复杂度是O(n)。最终结果要求有序时时间复杂度为O(n+klogk)，空间复杂度O(n)。

该算法是将Solution6的随机选取中间数那一步改成如下步骤:
1. 将数组的n个元素划分为n/5组，除最后一组外每组5个元素，最后一组n%5个元素
2. 寻找n/5个组中的中位数
3. 对于2中找出的n/5个中位数使用原算法寻找中位数，使用该中位数作为中间元素做划分，该中位数划分的两部分中较多的一部分最多占3n/10-6个元素

因此找出无序的前k个数的时间复杂度T(n) <= T(n/5) + T(3n/10) + O(n),T(1) = O(1), T(n) = O(n)。