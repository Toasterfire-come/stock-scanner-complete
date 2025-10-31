import os
import paramiko

HOST = os.environ.get("SFTP_HOST", "access-5018544625.webspace-host.com")
PORT = int(os.environ.get("SFTP_PORT", "22"))
USER = os.environ.get("SFTP_USER", "")
PASSWORD = os.environ.get("SFTP_PASSWORD", "")
LOCAL_BUILD_DIR = os.environ.get("LOCAL_BUILD_DIR", os.path.join(os.path.dirname(__file__), "..", "frontend", "build"))
REMOTE_ROOT = os.environ.get("SFTP_REMOTE_ROOT", "/")

def sftp_connect():
    transport = paramiko.Transport((HOST, PORT))
    transport.connect(username=USER, password=PASSWORD)
    sftp = paramiko.SFTPClient.from_transport(transport)
    return sftp, transport

def remove_all(sftp, path):
    try:
        for entry in sftp.listdir_attr(path):
            p = f"{path.rstrip('/')}/{entry.filename}"
            if str(entry.longname).startswith('d'):
                remove_all(sftp, p)
                try:
                    sftp.rmdir(p)
                except Exception:
                    pass
            else:
                try:
                    sftp.remove(p)
                except Exception:
                    pass
    except IOError:
        pass

def ensure_dirs(sftp, remote_path):
    parts = remote_path.strip('/').split('/')
    cur = ''
    for part in parts[:-1]:
        cur += '/' + part
        try:
            sftp.stat(cur)
        except IOError:
            sftp.mkdir(cur)

def upload_dir(sftp, local_dir, remote_dir):
    for root, dirs, files in os.walk(local_dir):
        rel = os.path.relpath(root, local_dir)
        target = remote_dir if rel == '.' else f"{remote_dir.rstrip('/')}/{rel}"
        ensure_dirs(sftp, target + '/x')
        for d in dirs:
            rp = f"{target.rstrip('/')}/{d}"
            try:
                sftp.stat(rp)
            except IOError:
                sftp.mkdir(rp)
        for f in files:
            lp = os.path.join(root, f)
            rp = f"{target.rstrip('/')}/{f}"
            sftp.put(lp, rp)

def main():
    if not USER or not PASSWORD:
        raise SystemExit("Set SFTP_USER and SFTP_PASSWORD env vars.")
    build_dir = os.path.abspath(LOCAL_BUILD_DIR)
    if not os.path.isdir(build_dir):
        raise SystemExit(f"Build dir not found: {build_dir}")
    sftp, transport = sftp_connect()
    try:
        remove_all(sftp, REMOTE_ROOT)
        upload_dir(sftp, build_dir, REMOTE_ROOT)
        print("Deployed successfully.")
    finally:
        sftp.close()
        transport.close()

if __name__ == "__main__":
    main()

