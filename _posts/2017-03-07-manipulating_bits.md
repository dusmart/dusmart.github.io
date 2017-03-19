---
layout:     post
title:      "Manipulating Bits"
author:     "dusmart"
tags:
    - project
    - code
---

> [CS359 Computer Architecture Project 1](/assets/material/2017-03-07-Project1.zip)

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

The solution is like merge sort algorithm. This code is not beautiful because I want to use less operations. The algorithm should be like this. We consider every 1 bit infomation stores how many 1s in that 1 bit. Then we add every two bits and store the value in that two bits. We do the same thing to every four bits and eight bits as well as sixteen bits. Thus, after we finish doing the same operation on 32 bits,the 32 bits itself will store how many 1s in the origin 32 bits. Here we use unsigned is for logical shift.

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
1    | 0101 1111 0011 0000 0111 1000 0000 0000 | 0101111100110000 0111100000000000
2    | 0101 1010 0010 0000 0110 0100 0000 0000 |  1 1 2 2 0 2 0 0  1 2 1 0 0 0 0 0
3    | 0010 0100 0010 0000 0011 0001 0000 0000 |    2   4   2   0    3   1   0   0
4    | 0000 0110 0000 0010 0000 0100 0000 0000 |        6       2        4       0
5    | 0000 0000 0000 1000 0000 0000 0000 0100 |                8                4
6    | 0000 0000 0000 0000 0000 0000 0000 1100 |                                 12

### Problem 5

```
int bang(int x) {
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
  int n_minus_1 = n + ~0;
  x = x >> n_minus_1;
  return !x | !(~x);
}
```

X(now 32bits) is a negtive number can be represented as an n-bit twos complement integer if and only if the first (32-n+1) bits of x all are 1s. X is a positive number if and only if the first (32-n+1) bits of x all are 0s.

### Problem 8

```
int divpwr2(int x, int n) {
  int sign = (x >> 31) & 1;
  int is_left_all_0 = !!(~(~0 << n) & x);
  return (x >> n) + (sign & is_left_all_0);
}
```

If x is positive, we just shift it to right by n bits. 

If x is negtive and can be divisible by 2^n(the lower n bits are all 0s), we just shift it to right by n bits.

If x is negtive and can't be divisible by 2^n, we add 1 to it after shift it to right by n bits.

### Problem 9

```
/* 
 * negate - return -x 
 *   Example: negate(1) = -1.
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 5
 *   Rating: 2
 */
int negate(int x) {
  return ~x + 1;
}
```

This doesn't work for -2^31 because we cann't store 2^31 in a integer as two's complement.

### Problem 10

```
/* 
 * isPositive - return 1 if x > 0, return 0 otherwise 
 *   Example: isPositive(-1) = 0.
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 8
 *   Rating: 3
 */
int isPositive(int x) {
  int x_minus_1 = x + ~0;
  int sign_mask = 1 << 31;
  int sign1 = sign_mask & x;
  int sign2 = sign_mask & x_minus_1;
  int result = !(sign1 | sign2);
  return result;
}
```

We can simply identify a negtive number by its sign bit. Therefore, we consider x is not positive if and only if x negtive or x-1 is negtive.

### Problem 11

```/* 
 * isLessOrEqual - if x <= y  then return 1, else return 0 
 *   Example: isLessOrEqual(4,5) = 1.
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 24
 *   Rating: 3
 */
int isLessOrEqual(int x, int y) {
  int y_minus_x = y + (~x + 1);
  int sign_y_minus_x = (y_minus_x >> 31) & 1; // y-x >= 0
  int x_pos_y_neg = (~(x >> 31)) & (y >> 31) & 1;
  int x_neg_y_pos = (~(y >> 31)) & (x >> 31) & 1; // y+,x-
  int x_is_min = !((1 << 31) ^ x); // x = minimum
  return ((!sign_y_minus_x) & (!x_pos_y_neg)) | x_neg_y_pos | x_is_min;
}
```

1. !(x >= 0 & y < 0) & y-x >= 0 (the first condition is to avoid overflow)
2. x < = & y >= 0
3. x is the smallest number -2^31

x <= y is true if and only if one of the above is true.

### Problem 12

```
/*
 * ilog2 - return floor(log base 2 of x), where x > 0
 *   Example: ilog2(16) = 4
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 90
 *   Rating: 4
 */
int ilog2(int x) {
  int mask1 = (0x55 << 24) + (0x55 << 16) + (0x55 << 8) + 0x55;
  int mask2 = (0x33 << 24) + (0x33 << 16) + (0x33 << 8) + 0x33;
  int mask3 = (0x0f << 24) + (0x0f << 16) + (0x0f << 8) + 0x0f;
  int mask4 = (0xff << 16) + 0xff;
  int mask5 = (0xff << 8) + 0xff;
  x = x | (x >> 1);
  x = x | (x >> 2);
  x = x | (x >> 4);
  x = x | (x >> 8);
  x = x | (x >> 16);
  x = x >> 1;
  x = ((x & ~mask1) >> 1) + (x & mask1);
  x = ((x & ~mask2) >> 2) + (x & mask2);
  x = ((x & ~mask3) >> 4) + (x & mask3);
  x = ((x & ~mask4) >> 8) + (x & mask4);
  x = (x  >> 16) + (x & mask5);
  return x;
}
```

