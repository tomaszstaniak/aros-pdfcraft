# Detached pthread exit regression

`python3 tests/pthread-exit/build.py <fresh-label>` builds the selected pinned v11 pthread source plus the repository's private series. It injects a test-only hook immediately after the detached thread clears its slot and releases `thread_sem`. The hook busy-loops without Wait/Delay; it widens an actual preemption window without creating a new yielding operation.

Use an exclusively reserved matching v11 guest. Extract to RAM:pdfc, inspect the UnZip log, then `Execute RAM:pdfc/run-tail`. Collect while stopped and validate matching text, rc and done files. No hook is linked into production binaries.

The main task has higher priority, sleeps until the hook starts, then calls the real `__pthread_Exit_Func`. With only patch0001, the handler returns while `tail_done=0` (rc20, RED). With patch0002, the final Forbid prevents the parent from resuming until the epilogue has left executable code: `tail_done=1`, rc0. The test keeps the executable loaded after a RED result until the tail ends; it does not intentionally crash the guest by unloading it early.

This establishes the private pthread race and its correction on the selected older-v11 profile. It does not prove that a reported aros.games desktop crash has the same cause or establish mainline v1/SMP behavior.
