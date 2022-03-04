from backblaze import BackupManager

import asyncio
import os


async def main() -> None:
    return


if __name__ == '__main__':
    event_loop = asyncio.new_event_loop()

    backup_manager = BackupManager.from_file(
        os.getenv('CONFIG_FILE_NAME', 'config/config.json'))

    event_loop.create_task(main())
    manager_task = event_loop.create_task(backup_manager.run())

    event_loop.run_until_complete(manager_task)
