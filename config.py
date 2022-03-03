import json


class File():
    def __init__(self, system_path: str, bucket_path: str) -> None:
        self.system_path = system_path
        self.bucket_path = bucket_path

    @classmethod
    def from_dict(cls, d: dict) -> None:
        return cls(system_path=d.get('system_path', ''),
                   bucket_path=d.get('bucket_path', ''))

    def to_dict(self) -> dict:
        return {
            'system_path': self.system_path,
            'bucket_path': self.bucket_path
        }

    def __str__(self) -> str:
        return json.dumps(self.to_dict())


class Bucket():
    def __init__(self, b2_app_key_id: str, b2_app_key: str, cron_string: str, name: str, files: list) -> None:
        self.b2_app_key_id = b2_app_key_id
        self.b2_app_key = b2_app_key
        self.name = name
        self.files = files

    @classmethod
    def from_dict(cls, d: dict) -> None:
        return cls(b2_app_key_id=d.get('b2_app_key_id', ''),
                   b2_app_key=d.get('b2_app_key', ''),
                   cron_string=d.get('cron_string', ''),
                   name=d.get('name', ''),
                   files=[File.from_dict(f) for f in d.get('files', [])])

    def to_dict(self) -> dict:
        return {
            'cron_string': self.cron_string,
            'b2_app_key_id': self.b2_app_key_id,
            'b2_app_key': self.b2_app_key,
            'name': self.name,
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
            'buckets': self.buckets
        }

    def __str__(self) -> str:
        return json.dumps(self.to_dict())
