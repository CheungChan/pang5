#include <Array.au3>
; ����ִ��ǰ��Ҫ��windows�ϴ��� Ȼ�����exe���� ���������һ���Ǵ򿪵Ŀ�ı��⣨�е��Ǵ򿪣��е���ͼƬ�ϴ���
; ֮��Ĳ�����ͼƬ·�� ÿ��ͼƬ·������Ҫ������������
; e.g   D:/uploadImg.exe "D:\PycharmWorkspace\pang5\images\�½�\00.jpg" "D:\PycharmWorkspace\pang5\images\ �½�\01.jpg" "D:\PycharmWorkspace\pang5\images\�½�\02.jpg" "D:\PycharmWorkspace\pang5\images\�½�\03.jpg" "D:\PycharmWorkspace\pang5\images\�½�\04.jpg" "D:\PycharmWorkspace\pang5\images\�½�\05.jpg" "D:\PycharmWorkspace\pang5\images\�½�\06.jpg" "D:\PycharmWorkspace\pang5\images\�½�\07.jpg" "D:\PycharmWorkspace\pang5\images\�½�\08.jpg" "D:\PycharmWorkspace\pang5\images\�½�\09.jpg"
Local $title = $CmdLine[1]
ControlFocus($title, "", "Edit1")
WinWait("[CLASS:#32770]", "", 10)
; �Ѳ�������ǰ��������ȥ��
_ArrayDelete($CmdLine,0)
_ArrayDelete($CmdLine,0)
$a=_ArrayToString ( $CmdLine, '" "')
$b='"' & $a & '"'
ControlSetText($title ,"", "Edit1", $b)
Sleep(2000)
ControlClick($title, "","Button1");