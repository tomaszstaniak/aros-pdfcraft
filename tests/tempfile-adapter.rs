// Exercise the actual AROS adapter module on the host, without selecting AROS ABI types.
#[path = "../build/v11/crates/tempfile-3.27.0/src/file/imp/aros.rs"]
mod adapter;
use std::fs::{self, OpenOptions};
use std::io::Write;

#[test]
fn occupied_targets_and_replaced_paths_are_preserved() {
    let root = std::env::temp_dir().join(format!("pdfcraft-tempfile-{}", std::process::id()));
    fs::create_dir(&root).unwrap();
    let old = root.join("source");
    let dest = root.join("destination");
    let mut file = adapter::create_named(&old, &mut OpenOptions::new(), None).unwrap();
    file.write_all(b"original").unwrap();
    assert!(adapter::create_named(&old, &mut OpenOptions::new(), None).is_err());
    fs::write(&dest, b"existing").unwrap();
    assert!(adapter::persist(&old, &dest, false).is_err());
    assert!(adapter::persist(&old, &dest, true).is_err(), "unaccepted overwrite must fail closed");
    assert_eq!(fs::read(&dest).unwrap(), b"existing");
    assert_eq!(fs::read(&old).unwrap(), b"original");
    assert!(adapter::reopen(&file, &old).is_ok());
    fs::rename(&old, root.join("moved")).unwrap();
    fs::write(&old, b"replacement").unwrap();
    assert!(adapter::reopen(&file, &old).is_err());
    fs::remove_file(&dest).unwrap();
    adapter::persist(&old, &dest, false).unwrap();
    assert_eq!(fs::read(&dest).unwrap(), b"replacement");
    assert!(!old.exists());
    assert!(adapter::create(&root).is_err());
    adapter::keep(&dest).unwrap();
    drop(file);
    fs::remove_dir_all(root).unwrap();
}
