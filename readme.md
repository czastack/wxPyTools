# wxPyTools

基于wxPython 的实用工具集

## wxWidgets compile
### release
nmake -f makefile.vc TARGET_CPU=X64 BUILD=release UNICODE=1 SHARED=0 MONOLITHIC=0 RUNTIME_LIBS=static
### debug
nmake -f makefile.vc TARGET_CPU=X64 BUILD=debug UNICODE=1 SHARED=0 MONOLITHIC=0 RUNTIME_LIBS=static
### debug dll
nmake -f makefile.vc TARGET_CPU=X64 BUILD=debug UNICODE=1 SHARED=1 MONOLITHIC=0 RUNTIME_LIBS=static
### release dll (for sample)
nmake -f makefile.vc TARGET_CPU=X64 BUILD=release UNICODE=1 SHARED=1 MONOLITHIC=0 RUNTIME_LIBS=dynamic

## test env
mklink /D x64\Release\python ..\..\python
