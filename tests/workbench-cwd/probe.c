#include <proto/exec.h>
#include <proto/dos.h>
#include <dos/dosextens.h>
#include <pthread.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include "__posixc_intbase.h"
extern struct CrtIntBase *CrtBase;
static FILE *logfile;
static void *worker(void *arg) {
    BPTR old = ((struct Process *)FindTask(NULL))->pr_CurrentDir;
    int rc = chdir("RAM:");
    fprintf(logfile, "worker original=%p current=%p chdir=%d\n", (void *)old, (void *)((struct Process *)FindTask(NULL))->pr_CurrentDir, rc);
    return (void *)(long)(rc != 0);
}
int main(int argc, char **argv) {
    pthread_t t; void *ret;
#ifdef PRIME
    logfile=fopen("RAM:lock-green.log","w");
#else
    logfile=fopen("RAM:lock-red.log","w");
#endif
    if (!logfile) return 20;
    BPTR original=((struct Process *)FindTask(NULL))->pr_CurrentDir;
    fprintf(logfile,"main original=%p cli=%p\n",(void *)((struct Process *)FindTask(NULL))->pr_CurrentDir,(void *)((struct Process *)FindTask(NULL))->pr_CLI);
#ifdef PRIME
    if (chdir(".") != 0) return 20;
#endif
    if (pthread_create(&t,0,worker,0) || pthread_join(t,&ret)) return 20;
    fprintf(logfile,"main final=%p worker_rc=%ld\n",(void *)((struct Process *)FindTask(NULL))->pr_CurrentDir,(long)ret);
    struct PosixCIntBase *base=CrtBase->PosixCBase;
    int pass=base->cd_changed && base->cd_lock == original;
    fprintf(logfile,"saved=%p expected=%p owner_ok=%d\n",(void *)base->cd_lock,(void *)original,pass);
    fclose(logfile);
    return pass ? 0 : 20;
}
