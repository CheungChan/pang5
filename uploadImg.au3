#include <Array.au3>
; 程序执行前需要打开windows上传框。 然后调用exe程序 后面参数第一个是打开的框的标题（有的是打开，有的是图片上传）
; 之后的参数是图片路径 每个图片路径性需要用引号引起来
; e.g   D:/uploadImg.exe "D:\PycharmWorkspace\pang5\images\章节\00.jpg" "D:\PycharmWorkspace\pang5\images\ 章节\01.jpg" "D:\PycharmWorkspace\pang5\images\章节\02.jpg" "D:\PycharmWorkspace\pang5\images\章节\03.jpg" "D:\PycharmWorkspace\pang5\images\章节\04.jpg" "D:\PycharmWorkspace\pang5\images\章节\05.jpg" "D:\PycharmWorkspace\pang5\images\章节\06.jpg" "D:\PycharmWorkspace\pang5\images\章节\07.jpg" "D:\PycharmWorkspace\pang5\images\章节\08.jpg" "D:\PycharmWorkspace\pang5\images\章节\09.jpg"
Local $title = $CmdLine[1]
ControlFocus($title, "", "Edit1")
WinWait("[CLASS:#32770]", "", 10)
; 把参数数组前两个参数去掉
_ArrayDelete($CmdLine,0)
_ArrayDelete($CmdLine,0)
$a=_ArrayToString ( $CmdLine, '" "')
$b='"' & $a & '"'
ControlSetText($title ,"", "Edit1", $b)
Sleep(2000)
ControlClick($title, "","Button1");