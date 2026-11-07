"""Exécute les doublures Lua avec lua5.4, ou Lupa si Lua n'est pas sur le PATH."""
from pathlib import Path
import shutil,subprocess

def run(path, root):
    path,root=Path(path),Path(root)
    lua=shutil.which('lua5.4')
    if lua:
        subprocess.run([lua,str(path),str(root)],check=True)
    else:
        from lupa import LuaRuntime
        runtime=LuaRuntime(unpack_returned_tuples=True)
        runtime.globals().arg=runtime.table_from({1:root.as_posix()})
        runtime.execute(path.read_text(encoding='utf8'))
