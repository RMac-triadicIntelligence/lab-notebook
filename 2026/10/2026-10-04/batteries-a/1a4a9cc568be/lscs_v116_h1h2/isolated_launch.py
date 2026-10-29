"""H2 fix, part 1 (shrink what executes).

The pins verified the genome (four files) while the environment rewrote the expression
(usercustomize, PYTHON* vars, HOME). Instead of measuring the whole environment, make
the running set equal the measured set:

  python -I      isolated: no user site-packages, PYTHON* env ignored, no script dir or cwd on sys.path
  python -B      no .pyc writes
  -c BOOTSTRAP   puts ONLY the verified copies dir on sys.path, then runs notary.py by path,
                 so notary.py's own sibling imports (wire, etc.) still resolve under -I
  env            minimal and explicit; no HOME

Not closed by this: root-owned system site-packages (.pth / sitecustomize) still run, and
`-S` would drop `cryptography`. `startup_surface()` reports what still executes so it can be
audited or added to the lineage. The interpreter binary itself is trusted.
"""
import subprocess, sys

BOOTSTRAP = (
    "import sys, runpy\n"
    "_p, _d = sys.argv[1], sys.argv[2]\n"
    "sys.argv = [_p] + sys.argv[3:]\n"
    "sys.path.insert(0, _d)\n"
    "runpy.run_path(_p, run_name='__main__')\n"
)

CLEAN_ENV = {"PATH": "/usr/bin:/bin", "LC_ALL": "C.UTF-8"}


def notary_argv(notary_path, copies_dir, args=(), python=None):
    return [python or sys.executable, "-I", "-B", "-c", BOOTSTRAP,
            notary_path, copies_dir, *map(str, args)]


def launch(notary_path, copies_dir, args=(), python=None, **popen_kw):
    popen_kw.setdefault("env", dict(CLEAN_ENV))
    popen_kw.setdefault("cwd", copies_dir)
    popen_kw.setdefault("close_fds", True)
    return subprocess.Popen(notary_argv(notary_path, copies_dir, args, python), **popen_kw)


_SURFACE = r'''
import sys, site, os, json, importlib.util
out = {"isolated": sys.flags.isolated, "user_site_enabled": site.ENABLE_USER_SITE,
       "sitecustomize": None, "exec_pth": []}
spec = importlib.util.find_spec("sitecustomize")
if spec and spec.origin: out["sitecustomize"] = spec.origin
for d in site.getsitepackages():
    if os.path.isdir(d):
        for n in sorted(os.listdir(d)):
            if n.endswith(".pth"):
                p = os.path.join(d, n)
                try:
                    if any(l.startswith(("import ", "import\t")) for l in open(p)):
                        out["exec_pth"].append(p)
                except OSError: pass
print(json.dumps(out))
'''


def startup_surface(python=None):
    """What still runs before notary.py under -I. Anything listed should be root-owned
    and, ideally, marked in the lineage."""
    import json
    p = subprocess.run([python or sys.executable, "-I", "-B", "-c", _SURFACE],
                       env=dict(CLEAN_ENV), capture_output=True, text=True, timeout=30)
    return json.loads(p.stdout)
