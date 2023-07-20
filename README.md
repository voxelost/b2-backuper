# b2-backuper

A python script for backuping files and directories on a user-defined hour from within a docker container.
It uses docker's volumes to map selected directories to the container's storage, [bzip2](https://www.sourceware.org/bzip2/) (currently with the highest level of compression enabled) to compress the data and [python backblaze sdk](https://github.com/Backblaze/b2-sdk-python) to authenticate against Backblaze and upload files

To enable backups on your machine you need to have docker and docker-compose installed, for more information see https://docs.docker.com/engine/install/

An example [json config file](example.config.json) was provided, where
```
b2_app_key_id - api app key id obtained from the backblaze panel
b2_app_key    - api app key obtained from the backblaze panel
name          - the name of the bucket (this is globally unique and must match the bucket name set in the backblaze panel)
backup_time   - the time (in format of hh:mm) backups for this bucket are triggered, this should preferably be randomized or set to a time of low traffic on your server
files         - an array of system-bucket file paths where:
  system_path - an in-container path to the file or directory that's going to be compressed and sent to backblaze
  bucket_path - the bucket path, to which the file will be uploaded (WARNING: this filename will always be stripped of any file extensions and a '.tar.bz2' extension will be added for ease of manual decmpression)
```

An example [docker compose file](example.compose.yml) was also provided, you'll need to manually set
```yml
# snip
volumes:
    - /host/machine/directory:/container/directory:ro
```

So a typical setup for a single bucket uploading a single path would look like this:

config.json
```json
{
  "buckets": [
    {
      "b2_app_key_id": "<YOUR_B2_APP_KEY_ID>",
      "b2_app_key": "<YOUR_B2_APP_KEY>",
      "name": "my_awesome_bucket",
      "backup_time": "5:00",
      "files": [
        {
          "system_path": "/app/volumes/docker_volumes",
          "bucket_path": "my_docker_volumes"
        }
      ]
    }
  ]
}
```

docker-compose.yml
```yml
version: "3.8"

services:
  app:
  build: .
  restart: unless-stopped
  volumes:
    - /var/lib/docker/volumes:/app/volumes/docker_volumes:ro
```

It is advised to use a single key pair per bucket with write access only for the purpose of this application.

TODOS:
- [ ] make scheduling more adjustable (perhaps implement cron-like strings)
- [ ] add extended target path naming logic
- [ ] add automatic compressed file removal after a successful upload
- [ ] add an automatic script for generating the docker compose file
- [ ] make compression adjustable (algorithm and compression level preference)
