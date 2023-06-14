import os
import sys
import shutil
import filecmp
import schedule
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler

# check if all cli args was given
if len(sys.argv) != 5:
    print('You must provide 4 postional args to sync script:\n'
          'First: Source dir path\n'
          'Second: Replica dir path\n'
          'Third: Log file path\n'
          'Fourth: Sync interval: positive integer')
    sys.exit()

# get cli args
src_path = sys.argv[1]
rpl_path = sys.argv[2]
log_path = sys.argv[3]
interval = int(sys.argv[4])

# setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.propagate = False
handler = RotatingFileHandler(filename=log_path, maxBytes=20000, backupCount=3)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# function for sync dirs
def sync(src, rpl):

    # src/rpl Path obj
    src_dir = Path(src)
    rpl_dir = Path(rpl)

    # filecmp dirs comp obj
    comparison = filecmp.dircmp(src_dir, rpl_dir)

    # Copy files and folders to repl if exist only in the source folder
    for src_only in comparison.left_only:

        # join path and file name
        source_only_path = src_dir / src_only

        # copy dir recurs. from source to repl
        if source_only_path.is_dir():
            shutil.copytree(source_only_path, rpl_dir / src_only)
            print(f"Folder '{src_only}' from the source folder was copied to replica folder.")
            logger.info(f"Folder '{src_only}' from the source folder was copied to replica folder.")

        # copy files from source to repl
        elif source_only_path.is_file():
            shutil.copy2(source_only_path, rpl_dir / src_only)
            print(f"File '{src_only}' from the source folder was copied to the replica folder.")
            logger.info(f"File '{src_only}' from the source folder was copied to the replica folder.")

    # Remove files that exist only in the replica folder
    for rpl_only in comparison.right_only:

        # join path and file name
        rpl_only_path = rpl_dir / rpl_only

        # remove dirs recurs. from repl folder
        if rpl_only_path.is_dir():
            shutil.rmtree(rpl_only_path, rpl_dir / rpl_only)
            print(f"Folder '{rpl_only}' was removed from the replica folder.")
            logger.info(f"Folder '{rpl_only}'was removed from the replica folder.")

        # remove files from repl folder
        elif rpl_only_path.is_file():
            os.remove(os.path.join(rpl_dir, rpl_only))
            print(f"File '{rpl_only}' was removed from replica folder.")
            logger.info(f"File '{rpl_only}' was removed from the replica folder.")

    # Update diff files from source to repl
    for diff_file in comparison.diff_files:
        os.remove(os.path.join(rpl_dir, diff_file))
        shutil.copy2(os.path.join(src_dir, diff_file), os.path.join(rpl_dir, diff_file))
        print(f"File {diff_file} from replica folder was updated successfully.")
        logger.info(f"File {diff_file} from replica folder was updated successfully.")

    # Recursively apply sync function to all sub-dirs
    for sub_cmp in comparison.subdirs.values():
        sync(sub_cmp.left, sub_cmp.right)


# schedule interval sync
if __name__ == '__main__':
    schedule.every(interval).minutes.do(lambda: sync(src_path, rpl_path))

    while True:
        schedule.run_pending()

