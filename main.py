from backblaze import BucketFile, BackupManager

import os


if __name__ == '__main__':
    print('im in main')
    # os.environ['CONFIG_FILE_NAME'] = 'config.json'

    backup_manager = BackupManager.from_file(
        os.getenv('CONFIG_FILE_NAME', 'config/config.json'))

    for bucket in backup_manager.buckets:
        backup_manager.backup_bucket_files(bucket=bucket)

    print('exiting')

    while True:
        continue
