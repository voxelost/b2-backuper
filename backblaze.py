from datetime import datetime
import os
import tarfile
import tempfile
import json

from apscheduler.schedulers.blocking import BlockingScheduler
from b2sdk.v2 import B2Api


class BucketFile():
    def __init__(self, cron_str: str, system_path: str, bucket_path: str) -> None:
        self.cron_str = cron_str
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

    def register_job(self):
        def backup_func():
            print(f'job triggered, {datetime.now()}')
            self._api_bucket.upload_local_file(
                local_file=self.create_archive_file(),
                file_name=self.bucket_path
            )
        return backup_func


class Bucket():
    def __init__(self, name: str, b2_app_key_id: str, b2_app_key: str, files: list) -> None:
        self.name = name
        self.bucket_files = [BucketFile(
            cron_str=f['cron_str'],
            system_path=f['system_path'],
            bucket_path=f['bucket_path']
        ) for f in files]

        self.b2_api = B2Api()
        self.b2_api.authorize_account(
            'production', b2_app_key_id, b2_app_key
        )

        self._api_bucket = self.b2_api.get_bucket_by_name(self.name)

    def add_bucket_file(self, file: BucketFile) -> None:
        self.bucket_files.append(file)

    def remove_bucket_file(self, file: BucketFile) -> None:
        self.bucket_files.pop(file)

    def setup_cron_jobs(self, scheduler: BlockingScheduler):
        for bucket_file in self.bucket_files:

            scheduler.add_job(bucket_file.register_job(),
                              'interval', seconds=5)


class BackupManager():
    def __init__(self, config: dict) -> None:
        self._buckets = []
        self.scheduler = BlockingScheduler()
        self.scheduler.add_executor('processpool')

        for b in config['buckets']:
            bucket = Bucket(
                name=b['name'],
                b2_app_key_id=b['b2_app_key_id'],
                b2_app_key=b['b2_app_key'],
                files=b['files']
            )

            bucket.setup_cron_jobs(self.scheduler)
            self._buckets.append(bucket)

        self.scheduler.start()

    @classmethod
    def from_file(cls, f: str):
        with open(f, 'r') as fptr:
            return cls(json.loads(fptr.read()))

    def backup_bucket_files(self, bucket: Bucket) -> None:
        bucket.setup_backup_funcs()

    def run(self) -> None:
        print('running backblaze manager')
