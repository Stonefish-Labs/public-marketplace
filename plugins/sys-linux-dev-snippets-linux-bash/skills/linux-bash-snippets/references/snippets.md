# Linux Bash Snippet References

## 1) Download File Over TOR

Use when you need resumable anonymous download behavior.

```bash
torsocks wget --tries=0 -c http://example.onion/file.bin
```

- `--tries=0`: infinite retries.
- `-c`: resume partial download.

Prerequisites:
- `torsocks` and `wget` installed.
- TOR service/path works in current environment.

Verification:
```bash
ls -lh ./file.bin
```

Rollback/fallback:
- Remove partial artifact: `rm -f ./file.bin`.
- If TOR is unavailable, document that non-TOR fallback changes threat model.

## 2) Copy Shared Libraries from `ldd` Output

Use when packaging a dynamically linked ELF binary with local dependency copies.

```bash
#!/usr/bin/env bash

if [ -z "$1" ]; then
    echo "Usage: $0 <elf_binary>"
    exit 1
fi

if [ ! -f "$1" ]; then
    echo "Error: ELF binary not found: $1"
    exit 1
fi

mkdir -p libs

ldd "$1" | while read -r line; do
    lib_path=$(echo "$line" | awk '{ print $3 }')
    if [ -f "$lib_path" ]; then
        cp "$lib_path" libs/
    fi
done

echo "Libraries copied to 'libs' folder."
```

Verification:
```bash
find libs -maxdepth 1 -type f | wc -l
```

Fallback:
- For containerized delivery, prefer building in target base image instead of copying host libs.

Rollback:
```bash
rm -rf libs
```

