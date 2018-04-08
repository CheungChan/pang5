#include <Array.au3>
ControlFocus("文件上传", "", "Edit1")
WinWait("[CLASS:#32770]", "", 10)
_ArrayDelete($CmdLine,0)
$a=_ArrayToString ( $CmdLine, '" "')
$b='"' & $a & '"'
ControlSetText("文件上传" ,"", "Edit1", $b)
Sleep(2000)
ControlClick("文件上传", "","Button1");