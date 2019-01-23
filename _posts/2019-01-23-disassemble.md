---
layout:     post
title:      "CSAPP Lab2 Writeup"
autor:      "dusmart"
tags:
    - project
---

> This post aims to record the time YinghuiGao and I spend to solve the CSAPP Lab2. This Lab is for understanding GDB x86\_64's disassembling. We're provided with a binary executable file named *bomb*.


<!--more-->

> [This is a self-study experiment Lab from CSAPP](/assets/material/2019-01-23-bomb.tar)

> Two years have been past since I finished the first Lab of CSAPP. Actually, I've tried to do Lab2 that time. Unfortunately, after few hours' learning, I waived the experiment. Recently, I fell in love with YinghuiGao. It's she who encouraged me to pick it up again. We spent four nights on the CSAPP book and finally finished this one.

## 1. Tools used and knowledge related

Our goal is to find some magic strings as inputs of this program so that it defuses all bombs. We need to use *GDB* or some other debuggers to analyze the binary file. *Objdump* can translate it to assemble code. These two tools will be enough to do with this lab. We need to master some basic operation of GDB. We should know most of x86-64's assemble instructions and how to map C code and this language to each other.

Plus, we should also remember the common usage of every register.

![img](/assets/img/2019-01-23-2.jpg)

You can simply use IDA64 to disassemble it to C code. But this will make it very boring.



## 2. The main structure of this program

By source code of bomb.c, we can see that there are three source files used to generate the final bomb program.

1. **support.c**
    This file contains some tool functions such as `initialize_bomb` and `explode_bomb`.
2. **phases.c**
    This file contains six functions named `phase_i` (i \in [1, 7)). We should disassemble these functions and sub-functions they used to determain which argument will let the function bypass calling `explode_bomb`.
3. **bomb.c**
    Main function locates here. It calls those phases function like this:
    ```
    input = read_line();
    phase_i(input);
    phase_defused();
    ```
    Therefore, our specific task is to find six sentences feeding to the bomb file so that it won't call `explode_bomb`.


By using *objdump* with argument *-d*, we can see all functions' assemble instruction used by bomb.

## 3. Function phase\_1

We can find this assemble code from the output of *objdump*. We simply need to analyze this function to bypass calling `explode_bomb`.

```
0000000000400ee0 <phase_1>:
  400ee0:	48 83 ec 08          	sub    $0x8,%rsp
  400ee4:	be 00 24 40 00       	mov    $0x402400,%esi
  400ee9:	e8 4a 04 00 00       	callq  401338 <strings_not_equal>
  400eee:	85 c0                	test   %eax,%eax
  400ef0:	74 05                	je     400ef7 <phase_1+0x17>
  400ef2:	e8 43 05 00 00       	callq  40143a <explode_bomb>
  400ef7:	48 83 c4 08          	add    $0x8,%rsp
  400efb:	c3                   	retq   
```

The first allocate 8 bytes on stack so that this function's stack frame will take a size which is multiple of 16(8 bytes + 8 bytes return address used when calling other functions).

Actually these 8 bytes are wasted simply because GCC insist to obey a X86 guideline. This guideline tells we should let the statck frame size be a multiple of 16 bytes. This is for data alignment.

The second instruction `mov` copies a 32bit number to %esi register which are commonly used as second parameter when calling a function. Actually, when the higher 32bits of %rsi are set to 0 when this instruction are executed. 

Combined with third instruction being `call`, we know that `phase_1` calls `strings_not_equal(input, 0x402400L)`. Because %rdi is not changed, we know that the first parameter is the same as what we passed to `phase_1`. That's the first setence we input to bomb.

The fourth and fifth instructions test if the return value(often stored in %eax) is zero or not. If it is not zero, the sixth instruction will be loaded. Otherwise, it jump to seventh instruction.

We can see the sixth instruction is calling `explode_bomb`. Therefore, we should make sure the return value is 0 which equals letting input be the same as string located at 0x402400. 

By typing `file bomb` and `print (char *) 0x402400` in *gdb*'s shell, we get the first setence "**Border relations with Canada have never been better.**".

Actually we can disassemble these insturctions to C code.

```
void phase_1(char* input) {
    bool result;
    result = strings_not_equal(input, "");
    if (result)
        explode_bomb();
}
```

![img](/assets/img/2019-01-23-1.jpg)


## 4. Function phase\_2

