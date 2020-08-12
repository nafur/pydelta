import os

def version_from_git():
    import re
    import subprocess
    GIT_VERSION = subprocess.check_output(['git', 'describe', '--tags']).decode('utf8').strip()
    if re.match('^v[0-9.]+$', GIT_VERSION) is not None:
        return GIT_VERSION[1:]
    else:
        m = re.match('v([0-9]+)\\.([0-9]+)-([0-9]+)-g[a-z0-9]+', GIT_VERSION)
        if m is not None:
            return '{}.{}.dev{}'.format(m.group(1), int(m.group(2)) + 1, m.group(3))
    return GIT_VERSION

def version_from_package_metadata():
    try:
        from importlib import metadata
    except ImportError:
        import importlib_metadata as metadata
    return metadata.version('pydelta-smt')

__git_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.git')
if os.path.isdir(__git_dir):
    VERSION = version_from_git()
else:
    VERSION = version_from_package_metadata()
