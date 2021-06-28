# snake
一个简单的8位计算机电路图，采用哈佛架构，基于MIPS32设计指令集。

可以使用logisim打开snake.circ文件。



# 指令集

指令格式：

```
instruction dst, src [, imme8]
```



## movr reg, reg

把src寄存器的内容复制到dst中。



## movi reg, imme8

把立即数放入寄存器中。



## sw imme8(reg), reg

把src寄存器中的内容放入以src寄存器为基地址加上offset偏移量的内存单元中。



## ld reg, imme8(reg)

把以寄存器src为基地址加上一个立即数偏移的内存单元的内容放入dst寄存器中。



## add|sub|and|or reg, reg, imme8

把src寄存器中的内容加上立即数放入dst寄存器中。



## jmp label

跳转指令，跳转到label之后的指令中。



# 汇编器

提供了一个简单的汇编器，使用方法如下：

```shell
python snake_assembler.py <target file> <src file>
```

如果编译成功会生成一个二进制文件和一个以target file加上.txt结尾的文件，logisim中的ROM可以直接导入这个文件的内容。
