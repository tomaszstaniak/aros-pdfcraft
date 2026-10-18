use std::path::Path;
fn report(label: &str) {
    println!("{label} cwd={:?}", std::env::current_dir());
    for path in [".", "RAM:", "RAM:pdfc", "/RAM", "/RAM/pdfc", "RAM:pdfc/fixture.pdf"] {
        println!("{label} {path:?} meta={:?} canonical={:?}",
            std::fs::metadata(path).map(|m| (m.is_dir(), m.len())), Path::new(path).canonicalize());
    }
    let dot = std::ffi::CString::new(".").expect("literal");
    let fd = unsafe { libc::open(dot.as_ptr(), libc::O_RDONLY) };
    println!("{label} open_dot={fd} errno={:?}", std::io::Error::last_os_error());
    if fd >= 0 { unsafe { libc::close(fd); } }
}
fn main() {
    println!("PATH_PROBE {}", std::env::args().nth(1).unwrap_or_default());
    report("main");
    std::thread::Builder::new().stack_size(1048576).spawn(||report("worker")).expect("spawn").join().expect("join");
    println!("PATH_PROBE_DONE");
}
