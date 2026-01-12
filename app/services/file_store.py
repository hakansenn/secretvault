import os, uuid
from pathlib import Path
from app.core.config import settings

ALLOWED = {
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/png":  [b"\x89PNG\r\n\x1a\n"],
    "application/pdf": [b"%PDF"],
}

def _sniff_ok(content_type: str, head: bytes) -> bool:
    sigs = ALLOWED.get(content_type)
    if not sigs:
        return False
    return any(head.startswith(sig) for sig in sigs)

def save_upload(fileobj, *, content_type: str) -> tuple[str, int]:
    """
    returns (stored_name, size_bytes)
    """
    if content_type not in ALLOWED:
        raise ValueError("Unsupported content type")

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # signature check
    head = fileobj.read(16)
    if not _sniff_ok(content_type, head):
        raise ValueError("File signature does not match content type")
    fileobj.seek(0)

    stored_name = uuid.uuid4().hex
    path = upload_dir / stored_name

    max_bytes = settings.max_upload_mb * 1024 * 1024
    total = 0

    with open(path, "wb") as out:
        while True:
            chunk = fileobj.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > max_bytes:
                out.close()
                try:
                    os.remove(path)
                except OSError:
                    pass
                raise ValueError("File too large")
            out.write(chunk)

    return stored_name, total
