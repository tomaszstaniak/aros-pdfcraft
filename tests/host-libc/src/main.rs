fn main() {
    assert_eq!(unsafe { libc::getpid() }, std::process::id() as libc::pid_t);
    assert_eq!(std::mem::size_of::<libc::pthread_t>(), std::mem::size_of::<usize>());
    let client = jobserver::Client::new(1).expect("host jobserver creation");
    let token = client.acquire().expect("host jobserver acquire");
    drop(token);
    assert_eq!(client.available().expect("host pipe ioctl"), 1);
}
