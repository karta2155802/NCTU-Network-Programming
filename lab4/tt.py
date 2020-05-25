a = 1   # 建立全域變數a

def fun():
	global a, c   # 宣告函式中會用到全域變數a和c
	a = 10   # 改變全域變數a的值
	c = 30   # 改變全域變數c的值

c = 3   # 建立全域變數c

fun()   # 呼叫函式

print(a)   # 顯示變數a的值
print(c)   # 顯示變數c的值