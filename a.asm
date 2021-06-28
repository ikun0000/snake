; 初始化坐标
movi r0, 0			
movi r1, 2		
sw 1(r0), r1
sw 2(r0), r1	
ld r6, 2(r0)	

; 向右移动一格
label1:
ld r1, 1(r0)
add r2, r1, 1	
sw 1(r0), r2	
movr r5, r2		
jmp label1	