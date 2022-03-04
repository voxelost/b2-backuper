import os
import tarfile
import tempfile
import json

import schedule
import asyncio
from b2sdk.v2 import B2Api


class BucketFile():
    def __init__(self, system_path: str, bucket_path: str) -> None:
        self.system_path = system_path
        self.bucket_path = f"{bucket_path.split(sep='.')[0]}.tar.bz2"

    def create_archive_file(self) -> str:
        archive_file = f'{tempfile.gettempdir()}/{os.path.basename(self.system_path)}.tar.bz2'

        if os.path.exists(archive_file):
            os.remove(archive_file)

        tar = tarfile.open(
            archive_file, 'w:bz2', compresslevel=9)

        tar.add(name=self.system_path, recursive=True)
        tar.close()

        return archive_file

    def cron_job(self, b2_bucket):
        def backup_func():
            b2_bucket.upload_local_file(
                local_file=self.create_archive_file(),
                file_name=self.bucket_path
            )

        return backup_func


class Bucket():
    def __init__(self, name: str, b2_app_key_id: str, b2_app_key: str, backup_time: str, files: list) -> None:
        self.name = name
        self.backup_time = backup_time
        self.bucket_files = [BucketFile(
            system_path=f['system_path'],
            bucket_path=f['bucket_path']
        ) for f in files]

        self.b2_api = B2Api()
        self.b2_api.authorize_account(
            'production', b2_app_key_id, b2_app_key
        )

        self._api_bucket = self.b2_api.get_bucket_by_name(self.name)

        self._cron_jobs = []

        for bucket_file in self.bucket_files:
            self._cron_jobs.append(schedule.every().day.at(self.backup_time).do(
                bucket_file.cron_job(self._api_bucket)))


class BackupManager():
    def __init__(self, config: dict) -> None:
        self._buckets = []

        for b in config['buckets']:
            bucket = Bucket(
                name=b['name'],
                b2_app_key_id=b['b2_app_key_id'],
                b2_app_key=b['b2_app_key'],
                backup_time=b['backup_time'],
                files=b['files']
            )

            self._buckets.append(bucket)

    @classmethod
    def from_file(cls, f: str):
        with open(f, 'r') as fptr:
            return cls(json.loads(fptr.read()))

    async def run(self):
        while True:
            schedule.run_pending()
            await asyncio.sleep(1)
