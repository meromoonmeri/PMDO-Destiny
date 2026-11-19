"""Exécute les doublures Lua avec lua5.4, ou Lupa si Lua n'est pas sur le PATH."""
from pathlib import Path
import os,shutil,subprocess

def run(path, root):
    path,root=Path(path),Path(root)
    scripts = (root / 'game/Data/Script').as_posix()
    recherche = f'{scripts}/?.lua;{scripts}/?/init.lua;'
    lua=shutil.which('lua5.4')
    if lua:
        env = dict(os.environ, LUA_PATH=recherche + os.environ.get('LUA_PATH', ';'))
        subprocess.run([lua,str(path),str(root)],check=True,env=env)
    else:
        from lupa import LuaRuntime
        runtime=LuaRuntime(unpack_returned_tuples=True)
        package = runtime.globals().package
        package.path = recherche + package.path
        runtime.globals().arg=runtime.table_from({1:root.as_posix()})
        # Lua/CRT sous Windows ouvre certains chemins accentués avec la page
        # de code ANSI. Python utilise l'API Unicode, puis Lua compile le texte.
        compiler = runtime.eval('load')
        def loadfile_unicode(filename):
            try:
                source = Path(filename).read_text(encoding='utf-8-sig')
            except OSError as exc:
                return None, str(exc)
            return compiler(source, '@' + filename)
        runtime.globals().loadfile = loadfile_unicode
        runtime.execute(path.read_text(encoding='utf8'))