```
0000000000400efc <phase_2>:
  400efc:	55                   	push   %rbp
  400efd:	53                   	push   %rbx
  400efe:	48 83 ec 28          	sub    $0x28,%rsp
  400f02:	48 89 e6             	mov    %rsp,%rsi
  400f05:	e8 52 05 00 00       	callq  40145c <read_six_numbers>
  400f0a:	83 3c 24 01          	cmpl   $0x1,(%rsp)
  400f0e:	74 20                	je     400f30 <phase_2+0x34>
  400f10:	e8 25 05 00 00       	callq  40143a <explode_bomb>
  400f15:	eb 19                	jmp    400f30 <phase_2+0x34>
  400f17:	8b 43 fc             	mov    -0x4(%rbx),%eax
  400f1a:	01 c0                	add    %eax,%eax
  400f1c:	39 03                	cmp    %eax,(%rbx)
  400f1e:	74 05                	je     400f25 <phase_2+0x29>
  400f20:	e8 15 05 00 00       	callq  40143a <explode_bomb>
  400f25:	48 83 c3 04          	add    $0x4,%rbx
  400f29:	48 39 eb             	cmp    %rbp,%rbx
  400f2c:	75 e9                	jne    400f17 <phase_2+0x1b>
  400f2e:	eb 0c                	jmp    400f3c <phase_2+0x40>
  400f30:	48 8d 5c 24 04       	lea    0x4(%rsp),%rbx
  400f35:	48 8d 6c 24 18       	lea    0x18(%rsp),%rbp
  400f3a:	eb db                	jmp    400f17 <phase_2+0x1b>
  400f3c:	48 83 c4 28          	add    $0x28,%rsp
  400f40:	5b                   	pop    %rbx
  400f41:	5d                   	pop    %rbp
  400f42:	c3                   	retq   
```

