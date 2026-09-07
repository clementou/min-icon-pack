"""Fetch pinned official Android SDK archives into ignored local storage."""
from pathlib import Path
import hashlib
import platform
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parents[1]
PACKAGES={
 'Darwin':('build-tools_r36_macosx.zip','199ae0047ee61e842f8ee0c6d3918e44fb9a1f83'),
 'Linux':('build-tools_r36_linux.zip','b0b6376977657e8ad9b969bacf4093601da2c6fb'),
}

def main():
    archives=[(*PACKAGES[platform.system()],'build-tools'),
              ('platform-36_r02.zip','2c1a80dd4d9f7d0e6dd336ec603d9b5c55a6f576','platforms')]
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
