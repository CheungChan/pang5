#include <Array.au3>
ControlFocus("�ļ��ϴ�", "", "Edit1")
WinWait("[CLASS:#32770]", "", 10)
_ArrayDelete($CmdLine,0)
$a=_ArrayToString ( $CmdLine, '" "')
$b='"' & $a & '"'
ControlSetText("�ļ��ϴ�" ,"", "Edit1", $b)
Sleep(2000)
ControlClick("�ļ��ϴ�", "","Button1");