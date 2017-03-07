---
layout:     post
title:      "Manipulating Bits"
author:     "dusmart"
tags:
    - project
    - code
---

> [CS359 Computer Architecture Project 1](/material/2017-03-07-Project1.zip)

<!--more-->

> The purpose of this project is to become familiar with bit-level representations of intergers and floating point numbers.

### Problem 1

```
/* 
 * bitAnd - x&y using only ~ and | 
 *   Example: bitAnd(6, 5) = 4
 *   Legal ops: ~ |
 *   Max ops: 8
 *   Rating: 1
 */
int bitAnd(int x, int y) {
  return ~(~x | ~y);
}
```

De Morgan law tells us: ~(x&y) == ~x \| ~y

### Problem 2

```
/* 
 * getByte - Extract byte n from word x
 *   Bytes numbered from 0 (LSB) to 3 (MSB)
 *   Examples: getByte(0x12345678,1) = 0x56
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 6
 *   Rating: 2
 */
int getByte(int x, int n) {
  int mask = 0xff;
  int shift_num = n << 3;
  int result = (x >> shift_num) & mask;
  return result;
}
```

Shift the nth byte to the right.Then use mask to get lower 8 bits.

### Problem 3

```
/* 
 * logicalShift - shift x to the right by n, using a logical shift
 *   Can assume that 0 <= n <= 31
 *   Examples: logicalShift(0x87654321,4) = 0x08765432
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 20
 *   Rating: 3 
 */
int logicalShift(int x, int n) {
  int mask = 1 << 31;
  mask = mask >> n;
  mask = mask << 1;
  x = x >> n;
  return x & (~mask);
}
```

The difference between arithmetical shift and logical shift occur when we shift a negtive number to right by n bits. By using arithmetical shift, the high (n-1) bits will be 1s while by using logical shift they are all 0s. Therefore, we cut the high (n-1) bits using a mask.

### Problem 4

```
/*
 * bitCount - returns count of number of 1's in word
 *   Examples: bitCount(5) = 2, bitCount(7) = 3
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 40
 *   Rating: 4
 */
int bitCount(int x) {
  int mask0 = (0xff << 8) + 0xff;
  int r = x & mask0;
  int l = (x >> 16) & mask0;
  int total;
  int mask1 = (0x55 << 8) + 0x55;
  int mask2 = (0x33 << 8) + 0x33;
  int mask3 = (0x0f << 8) + 0x0f;
  int mask4 = 0xff;
  l = ((l & ~mask1) >> 1) + (l & mask1);
  l = ((l & ~mask2) >> 2) + (l & mask2);
  r = ((r & ~mask1) >> 1) + (r & mask1);
  r = ((r & ~mask2) >> 2) + (r & mask2);
  total = l + r;
  total = ((total & ~mask3) >> 4) + (total & mask3);
  // (total & ~mask4) >> 8 == total >> 8, because total only has 16 bits
  total = (total            >> 8) + (total & mask4);
  return total;
}
```

The solution is like merge sort algorithm. This code is not beautiful because I want to use less operations. The algorithm should be like this. We consider every 1 bit infomation stores how many 1s in that 1 bit. Then we add every two bits and store the value in that two bits. We do the same thing two every four bits and eight bits as well as sixteen bits. Thus, after we finish doing the same operation on 32 bits,the 32 bits itself will store how many 1s in the origin 32 bits. Here we use unsigned is for logical shift.

```
unsigned bitCount(unsigned x) {
  unsigned mask1=0x55555555;
  unsigned mask2=0x33333333;
  unsigned mask3=0x0f0f0f0f;
  unsigned mask4=0x00ff00ff;
  unsigned mask5=0x0000ffff;
  x=(x+(x>>1))&mask1;
  x=(x+(x>>2))&mask2;
  x=(x+(x>>4))&mask3;
  x=(x+(x>>8))&mask4;
  x=(x+(x>>16))&mask5;
  return x;
}
```

take 0x5f307800(12 1s in it) for example:

step |             binary of x                 | how many 1s in every n bits
---- | --------------------------------------- | --------------------------------
1    | 0101 1111 0011 0000 0111 1000 0000 0000 | 01011111001100000111100000000000
2    | 0101 1010 0010 0000 0110 0100 0000 0000 |  1 1 2 2 0 2 0 0 1 2 1 0 0 0 0 0
3    | 0010 0100 0010 0000 0011 0001 0000 0000 |    2   4   2   0   3   1   0   0
4    | 0000 0110 0000 0010 0000 0100 0000 0000 |        6       2       4       0
5    | 0000 0000 0000 1000 0000 0000 0000 0100 |                8               4
6    | 0000 0000 0000 0000 0000 0000 0000 1100 |                                c

### Problem 5

```
int bang(int x) {
  // if 1 exists, move all 1s to the left bit, then shift it to 0xffffffff
  // else it will be 0 all the time
  // return the x + 1 will be just fine
  x = x | (x << 1);
  x = x | (x << 2);
  x = x | (x << 4);
  x = x | (x << 8);
  x = x | (x << 16);
  return (x >> 31) + 1;
}
```

We turn the highest bit to 1 if there exist 1 in x. Then we shift x to right by 31 bits so that it turns to -1 if there exist 1 in x. Finally, we add 1 to it so that the result is 0 if there exist 1 in x. If x is 0, it will be 1 at last apparently.

### Problem 6

```
/* 
 * tmin - return minimum two's complement integer 
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 4
 *   Rating: 1
 */
int tmin(void) {
  return (1 << 31);
}
```

The smallest number of integer is 0x80000000.

### Problem 7

```
/* 
 * fitsBits - return 1 if x can be represented as an 
 *  n-bit, two's complement integer.
 *   1 <= n <= 32
 *   Examples: fitsBits(5,3) = 0, fitsBits(-4,3) = 1
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 15
 *   Rating: 2
 */
int fitsBits(int x, int n) {
  // just consider the bits above n-1, if they're all 1's or 0's,
  // x can be represented as n bits
  // Thus, we move x left to n-1 bits, then test if it's 0 or ~0.
  int n_minus_1 = n + ~0;
  x = x >> n_minus_1;
  return !x | !(~x);
}
```





