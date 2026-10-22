# Workbench directory ownership regression

This native ABIv11 test starts a pthread which changes directory, then checks which original directory lock CRT has retained for exit. It uses the pinned CRT private layout for observation only; production code uses the public `chdir` API. It is not a mainline v1 test.

Build with `python3 tests/workbench-cwd/build.py /absolute/new-output-directory` after configuring `local.json`. Deploy to a disk drawer such as `SYS:pdf-cwd-test`, not RAM:. RAM filesystem locks can share addresses and mask the ownership error.

Run `openwb SYS:pdf-cwd-test/lock-red`. Read `RAM:lock-red.log`: `cli=0` confirms Workbench startup, and `owner_ok=0` demonstrates that CRT retained the worker's lock rather than the main process's original lock. Preserve the log and restart the test system: exit may double-unlock a freed lock even when it produces no alert.

Run `openwb SYS:pdf-cwd-test/lock-green` on the fresh boot. Expect `owner_ok=1`, a zero worker result, and a responsive desktop after exit. The only difference is the main process's `chdir(".")` before pthread creation. Also run `lock-green` from a Shell and check its exit code. Logs are overwritten on each invocation; save each result under a distinct name.

The probe tests the CRT ownership defect. Separately test the patched PdfCraft binary from a disk drawer through Workbench and Shell, including open/save and post-exit disk browsing. Success under emulation does not establish that every AROS environment is fixed.