Find the highest 1 in the x. The number of bits right to it will be the answer.

We use the same operation as Problem 5 to set all bits that lower than the highest 1 to be 1s. Then we count the number of 1s in x the same as problem 4.

We shift x to right by 1 bit in the middle.Because the number of 1s in x is larger than result. What's important, code still works in this way if x is 0(none 1 in x).

### the IEEE 754 float example

![img](/assets/img/2017-03-07-1.png)

sign = +1<br>
exponent = (-127) + 124 = -3<br>
fraction = 1 + 2<sup>-2</sup> = 1.25<br>
value = +0.15625

exponent | fraction | type
-------- | -------- | ----
0        | 0        | 0
0        | not 0    | Denormalized number
1~254    | arbitrary| float
255      | 0        | infinity
255      | not 0    | NAN



### Problem 13

```
/* 
 * float_neg - Return bit-level equivalent of expression -f for
 *   floating point argument f.
 *   Both the argument and result are passed as unsigned int's, but
 *   they are to be interpreted as the bit-level representations of
 *   single-precision floating point values.
 *   When argument is NaN, return argument.
 *   Legal ops: Any integer/unsigned operations incl. ||, &&. also if, while
 *   Max ops: 10
 *   Rating: 2
 */
unsigned float_neg(unsigned uf) {
  unsigned mask = 0xff000000;
  unsigned newuf = uf << 1;
  if(!((mask & newuf) ^ mask) && (newuf ^ mask)) return uf;
  return (1 << 31) ^ uf;
}
```

If it's NAN, we output it. Else we give the opposite number.

### Problem 14

```
/* 
 * float_i2f - Return bit-level equivalent of expression (float) x
 *   Result is returned as unsigned int, but
 *   it is to be interpreted as the bit-level representation of a
 *   single-precision floating point values.
 *   Legal ops: Any integer/unsigned operations incl. ||, &&. also if, while
 *   Max ops: 30
 *   Rating: 4
 */
unsigned float_i2f(int x) {
  unsigned pos_x = x;
  unsigned shift_left = 0;
  unsigned carry = 0;
  unsigned sign = x & 0x80000000;
  if(!x) return 0;
  if(!(x ^ 0x80000000)) return 0xcf000000;
  if(sign) pos_x = -x;
  while(!(pos_x & 0x80000000)){
    shift_left = shift_left + 1;
    pos_x = pos_x << 1;
  }
  if((pos_x & 0x00000080) && (pos_x & 0x0000007f)) carry = 1;
  if(!((pos_x & 0x000001ff) ^ 0x00000180)) carry = 1;
  pos_x = (pos_x >> 8) & 0x00ffffff;
  pos_x = pos_x + carry;
  if(pos_x & 0xff000000){
    shift_left = shift_left - 1;
    pos_x = pos_x >> 1;
  }
  return sign | ((158 - shift_left) << 23) | (pos_x & 0x007fffff);
}
```

1. if x is 0, return 0
2. if x is the smallest number, return 0xcf000000
3. if x is negtive, turn it to opposite number
    * get the fraction and exponent from x
    * judge if we need a carry
    * judge when we add the carry, if it is now 24 bits so that we need change the exponent

The point to this question is when does a float need a carry. It's hard to explain, we just show some examples. The last two examples is interesting and important. That is when the extra number is exactly 1000, we should make the number's last bit as 0 after rounding.

origin number | after rounding
------------- | --------------
1.0011001     | 1.010
1.0010110     | 1.001
1.0011000     | 1.010
1.0001000     | 1.000

### Problem 15

```
/* 
 * float_twice - Return bit-level equivalent of expression 2*f for
 *   floating point argument f.
 *   Both the argument and result are passed as unsigned int's, but
 *   they are to be interpreted as the bit-level representation of
 *   single-precision floating point values.
 *   When argument is NaN, return argument
 *   Legal ops: Any integer/unsigned operations incl. ||, &&. also if, while
 *   Max ops: 30
 *   Rating: 4
 */
unsigned float_twice(unsigned uf) {
  unsigned mask = 0xff000000;
  unsigned newuf = uf << 1;
  if(!((mask & newuf) ^ mask)) return uf;
  else if(!(mask & newuf)) return (((uf & 0x007fffff) << 1) | (0x80000000 & uf));
  else return (uf + 0x00800000);
}
```

1. if it's NAN or inf, return itself
2. if it's denormalized number, just shift frac to left by 1 bit
3. else, shift exponent to left by 1 bit

### result

![img](/assets/img/2017-03-07-2.png)