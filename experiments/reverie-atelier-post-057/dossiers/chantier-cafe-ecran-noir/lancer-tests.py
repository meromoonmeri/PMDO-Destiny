from pathlib import Path
from lupa import LuaRuntime
root=str(Path('travail').resolve())
lua=LuaRuntime(unpack_returned_tuples=True);lua.globals().arg=lua.table_from({1:root});lua.execute(Path('test_intro_cafe.lua').read_text())
