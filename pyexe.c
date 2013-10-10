#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <wchar.h>
#include <Python.h>

char* to_utf8(const wchar_t* buffer)
{
    int len = -1;
    int nChars = WideCharToMultiByte(
        CP_UTF8,
        0,
        buffer,
        len,
        NULL,
        0,
        NULL,
        NULL);
    if (nChars == 0) return "";

    char* newbuffer = malloc((nChars + 1) * sizeof(char));
    WideCharToMultiByte(
        CP_UTF8,
        0,
        buffer,
        len,
        newbuffer,
        nChars,
        NULL,
        NULL);

    return newbuffer;
}

int main()
{
    LPWSTR *szArglist;
    int nArgs;
    wchar_t wszPath[10240];
    wchar_t wszCmd[10240];
    wchar_t *p;
    char* szCmd;

    GetModuleFileNameW(NULL, wszPath, sizeof(wszPath));
    p = wcsrchr(wszPath, L'\\');
    if (p == NULL) {
            printf("Get module file name error!\n");
            return -1;
    }
    *p = 0;

    szArglist = CommandLineToArgvW(GetCommandLineW(), &nArgs);

    swprintf(wszCmd, L"PATH=%s\\DLLs;%%PATH%%", wszPath);
    _wputenv(wszCmd);

    Py_NoSiteFlag = 1;
    Py_SetPythonHome(wszPath);
    swprintf(wszCmd, L"%s\\Lib", wszPath);
    Py_SetPath(wszCmd);
    Py_Initialize();
    PySys_SetArgv(nArgs-1, szArglist+1);

    swprintf(wszCmd,
            L"import sys\n"
            L"cur = r'%s'\n"
            L"join = lambda *args: '\\\\'.join(args)\n"
            L"sys.path = [join(cur, f) for f in ['', 'Lib', 'Lib/libstdpy.zip', 'site-packages', 'DLLs']]\n"
            L"import os; join = os.path.join\n"
            L"sys.path += [join(cur, 'Lib', f) for f in os.listdir(join(cur, 'Lib')) if f.endswith('.zip') and f != 'libstdpy.zip']\n"
            L"sys.path.insert(1, join(cur, 'src.zip'))\n"
            L"m = r'%s'\n"
            L"sys.path.insert(0, os.path.split(m)[0])\n"
            L"import imp; imp.load_source('__main__', m)\n",
            wszPath, *(szArglist+1));
    /* wprintf(wszCmd); */
    szCmd = to_utf8(wszCmd);
    PyRun_SimpleString(szCmd);
    free(szCmd);
    LocalFree(szArglist);
    return 0;
}
