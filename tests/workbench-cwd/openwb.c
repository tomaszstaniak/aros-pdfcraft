#include <proto/exec.h>
#include <proto/workbench.h>
#include <workbench/workbench.h>
struct Library *WorkbenchBase;
int main(int argc,char **argv) {
 if(argc!=2)return 20;
 WorkbenchBase=OpenLibrary("workbench.library",0);
 if(!WorkbenchBase)return 20;
 int ok=OpenWorkbenchObjectA(argv[1],0);
 CloseLibrary(WorkbenchBase);return ok?0:20;
}
