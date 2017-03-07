---
layout:     post
title:      "Dynamic Programming demo"
subtitle:   " \"Give me your space,I will save your time.\""
date:       2017-02-19
author:     "dusmart"
tags:
    - code
---

> "dynamic programming (also known as dynamic optimization)<br />
> is a method for solving a complex problem by breaking it down<br />
> into a collection of simpler subproblems, <br />
> solving each of those subproblems just once, <br />
> and storing their solutions – ideally"  --wikipedia

<!--more-->

---

## Problem

[Leetcode - Wildcard Matching](https://leetcode.com/problems/wildcard-matching)

Implement wildcard pattern matching with support for '?' and '\*'

'?' Matches any single character.

'\*' Matches any sequence of characters (including the empty sequence).

## Sovle it with Recursion

第一想法当然是递归咯，总共五种情况:

boolean isMatch(String s, String p) 其中s为待匹配字符串，p为匹配模式

1. s为空，p为空 --> 空串模式匹配空串true
2. s非空，p为空 --> 空串模式匹配非空串false
3. s为空，p非空 --> 非空串模式匹配空串，取决于p是否全为'\*',因为'\*'可以匹配0或任意多个字符
4. s,p都非空，p[0]=='?'或p[0]==s[0] --> 第一个字符匹配成功，取决于除第一个字符之外的模式p是否匹配除第一个字符之外的字符串s
5. s,p都非空，p[0]=='\*' --> 
    1. 当'\*'匹配0个字符时，取决于除该'\*'外的模式p是否匹配字符串s
    2. 当'\*'匹配多个字符时，取决于p是否匹配除了第一个字符外的字符串s<br />
    于是只要这两种情况有一种匹配成功，则说p匹配s成功

```
public boolean isMatch(String s, String p) {
    if(s.isEmpty()&&p.isEmpty()) return true;
    if(p.isEmpty()&&!s.isEmpty()) return false;
    if(s.isEmpty()&&!p.isEmpty()) return p.charAt(0)=='\*'&&isMatch(s,p.substring(1));
    if(p.charAt(0)=='?'||p.charAt(0)==s.charAt(0))
        return isMatch(s.substring(1),p.substring(1));
    if(p.charAt(0)=='\*') return isMatch(s.substring(1),p)||isMatch(s,p.substring(1));
    return false;
}
```

虽然逻辑没有问题，本地测试通过，但是这种递归其实在第5种情况中有运算浪费,因为isMatch(s.substring(1),p)和isMatch(s,p.substring(1))可能都会再调用isMatch(s.substring(1),p.substring(1)),于是在leetcode上提交后显示Time Limit Exceeded

## Dynamic Programming

个人感觉动态规划主要是要找准状态转移方程，之后实现起来就容易多了，在递归中讨论到的5种情况分别对应了5个状态转移方程，为了方便解释，我们把递归时讨论的"第一个字符"换成"最后一个字符"，建立2D的动归转移方程

**建立二维表bool dp[s的长度+1][p的长度+1]，其中dp[i][j]表示p的前j个字符组成的模式是否匹配s的前i个字符组成的字符串**,为了直观起见我们把5种情况画在图上：

1. 蓝色部分对应空串模式匹配空串true
2. 绿色部分对应空串模式匹配非空串false
3. 黄色部分对应非空串模式匹配空串，dp[0][j]取决于p[j]是否为'\*'以及dp[0][j-1]\(即p的前j-1个字符是否为'\*')
4. 红色部分对应s,p都非空，p[j]=='?'或p[j]==s[i]，dp[i][j]取决于最后一个字符是否匹配以及dp[i-1][j-1]\(即除最后一个字符之外的模式p是否匹配除最后一个字符之外的字符串s)
5. 黑色部分对应s,p都非空，p[j]=='\*'，dp[i][j]取决于上边和左边的结果(和上述第五种一模一样)

![img](/assets/img/2017-02-19-1.png)

![img](/assets/img/2017-02-19-2.png)

显然所有依赖关系都朝向左/上方，我们可以根据这5条规则依次计算出所有的dp[i][j]，其中dp[s.length][p.length]就是我们的最终结果

talk is cheap,show me your code
```
public static boolean isMatch(String s, String p){
    boolean[][] dp = new boolean[s.length()+1][p.length()+1];
    dp[0][0] = true;
    for (int j = 0; j < p.length(); j++)
        if(p.charAt(j)=='*' && dp[0][j]) dp[0][j+1] = true;
    for (int i = 0; i < s.length(); i++) {
        for (int j = 0; j < p.length(); j++) {
            if(s.charAt(i)==p.charAt(j) || p.charAt(j)=='?') dp[i+1][j+1] = dp[i][j];
            if(p.charAt(j)=='*') dp[i+1][j+1] = dp[i+1][j]||dp[i][j+1];
        }
    }
    return dp[s.length()][p.length()];
}
```

## Bonus Time

leetcode上的第十题[Regular Expression Matching](https://leetcode.com/problems/regular-expression-matching)比较类似，但是状态转移稍微复杂些

```
public static boolean isMatch(String s, String p) {
    boolean[][] dp = new boolean[s.length()+1][p.length()+1];
    dp[0][0] = true;
    for (int j = 0; j < p.length(); j++) {
        if(p.charAt(j)=='*' && dp[0][j-1]) dp[0][j+1] = true;
    }
    for (int i = 0; i < s.length(); i++) {
        for (int j = 0; j < p.length(); j++) {
            if(s.charAt(i)==p.charAt(j) || p.charAt(j)=='.') dp[i+1][j+1] = dp[i][j];
            if(p.charAt(j)=='*'){
                if(s.charAt(i)==p.charAt(j-1) || p.charAt(j-1)=='.')
                    dp[i+1][j+1] = dp[i][j+1] || dp[i+1][j] || dp[i+1][j-1];
                if(s.charAt(i)!=p.charAt(j-1) && p.charAt(j-1)!='.')
                    dp[i+1][j+1] = dp[i+1][j-1];
            }
        }
    }
    return dp[s.length()][p.length()];
}
```