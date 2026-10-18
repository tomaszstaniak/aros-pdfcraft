/* Native regression: an exit handler must not return while detached thread
 * epilogue instructions still execute in the executable. Test-only hook is
 * injected after slot cleanup, widening that real scheduling window. */
#include <proto/exec.h>
#include <proto/dos.h>
#include <pthread.h>
#include <stdio.h>
#include <stdint.h>
static volatile unsigned tail_entered, tail_done, spins;
void pdfc_test_thread_tail(void)
{
    tail_entered = 1;
    for (spins = 0; spins < 40000000; ++spins)
        __asm__ volatile ("" ::: "memory");
    tail_done = 1;
}
static void *worker(void *unused) { (void)unused; return NULL; }
extern void __pthread_Exit_Func(void);
int main(void)
{
    pthread_t thread;
    pthread_attr_t attr;
    LONG previous = SetTaskPri(FindTask(NULL), 5);
    pthread_attr_init(&attr);
    pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_DETACHED);
    int error = pthread_create(&thread, &attr, worker, NULL);
    pthread_attr_destroy(&attr);
    if (error) { printf("create error %d\n", error); return 10; }
    unsigned timeout = 0;
    while (!tail_entered && timeout++ < 500) Delay(1);
    if (!tail_entered) { printf("hook not reached\n"); return 11; }
    __pthread_Exit_Func();
    unsigned returned_before_tail_done = !tail_done;
    printf("exit_returned_before_tail_done=%u entered=%u done=%u\n",
           returned_before_tail_done, tail_entered, tail_done);
    while (!tail_done) Delay(1);
    Delay(2); /* Leave the test process loaded until the instrumented tail ends. */
    SetTaskPri(FindTask(NULL), previous);
    return returned_before_tail_done ? 20 : 0;
}
