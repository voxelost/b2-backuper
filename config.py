import json


class BucketFile():
    def __init__(self, name: str, cron_str: str, b2_argument: str, system_path: str, bucket_path: str) -> None:
        self.name = name
        self.cron_str = cron_str
        self.b2_argument = b2_argument
        self.system_path = system_path
        self.bucket_path = bucket_path

    @classmethod
    def from_dict(cls, d: dict) -> None:
        return cls(
            name=d.get('name', ''),
            cron_str=d.get('cron_str', ''),
            b2_argument=d.get('b2_argument', 'upload_file'),
            system_path=d.get('system_path', ''),
            bucket_path=d.get('bucket_path', '')
        )

    @classmethod
    def from_bucket_file(cls, bucket_file):
        return cls(
            name=bucket_file.name,
            cron_str=bucket_file.cron_str,
            b2_argument=bucket_file.b2_argument,
            system_path=bucket_file.system_path,
            bucket_path=bucket_file.bucket_path
        )

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'cron_str': self.cron_str,
            'b2_argument': self.b2_argument,
            'system_path': self.system_path,
            'bucket_path': self.bucket_path
        }

    def __str__(self) -> str:
        return json.dumps(self.to_dict())


class Bucket():
    def __init__(self, b2_app_key_id: str, b2_app_key: str, files: list) -> None:
        self.b2_app_key_id = b2_app_key_id
        self.b2_app_key = b2_app_key
        self.files = files

    @classmethod
    def from_dict(cls, d: dict) -> None:
        return cls(b2_app_key_id=d.get('b2_app_key_id', ''),
                   b2_app_key=d.get('b2_app_key', ''),
                   files=[BucketFile.from_dict(f) for f in d.get('files', [])])

    def to_dict(self) -> dict:
        return {
            'b2_app_key_id': self.b2_app_key_id,
            'b2_app_key': self.b2_app_key,
            'files': [f.to_dict() for f in self.files]
        }

    def __str__(self) -> str:
        return json.dumps(self.to_dict())


class Config():
    def __init__(self, buckets: list) -> None:
        self.buckets = buckets

    @classmethod
    def from_dict(cls, d: dict):
        return cls(buckets=[Bucket.from_dict(b) for b in d.get('buckets', [])])

    @classmethod
    def from_file(cls, f: str):
        with open(f, 'r') as fptr:
            return cls.from_dict(json.loads(fptr.read()))

    def to_dict(self) -> dict:
        return {
            'buckets': [b.to_dict() for b in self.buckets]
        }

    def __str__(self) -> str:
        return json.dumps(self.to_dict())