1. Af first it stores value of %rbp and %rbx so that it can use these two registers. These two registers should not changed by callee function. Therefore it recover these registers at last before return to caller. 
2. It allocate 0x28 bytes for using. 0x28 + 8(%rbp) + 8(%rbx) + 8(caller's return address) = 0x40. We can see it still meets the guidline of stack frame's data alignment.
3. Then stack frame's lowest address and our input are used as two parameters to function `read_six_numbers`. We can assume by convention that this function will return **true** if it extracts six numbers from our inputs and return **false** otherwise. The function will extract those numbers to our stackframe at location %rsp.
4. Next, it checks if the first number is 1. If not, bomb explods. Else, it jump to 0x400f30.
5. This is a loop. %rbp is loop variable **i**, %rbp is stop flag **n**. **i** loops from 1 to 6. if number[i] != 2\*number[i-1], bomb explodes.

Therefore, the input should be "**1 2 4 8 16 32**".

## 5. Function phase\_3

```
0000000000400f43 <phase_3>:
  400f43:	48 83 ec 18          	sub    $0x18,%rsp
  400f47:	48 8d 4c 24 0c       	lea    0xc(%rsp),%rcx
  400f4c:	48 8d 54 24 08       	lea    0x8(%rsp),%rdx
  400f51:	be cf 25 40 00       	mov    $0x4025cf,%esi
  400f56:	b8 00 00 00 00       	mov    $0x0,%eax
  400f5b:	e8 90 fc ff ff       	callq  400bf0 <__isoc99_sscanf@plt>
  400f60:	83 f8 01             	cmp    $0x1,%eax
  400f63:	7f 05                	jg     400f6a <phase_3+0x27>
  400f65:	e8 d0 04 00 00       	callq  40143a <explode_bomb>
  // from above, it parses 2 numbers from our input string
  // if parsing fails, bomb will explode, else we can go to next instruction

  // below is typical switch statement which uses a jump table
  400f6a:	83 7c 24 08 07       	cmpl   $0x7,0x8(%rsp)
  400f6f:	77 3c                	ja     400fad <phase_3+0x6a>
  // if the first number greater than 7 or less than 0, it explode
  400f71:	8b 44 24 08          	mov    0x8(%rsp),%eax
  400f75:	ff 24 c5 70 24 40 00 	jmpq   *0x402470(,%rax,8)
  400f7c:	b8 cf 00 00 00       	mov    $0xcf,%eax
  400f81:	eb 3b                	jmp    400fbe <phase_3+0x7b>
  400f83:	b8 c3 02 00 00       	mov    $0x2c3,%eax
  400f88:	eb 34                	jmp    400fbe <phase_3+0x7b>
  400f8a:	b8 00 01 00 00       	mov    $0x100,%eax
  400f8f:	eb 2d                	jmp    400fbe <phase_3+0x7b>
  400f91:	b8 85 01 00 00       	mov    $0x185,%eax
  400f96:	eb 26                	jmp    400fbe <phase_3+0x7b>
  400f98:	b8 ce 00 00 00       	mov    $0xce,%eax
  400f9d:	eb 1f                	jmp    400fbe <phase_3+0x7b>
  400f9f:	b8 aa 02 00 00       	mov    $0x2aa,%eax
  400fa4:	eb 18                	jmp    400fbe <phase_3+0x7b>
  400fa6:	b8 47 01 00 00       	mov    $0x147,%eax
  400fab:	eb 11                	jmp    400fbe <phase_3+0x7b>
  400fad:	e8 88 04 00 00       	callq  40143a <explode_bomb>
  400fb2:	b8 00 00 00 00       	mov    $0x0,%eax
  400fb7:	eb 05                	jmp    400fbe <phase_3+0x7b>
  400fb9:	b8 37 01 00 00       	mov    $0x137,%eax
  400fbe:	3b 44 24 0c          	cmp    0xc(%rsp),%eax
  400fc2:	74 05                	je     400fc9 <phase_3+0x86>
  400fc4:	e8 71 04 00 00       	callq  40143a <explode_bomb>
  400fc9:	48 83 c4 18          	add    $0x18,%rsp
  400fcd:	c3                   	retq   
```

1. Obviously, this is a multiple-cases switch statement which can be translated to jump table format.
2. We simply need to input 2 numbers, the first must be in [0, 8).
3. By typing command `x/8xg 0x402470`(print 8 64-bit number in hex style started at 0x402470) in **gdb** shell, we could get the jump table:
    ```
    (gdb) x/8xg 0x402470
    0x402470:       0x0000000000400f7c      0x0000000000400fb9
    0x402480:       0x0000000000400f83      0x0000000000400f8a
    0x402490:       0x0000000000400f91      0x0000000000400f98
    0x4024a0:       0x0000000000400f9f      0x0000000000400fa6
    ```
4. We can see that these addresses in jump table are exactly matches our 8 cases.

Therefore, there are 8 pairs answer can be fed in. eg. "**7 327**"

## 6. Function phase\_4

```
000000000040100c <phase_4>:
  40100c:	48 83 ec 18          	sub    $0x18,%rsp
  401010:	48 8d 4c 24 0c       	lea    0xc(%rsp),%rcx
  401015:	48 8d 54 24 08       	lea    0x8(%rsp),%rdx
  40101a:	be cf 25 40 00       	mov    $0x4025cf,%esi
  40101f:	b8 00 00 00 00       	mov    $0x0,%eax
  401024:	e8 c7 fb ff ff       	callq  400bf0 <__isoc99_sscanf@plt>
  401029:	83 f8 02             	cmp    $0x2,%eax
  40102c:	75 07                	jne    401035 <phase_4+0x29>
  // from above, it parses 2 numbers from our input string
  // if parsing fails, bomb will explode, else we can go to next instruction

  40102e:	83 7c 24 08 0e       	cmpl   $0xe,0x8(%rsp)
  401033:	76 05                	jbe    40103a <phase_4+0x2e>
  401035:	e8 00 04 00 00       	callq  40143a <explode_bomb>
  40103a:	ba 0e 00 00 00       	mov    $0xe,%edx
  40103f:	be 00 00 00 00       	mov    $0x0,%esi
  401044:	8b 7c 24 08          	mov    0x8(%rsp),%edi
  401048:	e8 81 ff ff ff       	callq  400fce <func4>
  40104d:	85 c0                	test   %eax,%eax
  40104f:	75 07                	jne    401058 <phase_4+0x4c> 
  // return value must be 0
  401051:	83 7c 24 0c 00       	cmpl   $0x0,0xc(%rsp)
  401056:	74 05                	je     40105d <phase_4+0x51>
  // the first number must be 0
  401058:	e8 dd 03 00 00       	callq  40143a <explode_bomb>
  40105d:	48 83 c4 18          	add    $0x18,%rsp
  401061:	c3                   	retq   
```

1. At first, it extrats two numbers just like `phase_3`.
2. The first number should be less that or equal to 0xe and be positive. Otherwise, it explodes at 0x401035.
3. Then, it call `func4` with parameters (first\_number, 0, 0xe). What's more, it explodes if returned value is not 0.
4. If the second number is not 0, it also explodes.

So, we should go deep into `func4`.

```
0000000000400fce <func4>:
  400fce:	48 83 ec 08          	sub    $0x8,%rsp
  400fd2:	89 d0                	mov    %edx,%eax            # tmp = param3
  400fd4:	29 f0                	sub    %esi,%eax            # tmp -= param2
  400fd6:	89 c1                	mov    %eax,%ecx
  400fd8:	c1 e9 1f             	shr    $0x1f,%ecx           # sign = tmp >> 31, is 0 because tmp is positive
  400fdb:	01 c8                	add    %ecx,%eax            # tmp += sign (no effect)
  400fdd:	d1 f8                	sar    %eax                 # tmp /= 2
  400fdf:	8d 0c 30             	lea    (%rax,%rsi,1),%ecx   # mid = tmp + param2
  400fe2:	39 f9                	cmp    %edi,%ecx            # if mid > param1
  400fe4:	7e 0c                	jle    400ff2 <func4+0x24>
  400fe6:	8d 51 ff             	lea    -0x1(%rcx),%edx      #   new_param3 = mid - 1
  400fe9:	e8 e0 ff ff ff       	callq  400fce <func4>       #   result = func4(param1, param2, new_param3)
  400fee:	01 c0                	add    %eax,%eax            #   return 2 * result
  400ff0:	eb 15                	jmp    401007 <func4+0x39>
  400ff2:	b8 00 00 00 00       	mov    $0x0,%eax            # reuslt = 0
  400ff7:	39 f9                	cmp    %edi,%ecx            # if mid < param1
  400ff9:	7d 0c                	jge    401007 <func4+0x39>
  400ffb:	8d 71 01             	lea    0x1(%rcx),%esi       #   new_param2 = mid + 1
  400ffe:	e8 cb ff ff ff       	callq  400fce <func4>       #   result = func4(param1, new_param2, param3)
  401003:	8d 44 00 01          	lea    0x1(%rax,%rax,1),%eax#   result = 2 * result + 1
  401007:	48 83 c4 08          	add    $0x8,%rsp
  40100b:	c3                   	retq   
```

1. This is a recursive function with three branches in its body.
    1. return 0 if param1 = mid (mid is the middle number of param2 and param3)
    2. return 2 * func4(param1, param2, mid - 1) if param1 < mid
    3. return 2 * func4(param1, mid + 1, param3) + 1 if param1 > mid
2. The `phase_4` should let func4(first\_number, 0, 14) be zero. So first\_number can be 0, 3 and 7.

Therefore, the answer can be "**0 0**" or "**3 0**" or "**7 0**".

## 7. Function phase\_5

```
0000000000401062 <phase_5>:
  401062:	53                   	push   %rbx
  401063:	48 83 ec 20          	sub    $0x20,%rsp
  401067:	48 89 fb             	mov    %rdi,%rbx
  // A random value is inserted to avoid stack overflow attacking.
  40106a:	64 48 8b 04 25 28 00 	mov    %fs:0x28,%rax
  401071:	00 00 
  401073:	48 89 44 24 18       	mov    %rax,0x18(%rsp)
  401078:	31 c0                	xor    %eax,%eax
  40107a:	e8 9c 02 00 00       	callq  40131b <string_length>
  40107f:	83 f8 06             	cmp    $0x6,%eax
  401082:	74 4e                	je     4010d2 <phase_5+0x70>
  401084:	e8 b1 03 00 00       	callq  40143a <explode_bomb>
  // if our intput length is not 6, bomb will explode, else we can go to next instruction
  401089:	eb 47                	jmp    4010d2 <phase_5+0x70>

  // This is a loop. 
  40108b:	0f b6 0c 03          	movzbl (%rbx,%rax,1),%ecx   # ch = input[i]
  40108f:	88 0c 24             	mov    %cl,(%rsp)           # 
  401092:	48 8b 14 24          	mov    (%rsp),%rdx          # index = ch
  401096:	83 e2 0f             	and    $0xf,%edx            # index &= 0xf
  401099:	0f b6 92 b0 24 40 00 	movzbl 0x4024b0(%rdx),%edx  # tmp = array[index]
  4010a0:	88 54 04 10          	mov    %dl,0x10(%rsp,%rax,1)# des_str[i] = tmp
  4010a4:	48 83 c0 01          	add    $0x1,%rax            # i++
  4010a8:	48 83 f8 06          	cmp    $0x6,%rax            # if i != 6
  4010ac:	75 dd                	jne    40108b <phase_5+0x29>#     loop

  // Codes below compare six numbers generated by above loop and a given byte array
  4010ae:	c6 44 24 16 00       	movb   $0x0,0x16(%rsp)      # append '\0' to string end
  4010b3:	be 5e 24 40 00       	mov    $0x40245e,%esi       # "flyers"
  4010b8:	48 8d 7c 24 10       	lea    0x10(%rsp),%rdi      # des_str
  4010bd:	e8 76 02 00 00       	callq  401338 <strings_not_equal>
  4010c2:	85 c0                	test   %eax,%eax
  4010c4:	74 13                	je     4010d9 <phase_5+0x77>
  4010c6:	e8 6f 03 00 00       	callq  40143a <explode_bomb>
  4010cb:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
  4010d0:	eb 07                	jmp    4010d9 <phase_5+0x77>
  4010d2:	b8 00 00 00 00       	mov    $0x0,%eax
  4010d7:	eb b2                	jmp    40108b <phase_5+0x29>
  4010d9:	48 8b 44 24 18       	mov    0x18(%rsp),%rax
  4010de:	64 48 33 04 25 28 00 	xor    %fs:0x28,%rax
  4010e5:	00 00 
  4010e7:	74 05                	je     4010ee <phase_5+0x8c>
  4010e9:	e8 42 fa ff ff       	callq  400b30 <__stack_chk_fail@plt>
  4010ee:	48 83 c4 20          	add    $0x20,%rsp
  4010f2:	5b                   	pop    %rbx
  4010f3:	c3                   	retq   
```

1. It assures that our input length is 6. 
2. It uses our input character's less significent four bits as index to fetch a new string in a given array. By typing `print (char *) 0x4024b0` in **gdb** shell. We could see a 16-lengthed string followed by other characters. That array is "maduiersnfotvbyl".
3. Next, it compares our generated string and a literate string *flyers*(located at 0x40245e). If they are not the same, bomb explodes.
4. Therefore, our index is [9,0xf,0xe,5,6,7]. As a common sense, by adding (i-1) to 'a' or 'A', we can get a char whose lower 4 bits is i.

The answer can be "**ionefg**". And it's case insensitive. You can also use some other printable characters.


## 8. Function phase\_6

The assemble code is too hard to follow. We'd better use IDA64 to disassemble it into C code and analyze them together.

```
__int64 __fastcall phase_6(__int64 input)
{
    read_six_numbers(input, &first);

    for(int i = 1, int* it = &first; ; it++, i++)
    {
        // iterate 6 times, every number is in [1, 7)
        if ( *it - 1 < 0 || *it - 1 > 6 )
            explode_bomb();
        if ( i == 6 )
            break;
        // iterate 5 times, i \in [1, 6), every number is different
        for (int j = i; j <= 5; ++j)
        {
            if ( *it == *(&first + j) )
                explode_bomb();
        }
    }

    // every number becomes 7 - itself
    for (int* it = &first; it != &first+7; ++it)
    {
        *it = 7 - *it;
    }

    // it generated a local pointer array in stack
    // table[i] = node[input[i]]
    for (int i = 0; i != 6; i += 1)
    {
            int it_num = *(&first + i);

            int *v6 = 0x6032d0;
            if ( it_num > 1 )
                for (j = 1; j != it_num; ++j)
                {
                    v6 = v6->next;;
                }
            }
            *(&rsp_plus_0x20_value + i) = v6;
    }


    // it copies table[1] to table[0]->next
    //           table[2] to table[1]->next ......
    //           table[5] to table[4]->next
    for (it0 = rsp_plus_0x28, i = rsp_plus_0x20_number;
        it0 != rsp_plus_0x50 ;
        i = *it0, ++it0 )
    {
        *(i + 8) = *it0;
    }
    *(long *)(it2 + 8) = 0LL;


    v9 = rsp_plus_0x20_number;

    // we must assure table[i]->value >= table[i]->next->value.
    for (int i = 5; i != 0; i--)
        result = **(int **)(v9 + 8);
        if ( *(int *)v9 < (signed int)result )
            explode_bomb();
        v9 = *(long *)(v9 + 8);
    }

    return result;
}
```

After modify the C code generated by IDA64. We could get some pseudocode above.

1. Six numbers is loaded to a local int array.
2. Every number should be in [1, 7) and differ from each other.
3. Every number becomes 7 - itself.
4. By giving an address of a global linked list, it maps every number to a node's address and store it in a local array. Let's assume the local array's name is table.
    1. The linked list's address is 0x6032d0 told in code 0x4011a4.
    2. By typing `x/20xg 0x6032d0` in **gdb** shell. We can see that it's a 6-lengthed linked list. Every node has two int and one pointer.
    3. 
    ```
    0x6032d0 <node1>:       0x000000010000014c      0x00000000006032e0
    0x6032e0 <node2>:       0x00000002000000a8      0x00000000006032f0
    0x6032f0 <node3>:       0x000000030000039c      0x0000000000603300
    0x603300 <node4>:       0x00000004000002b3      0x0000000000603310
    0x603310 <node5>:       0x00000005000001dd      0x0000000000603320
    0x603320 <node6>:       0x00000006000001bb      0x0000000000000000
    ```
    4. So the node should be a structure like {int index; int value; node\* next}
    5. table[i] = node[input[i]] becase the linked list is node1->node2->node3->node4->node5->node6
5. It actually act like this: `table[i]->next = table[i+1]`
6. It assures table[i]->value >= table[i]->next->value. Actually, this is to assure the linked list be in a descending order. Therefore, by comparing the value of every node, we know that int step5, we should do it like this:
    1. node3->next = node4
    2. node4->next = node5
    3. node5->next = node6
    4. node6->next = node1
    5. node1->next = node2
7. Therefore, the local array table should be [node3, node4, node5, node6, node1, node2]. Combined with step4.5, we know that the input number's order should be [3,4,5,6,1,2]. By reversing step3, we got the final answer: "**4 3 2 1 6 5**"


This one is very disgusting. We can split it into pieces by jump instruction so that we can analyze every loop seperately. Below is the assemble code for reference.

```
00000000004010f4 <phase_6>:
  // store registers and parses numbers
  4010f4:	41 56                	push   %r14
  4010f6:	41 55                	push   %r13
  4010f8:	41 54                	push   %r12
  4010fa:	55                   	push   %rbp
  4010fb:	53                   	push   %rbx
  4010fc:	48 83 ec 50          	sub    $0x50,%rsp
  401100:	49 89 e5             	mov    %rsp,%r13
  401103:	48 89 e6             	mov    %rsp,%rsi
  401106:	e8 51 03 00 00       	callq  40145c <read_six_numbers>

  // i loop from 0 to 5: input[i] in [1,7) and input[i] != input[j] for every j > i
  40110b:	49 89 e6             	mov    %rsp,%r14
  40110e:	41 bc 00 00 00 00    	mov    $0x0,%r12d
  401114:	4c 89 ed             	mov    %r13,%rbp
  401117:	41 8b 45 00          	mov    0x0(%r13),%eax
  40111b:	83 e8 01             	sub    $0x1,%eax
  40111e:	83 f8 05             	cmp    $0x5,%eax
  401121:	76 05                	jbe    401128 <phase_6+0x34>
  401123:	e8 12 03 00 00       	callq  40143a <explode_bomb>
  401128:	41 83 c4 01          	add    $0x1,%r12d
  40112c:	41 83 fc 06          	cmp    $0x6,%r12d
  401130:	74 21                	je     401153 <phase_6+0x5f>
  401132:	44 89 e3             	mov    %r12d,%ebx
  401135:	48 63 c3             	movslq %ebx,%rax
  401138:	8b 04 84             	mov    (%rsp,%rax,4),%eax
  40113b:	39 45 00             	cmp    %eax,0x0(%rbp)
  40113e:	75 05                	jne    401145 <phase_6+0x51>
  401140:	e8 f5 02 00 00       	callq  40143a <explode_bomb>
  401145:	83 c3 01             	add    $0x1,%ebx
  401148:	83 fb 05             	cmp    $0x5,%ebx
  40114b:	7e e8                	jle    401135 <phase_6+0x41>
  40114d:	49 83 c5 04          	add    $0x4,%r13
  401151:	eb c1                	jmp    401114 <phase_6+0x20>
  401153:	48 8d 74 24 18       	lea    0x18(%rsp),%rsi
  401158:	4c 89 f0             	mov    %r14,%rax
  40115b:	b9 07 00 00 00       	mov    $0x7,%ecx
  401160:	89 ca                	mov    %ecx,%edx
  401162:	2b 10                	sub    (%rax),%edx
  401164:	89 10                	mov    %edx,(%rax)
  401166:	48 83 c0 04          	add    $0x4,%rax
  40116a:	48 39 f0             	cmp    %rsi,%rax
  40116d:	75 f1                	jne    401160 <phase_6+0x6c>

  // i loop from 0 to 5: table[i] = node[input[i]]
  40116f:	be 00 00 00 00       	mov    $0x0,%esi
  401174:	eb 21                	jmp    401197 <phase_6+0xa3>
  401176:	48 8b 52 08          	mov    0x8(%rdx),%rdx
  40117a:	83 c0 01             	add    $0x1,%eax
  40117d:	39 c8                	cmp    %ecx,%eax
  40117f:	75 f5                	jne    401176 <phase_6+0x82>
  401181:	eb 05                	jmp    401188 <phase_6+0x94>
  401183:	ba d0 32 60 00       	mov    $0x6032d0,%edx
  401188:	48 89 54 74 20       	mov    %rdx,0x20(%rsp,%rsi,2)
  40118d:	48 83 c6 04          	add    $0x4,%rsi
  401191:	48 83 fe 18          	cmp    $0x18,%rsi
  401195:	74 14                	je     4011ab <phase_6+0xb7>
  401197:	8b 0c 34             	mov    (%rsp,%rsi,1),%ecx
  40119a:	83 f9 01             	cmp    $0x1,%ecx
  40119d:	7e e4                	jle    401183 <phase_6+0x8f>
  40119f:	b8 01 00 00 00       	mov    $0x1,%eax
  4011a4:	ba d0 32 60 00       	mov    $0x6032d0,%edx
  4011a9:	eb cb                	jmp    401176 <phase_6+0x82>

  // i loop from 0 to 4: table[i]->next = table[i+1]
  4011ab:	48 8b 5c 24 20       	mov    0x20(%rsp),%rbx
  4011b0:	48 8d 44 24 28       	lea    0x28(%rsp),%rax
  4011b5:	48 8d 74 24 50       	lea    0x50(%rsp),%rsi
  4011ba:	48 89 d9             	mov    %rbx,%rcx
  4011bd:	48 8b 10             	mov    (%rax),%rdx
  4011c0:	48 89 51 08          	mov    %rdx,0x8(%rcx)
  4011c4:	48 83 c0 08          	add    $0x8,%rax
  4011c8:	48 39 f0             	cmp    %rsi,%rax
  4011cb:	74 05                	je     4011d2 <phase_6+0xde>
  4011cd:	48 89 d1             	mov    %rdx,%rcx
  4011d0:	eb eb                	jmp    4011bd <phase_6+0xc9>

  // i loop from 0 to 5: assure table[i]->value > table[i]->next->value
  4011d2:	48 c7 42 08 00 00 00 	movq   $0x0,0x8(%rdx)
  4011d9:	00 
  4011da:	bd 05 00 00 00       	mov    $0x5,%ebp
  4011df:	48 8b 43 08          	mov    0x8(%rbx),%rax
  4011e3:	8b 00                	mov    (%rax),%eax
  4011e5:	39 03                	cmp    %eax,(%rbx)
  4011e7:	7d 05                	jge    4011ee <phase_6+0xfa>
  4011e9:	e8 4c 02 00 00       	callq  40143a <explode_bomb>
  4011ee:	48 8b 5b 08          	mov    0x8(%rbx),%rbx
  4011f2:	83 ed 01             	sub    $0x1,%ebp
  4011f5:	75 e8                	jne    4011df <phase_6+0xeb>

  // restore registers and stack
  4011f7:	48 83 c4 50          	add    $0x50,%rsp
  4011fb:	5b                   	pop    %rbx
  4011fc:	5d                   	pop    %rbp
  4011fd:	41 5c                	pop    %r12
  4011ff:	41 5d                	pop    %r13
  401201:	41 5e                	pop    %r14
  401203:	c3                   	retq   
```
