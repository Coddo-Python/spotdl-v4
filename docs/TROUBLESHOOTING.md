# Troubleshooting / FAQ Guide

As common issues or questions are encountered solutions will be added to this guide.

## pkg_resources.DistributionNotFound

Sometimes not all packages are installed but are required by yt-dlp for example: `brotli` or `websockets`

### Error message

`pkg_resources.DistributionNotFound: The 'websockets' distribution was not found and is required by yt-dlp`

### Solution

`pip install brotli websockets yt-dlp -U`

## HTTP Error 404

https://github.com/plamere/spotipy/issues/795#issuecomment-1100321148

### Error message

`HTTP Error for GET to URL with Params: {} returned 404 due to None`

### Solution

Update spotdl to the latest version which contains workaround.

`pip install -U spotdl`

## Failed to install `RapidFuzz` on termux

https://github.com/spotDL/spotify-downloader/issues/1485
https://github.com/maxbachmann/RapidFuzz/issues/195

### Error message

```
ld.lld: error: unable to find library -lgcc
clang-13: error: linker command failed with exit code 1 (use -v to see invocation)
ninja: build stopped: subcommand failed.
```

or

```
ERROR: Could not build wheels for cmake, ninja, which is required to install pyproject.toml-based projects
```

### Solution

```bash
# Setup its-pointless repo
curl -LO https://its-pointless.github.io/setup-pointless-repo.sh
bash setup-pointless-repo.sh

# Install numpy
pkg install numpy

# install rapidfuzz (v1.9.1 for now)
pip install rapidfuzz==1.9.1

# Install spotdl
pip install spotdl
```

## ssl.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]

https://stackoverflow.com/questions/27835619/urllib-and-ssl-certificate-verify-failed-error

### Error message

`urllib.error.URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:847)>`

### Solution

https://stackoverflow.com/questions/27835619/urllib-and-ssl-certificate-verify-failed-error

## RecursionError

https://github.com/spotDL/spotify-downloader/issues/1493

### Error message

`RecursionError: maximum recursion depth exceeded`

### Solution

Update spotdl

`pip install spotdl -U`

## spotdl: command not found

If you see this error after installing spotdl, that means
that the bin folder is not on `$PATH`

### Solution

#### `.bashrc`

Add `export PATH=~/.local/bin:$PATH` at the bottom of `~/.bashrc`

Then run `source ~/.bashrc`

#### `.zshrc`

Add `export PATH=~/.local/bin:$PATH` at the bottom of `~/.zshrc`
Then run `source ~/.zshrc`

## RuntimeWarning

This happens when running spotdl using `python -m`.

### Error message

```
RuntimeWarning: 'spotdl.__main__' found in sys.modules after import of package 'spotdl',
but prior to execution of 'spotdl.__main__'; this may result in unpredictable behaviour
warn(RuntimeWarning(msg))
```

### Solution

You can ignore this error or just run spotdl directly

## Not found '_raw_ecb.so'

This error is specific for M1 Macs only.

https://discord.com/channels/771628785447337985/871006150357823498
https://discord.com/channels/771628785447337985/939475659238043738

### Error message

```
aise OSError("Cannot load native module '%s': %s" % (name, ", ".join(attempts)))
OSError: Cannot load native module 'Cryptodome.Cipher._raw_ecb': Not found '_raw_ecb.cpython-39-darwin.so',
Cannot load '_raw_ecb.abi3.so': dlopen(/opt/homebrew/lib/python3.9/site-packages/Cryptodome/Util/../Cipher/_raw_ecb.abi3.so, 6): no suitable image found.  Did find:
/opt/homebrew/lib/python3.9/site-packages/Cryptodome/Util/../Cipher/_raw_ecb.abi3.so: mach-o, but wrong architecture
/opt/homebrew/lib/python3.9/site-packages/Cryptodome/Cipher/_raw_ecb.abi3.so: mach-o, but wrong architecture, Not found '_raw_ecb.so'
```

### Solution

Possible solutions:

https://discord.com/channels/771628785447337985/871006150357823498
https://discord.com/channels/771628785447337985/939475659238043738


## 'spotdl' is not recognized

Python/(site packages) is not added to PATH correctly.
You need to install Python from https://www.python.org/downloads/

Or you are using python from microsoft store. If so uninstall it
and restart cmd. If this doesn't work reinstall python.

### Error message

```
'spotdl' is not recognized as an internal or external command,
operable program or batch file.
```

### Solution

Ensure to add to PATH when installing:
https://i.imgur.com/jWq5EnV.png


