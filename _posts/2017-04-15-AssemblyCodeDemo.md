---
layout:     post
title:      "Assembly Code Demo And Loop Unrooling"
author:     "dusmart"
tags:
    - project
    - code
---

> [CS359 Computer Architecture Project 2](/assets/material/2017-04-15-Project2.zip)

<!--more-->

> The purpose of this project is to learn about the design and implementation of a pipelined Y86 processor, optimizing both it and a benchmark program to maximize performance.

### Team Member

5140309022 DuShuai dusmart@qq.com

515030910024 WangZirun 906378526@qq.com

515030910375 CaoBoheng 	451735634@qq.com

### Problem 1

This is to write and simulate three Y86 programs according to some given C codes.

There are some example Y86 assembly code in sim/y86-code. Therefore, we can learn the basic format from these things. 

1. Firstly, we push %ebp to save previous frame pointer and copy %esp to %ebp to create new frame pointer.
2. Then, we retrieve parameters from the stack.
3. After that, we translate the C code one by one thanks to [this PDF(click me)](https://www.cs.utexas.edu/~witchel/429/lectures/ISA_1.pdf).
4. Finally, we restore previous frame pointer.

Not only should be the frame pointers protected, but also some other necessary general purpose registers should be protected when we call a function. That's why we push and pop the %ebx in the recursive version of ```sum``` function.

Here is an example for recursive ```sum```.

```
int rsum_list(list_ptr ls)
{
    if (!ls)
        return 0;
    else {
        int val = ls->val;
        int rest = rsum_list(ls->next);
        return val + rest;
    }
}
```
```
Main:
	irmovl ele1,%eax	# parameter: list_ptr ls
	pushl %eax
	call Rsum		# int rsum_list(list_ptr ls)
	halt

Rsum:
	pushl %ebp
	rrmovl %esp,%ebp
	mrmovl 8(%ebp),%ecx
	pushl %ebx		# save callee's %ebx

	irmovl $0,%ebx
	subl %ecx,%ebx
	je Ret0			# if(!ls) return 0;
				# else:
	mrmovl (%ecx),%ebx	# int val = ls->val;
	mrmovl 4(%ecx),%ecx	# ecx = ls->next;
	pushl %ecx
	call Rsum		# int rest = rsum_list(ls->next);//eax = rest
	addl %ebx,%eax		# return val+rest
	jmp Exit
Ret0:
	irmovl $0,%eax		# return 0;
Exit:
	mrmovl -4(%ebp),%ebx
	rrmovl %ebp,%esp
	popl %ebp
	ret
```

### Problem 2

Our task in Part B is to extend the SEQ processor to support a new instruction: iaddl. The function of
iaddl is to add a constant value to a register.

The usage of this instruction is like this: ```iaddl $3, %eax``` which intend to increase register %eax by 3.


1. **Fetch Stage** Add this instruction to valid set. From above we can see that this instruction need to use a constant value and a register. 
2. **Decode Stage**  srcB and ALU output's destination should be the second register.
3. **Execute Stage** valA is the constant, valB is the srcB(register),  condition code should be updated because this instruction is a pure arithmetic instruction.
4. **Memory Stage** Nothing need to be changed because this instruction have nothing to do with data memory.
5. **Program Counter Update** Nothing need to be done because this instruction doesn't change the execution flow.

The changes is listed as follows.

```
dusmart@desktop:~/sim/seq$ diff seq-full.hcl old-seq-full.hcl 
```
```
110c110
< 	       IOPL, IJXX, ICALL, IRET, IPUSHL, IPOPL, IIADDL };
---
> 	       IOPL, IJXX, ICALL, IRET, IPUSHL, IPOPL };
115c115
< 		     IIRMOVL, IRMMOVL, IMRMOVL, IIADDL };
---
> 		     IIRMOVL, IRMMOVL, IMRMOVL };
119c119
< 	icode in { IIRMOVL, IRMMOVL, IMRMOVL, IJXX, ICALL, IIADDL };
---
> 	icode in { IIRMOVL, IRMMOVL, IMRMOVL, IJXX, ICALL };
132c132
< 	icode in { IOPL, IRMMOVL, IMRMOVL, IIADDL  } : rB;
---
> 	icode in { IOPL, IRMMOVL, IMRMOVL  } : rB;
140c140
< 	icode in { IIRMOVL, IOPL, IIADDL } : rB;
---
> 	icode in { IIRMOVL, IOPL} : rB;
156c156
< 	icode in { IIRMOVL, IRMMOVL, IMRMOVL, IIADDL } : valC;
---
> 	icode in { IIRMOVL, IRMMOVL, IMRMOVL } : valC;
165c165
< 		      IPUSHL, IRET, IPOPL, IIADDL } : valB;
---
> 		      IPUSHL, IRET, IPOPL } : valB;
177c177
< bool set_cc = icode in { IOPL, IIADDL };
---
> bool set_cc = icode in { IOPL };

```

### Problem 3

Our task in Part C is to modify ncopy.ys and pipe-full.hcl with the goal of making ncopy.ys
run as fast as possible.

As for pipe-full.hcl, we just add a instruction iaddl just the same as Problem2. Because we will add a constant to a register frequently.

We mainly changed the ncopy.ys itself to achieve lower CPE(cycles per element).

Loop unrolling is a program transformation that reduces the number of iterations for a loop by increasing the number of elements computed on each iteration. In this way, we can reduce the **condition branch instructions** and **source&destination address updating instructions** as well as **nop instruction from data dependency**. In every unrolled code blocks, we just need 1 condition instruction for determining whether continue copy or not. We just need 1 address updating instruction to add n*4 to the address.

Our solution is to implement several level loop unrolling including 16copy, 8copy, 4copu and 2copy and origin copy.

1. Firstly we subscribe the copy_length by 16. If it still greater than or equal to 0, we perform the unrolled 16copy then jump to the start.
2. The copy_length now is the actual length minus 16. We add 8 to it. It is actual length minus 8 now. Therefore, if it is greater than or equal to 0 we perform the unrolled 8copy add subscribe 8 to it.
3. The copy_length now is the actual length minus 8 whether it perform copy8 or not. We add 4 to it. It is actual length minus 4 now. Therefore, if it is greater than or equal to 0 we perform the unrolled 4copy add subscribe 4 to it.
4. Do 2copy and 1copy the same as step3.

```
    xorl %eax,%eax		# count = 0;

Loop16:
    iaddl $-16,%edx		# len-16 < 0?
    jl Loop8		# if so, goto 8:
# perform copy 16 blocks from source to destination
#........................................
Npos1615:
    mrmovl 60(%ebx), %esi	# read val from src...
    rmmovl %esi, 60(%ecx)	# ...and store it to dst
    andl %esi, %esi		# val <= 0?
    jle Npos1616		# if so, goto Npos:
    iaddl $1, %eax		# count++
Npos1616:
    iaddl $64, %ebx		# src++
    iaddl $64, %ecx		# dst++
    jmp Loop16

Loop8:
    iaddl $8,%edx		# len-8 < 0?
    jl Loop4		# if so, goto 4
#perform copy 8 blocks from source to destination
#........................................
Npos88:
    iaddl $32, %ebx		# src++
    iaddl $32, %ecx		# dst++
    iaddl $-8,%edx

Loop4:
#........................................
Loop2:
#........................................
Loop1:
    iaddl $1,%edx		# len-1 < 0?
    jl Done			# if so, goto 16:

    mrmovl (%ebx), %esi	# read val from src...
    rmmovl %esi, (%ecx)	# ...and store it to dst
    andl %esi, %esi		# val <= 0?
    jle Npos11		# if so, goto Npos:
    iaddl $1, %eax		# count++
Npos11:
    iaddl $4, %ebx		# src++
    iaddl $4, %ecx		# dst++
    iaddl $-1,%edx
```

But after doing this, we still didn't get 60.0/60.0 scores. After 1 day, we discover that there are some extra code in it.
1. the last address updating is unnecessary. We can directly jump to ```Done``` blocks.
```
Loop1:
    iaddl $1,%edx		# len-1 < 0?
    jl Done	
    mrmovl (%ebx), %esi	# read val from src...
    rmmovl %esi, (%ecx)	# ...and store it to dst
    andl %esi, %esi		# val <= 0?
    jle Done		# if so, goto Done
    iaddl $1, %eax		# count++
```
2. the Loop16 could reduce 1 jump isntruction by rearrange the code like this.
```
Loop16:
    iaddl $-16,%edx		# len-16 < 0?
    jl Loop8		# if so, goto 8:
# perform copy 16 blocks from source to destination
#........................................
Npos1615:
    mrmovl 60(%ebx), %esi	# read val from src...
    rmmovl %esi, 60(%ecx)	# ...and store it to dst
    iaddl $64, %ebx		# src++
    iaddl $64, %ecx		# dst++
    andl %esi, %esi		# val <= 0?
    jle Loop16		# if so, goto Loop16 directly
    iaddl $1, %eax		# count++
Npos1616:
    jmp Loop16
```
3. Reading two value from source at the same time, then writing two to destination at the same time could reduce data dependence. We didn't do this because the first two method had reached the 10.0 PCE. Still we tried this way, it indeed reduces the PCE.

### Result

![img](/assets/img/2017-04-15-1.png)

Figure 1: Test result for psim with extensive regression

![img](/assets/img/2017-04-15-2.png)

Figure 2: Test result for correctness

![img jjjjjfdlskjsal](/assets/img/2017-04-15-3.png)

Figure 3: Score for ncopy.ys