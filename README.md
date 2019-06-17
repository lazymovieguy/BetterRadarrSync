# BetterRadarrSync

Based off of Sperryfreak01 project RadarrSync https://github.com/Sperryfreak01/RadarrSync

## Docker

`docker run -ti --rm lazymovieguy/brs:0.1 profiles -h`

`docker run -ti --rm lazymovieguy/brs:0.1 profiles http://localhost API_KEY`


`docker run -ti --rm lazymovieguy/brs:0.1 syncronize -h`

`docker run -ti --rm lazymovieguy/brs:0.1 syncronize http://localhost --src-port 80 --src-profile 'Ultra-HD' SRC_API_KEY http://localhost --dest-port 7879 --dest-profile HD-720p DEST_API_KEY`



## From Source
---
```
usage: brs.py [-h] [--port PORT] [-v {INFO,WARNING,ERROR,CRITICAL,DEBUG}]
              url key

Lists profiles on a Radarr Instance

positional arguments:
  url                   Radarr url to list profiles from; Ex.http://127.0.0.1
  key                   API key

optional arguments:
  -h, --help            show this help message and exit
  --port PORT           Port to use; Default: 80
  -v {INFO,WARNING,ERROR,CRITICAL,DEBUG}
                        Verbosity Level; Default: INFO
```

---
```
usage: brs.py [-h] [--src-port SRC_PORT] [--src-profile SRC_PROFILE]
              [--dest-port DEST_PORT] [--dest-profile DEST_PROFILE]
              [-v {INFO,WARNING,ERROR,CRITICAL,DEBUG}]
              src-url src-key dest-url dest-key

Syncs movies matching a profile from instance x to instance y

positional arguments:
  src-url               Radarr url to sync from; Ex.http://127.0.0.1
  src-key               API key
  dest-url              Radarr url to sync to; Ex. http://127.0.0.1
  dest-key              API key

optional arguments:
  -h, --help            show this help message and exit
  --src-port SRC_PORT   Port to use; Default: 80
  --src-profile SRC_PROFILE
                        Profile to sync; Default: Ultra-HD
  --dest-port DEST_PORT
                        Port to use; Default: 80
  --dest-profile DEST_PROFILE
                        Profile to sync; Default: HD-720p
  -v {INFO,WARNING,ERROR,CRITICAL,DEBUG}
                        Verbosity Level; Default: INFO
```
