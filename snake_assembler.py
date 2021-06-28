import sys
import re
import struct

# 用于转换寄存器对应的数字
register_map = {'r0': 0, 'r1': 1, 'r2': 2, 'r3': 3, 
				'r4': 4, 'r5': 5, 'r6': 6, 'r7': 7}
# 把字符的运算操作转化为对应的操作码
calc_map = {'add': 0x0, 'sub': 0x04, 'and': 0x02, 'or': 0x0a}
# 用于记录标签的行号
label_line_map = {}
# 当前行，包括空行，注释
current_line = 0
# 指令的行号，去除空行，注释，标签行
instruction_order = 0

# movr reg, reg
def mov_reg_reg(dst, src):
	instruction = 0x80000000
	dst = register_map[dst] << 16
	src = register_map[src] << 21
	instruction |= dst
	instruction |= src
	return instruction

# movi reg, imme8
def mov_reg_imme(dst, num):
	instruction = 0x80e00000
	dst = register_map[dst] << 16
	instruction |= (num << 6)
	instruction |= dst
	return instruction

# sw imme8(reg), reg
def sw_mem_reg(offset, base, src):
	instruction = 0x20000000
	offset <<= 6
	src = register_map[src] << 16
	dst = register_map[base] << 21
	instruction |= dst
	instruction |= src
	instruction |= offset
	return instruction

# ld reg, imme8(reg)
def ld_reg_mem(dst, offset, base):
	instruction = 0xc0000000
	offset <<= 6
	dst = register_map[dst] << 16
	src = register_map[base] << 21
	instruction |= src
	instruction |= dst
	instruction |= offset
	return instruction

# add reg, reg
# sub reg, reg
# and reg, reg
# or reg, reg
def calc_dst_src_imme(calc_instr, dst, src, num):
	instruction = 0x80000000
	dst = register_map[dst] << 16
	src = register_map[src] << 21
	num <<= 6
	instruction |= src
	instruction |= dst
	instruction |= num
	instruction |= calc_map[calc_instr]
	return instruction

# jmp imme8
def jump_instruction(addr):
	instruction = 0x10000000
	instruction |= addr
	return instruction

if __name__ == '__main__':
	if len(sys.argv) < 3:
		print("Usage: ")
		print("python snake_assembler.py <target_file> <src_file>")
		sys.exit(1)

	# 输出的二进制文件
	target_fd = open(sys.argv[1], 'wb')
	# 输出可以让logisim直接导入的文件
	target_logisim_fd = open(sys.argv[1]+".txt", 'w')
	# 源代码文件
	src_fd = open(sys.argv[2], 'r', encoding='utf-8')

	target_logisim_fd.write("v2.0 raw\n")

	for line in src_fd.readlines():
		current_line += 1
		instruction = 0
		line = line.strip().lower()

		# 以下处理不同指令

		if line.startswith(('add', 'sub', 'and', 'or')):
			groups = re.match(r'(add|sub|and|or) +(r[0-7]) *, *(r[0-7]) *, *([0-9]+)', line).groups()
			if groups is None:
				print("line: {} have an error: \n\t{}".format(current_line, line))
				sys.exit(2)

			instruction = calc_dst_src_imme(groups[0], groups[1], groups[2], int(groups[3]))
			instruction_order += 1
		elif line.startswith('jmp'):
			groups = re.match(r'(jmp) +(\w+)', line).groups()
			if groups is None:
				print("line: {} have an error: \n\t{}".format(current_line, line))
				sys.exit(2)

			# 找到对应标签的行号并把标签转化为行号，如果没有标签停止编译
			if groups[1] not in label_line_map.keys():
				print("line: {} can't not found label: {}\n\t{}".format(current_line, groups[1], line))
				sys.exit(2)
			
			instruction = jump_instruction(label_line_map[groups[1]])
			instruction_order += 1
		elif line.startswith('sw'):
			groups = re.match(r'sw +([0-9]+)\((r[0-7])\) *, *(r[0-7])', line).groups()
			if groups is None:
				print("line: {} have an error: \n\t{}".format(current_line, line))
				sys.exit(2)

			instruction = sw_mem_reg(int(groups[0]), groups[1], groups[2])	
			instruction_order += 1
		elif line.startswith('ld'):
			groups = re.match(r'ld +(r[0-7]) *, *([0-9]+)\((r[0-7])\)', line).groups()
			if groups is None:
				print("line: {} have an error: \n\t{}".format(current_line, line))
				sys.exit(2)

			instruction = ld_reg_mem(groups[0], int(groups[1]), groups[2])
			instruction_order += 1
		elif line.startswith('movi'):
			groups = re.match(r'movi +(r[0-7]) *, *([0-9]+)', line).groups()
			if groups is None:
				print("line: {} have an error: \n\t{}".format(current_line, line))
				sys.exit(2)

			instruction = mov_reg_imme(groups[0], int(groups[1]))
			instruction_order += 1
		elif line.startswith('movr'):
			groups = re.match(r'movr +(r[0-7]) *, *(r[0-7])', line).groups()
			
			instruction = mov_reg_reg(groups[0], groups[1])
			instruction_order += 1
		else:
			# 标签行，记录行号
			if line.endswith(":"):
				label_line_map[line.strip(':')] = instruction_order
			# 注释和空行
			elif line.startswith(";") or line == '':
				pass
			else:
				# 未识别指令
				print("line: {} instruction error:\n\t{}".format(current_line, line))
				sys.exit(2)
			continue

		print("{}  ->  {}".format(line, hex(instruction)))
		target_fd.write(struct.pack('I', instruction))
		target_logisim_fd.write(hex(instruction)[2:] + ' ')
		target_logisim_fd.write('\n' if instruction_order % 8 == 0 else '')

	target_fd.close()
	target_logisim_fd.close()
	src_fd.close()