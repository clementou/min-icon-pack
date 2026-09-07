# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Fetch pinned official Android SDK archives into ignored local storage."""
from pathlib import Path
import hashlib
import platform
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parents[1]
PACKAGES={
 'Darwin':('build-tools_r37_macosx.zip','eb080751b2b2028eb3604f571027d6f7b3c46321'),
 'Linux':('build-tools_r37_linux.zip','70954e99f4c3d9d46ee70fa32624672fe7cd6ebe'),
}
PLATFORM=('platform-37.2_r01.zip','4bec12a02162ff6852df50b5fcf8ee762b050966')

def main():
    archives=[(*PACKAGES[platform.system()],'build-tools'),(*PLATFORM,'platforms')]
    downloads=ROOT/'.local/downloads'; downloads.mkdir(parents=True,exist_ok=True)
    for name,checksum,folder in archives:
        path=downloads/name
        if not path.exists():
            print('Downloading '+name,flush=True)
            urllib.request.urlretrieve('https://dl.google.com/android/repository/'+name,path)
        if hashlib.sha1(path.read_bytes()).hexdigest()!=checksum:
            raise SystemExit('SDK checksum mismatch: '+name)
        dest=ROOT/'.local/sdk'/folder; dest.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(path) as archive:
            for item in archive.infolist():
                target=(dest/item.filename).resolve()
                if not target.is_relative_to(dest.resolve()): raise ValueError(item.filename)
                archive.extract(item,dest)
                mode=item.external_attr>>16
                if mode and not item.is_dir(): target.chmod(mode & 0o777)
    print('SDK ready in .local/sdk. Archives governed by the Android SDK license.')

if __name__=='__main__': main()
