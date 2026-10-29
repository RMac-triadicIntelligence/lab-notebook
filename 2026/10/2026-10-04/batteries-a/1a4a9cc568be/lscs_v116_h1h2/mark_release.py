"""Offline marking tool. The founder key is generated and kept OFF the box the organism runs on.

  keygen   --out KEY                     new Ed25519 key (prints its public hex)
  genesis  --key FOUNDER --root DIR --version V --files f1 f2 ... --next PUBHEX [PUBHEX...]
  descend  --key SIGNER  --root DIR --version V --files ...       --next PUBHEX [PUBHEX...]
  verify   --anchor FOUNDER.pub --root DIR --files ... [--min-generation N] [--lax]
"""
import argparse, os, sys
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
import lineage as L


def _load(path):
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), None)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["keygen", "genesis", "descend", "verify"])
    ap.add_argument("--out"); ap.add_argument("--key"); ap.add_argument("--anchor")
    ap.add_argument("--root"); ap.add_argument("--version")
    ap.add_argument("--files", nargs="*", default=[]); ap.add_argument("--next", nargs="*", default=[])
    ap.add_argument("--min-generation", type=int, default=0); ap.add_argument("--lax", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "keygen":
        k = Ed25519PrivateKey.generate()
        fd = os.open(a.out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        os.write(fd, k.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                     serialization.NoEncryption())); os.close(fd)
        with open(a.out + ".pub", "w") as f:
            f.write(L.pub_hex(k) + "\n")
        print(L.pub_hex(k)); return 0
    if a.cmd in ("genesis", "descend"):
        files = L.hash_tree(a.root, a.files)
        if a.cmd == "genesis":
            chain = L.genesis(_load(a.key), a.version, files, a.next)
        else:
            chain = L.descend(L.read_chain(a.root), _load(a.key), a.version, files, a.next)
        L.write_chain(a.root, chain)
        print("generation", chain[-1]["generation"], "marked", len(files), "files"); return 0
    anchor = L.load_anchor(a.anchor, a.root, strict=not a.lax)
    head = L.gate(a.root, a.files, L.read_chain(a.root), anchor, a.min_generation)
    print("OK generation", head["generation"], head["version"]); return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except L.LineageError as e:
        print("REFUSED:", e); sys.exit(2)
