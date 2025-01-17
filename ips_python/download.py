import os
import time
import shutil
from pathlib import Path
from ssl import SSLCertVerificationError

import requests
from humanfriendly import format_size

try:
    from ips_python.utils import get_raw_data_filepath
    from ips_python.constants import IATI_FIELDS
except ModuleNotFoundError:
    from utils import get_raw_data_filepath
    from constants import IATI_FIELDS


def get_download_url():
    return f"http://iati.cloud/search/activity?q=*:*&fl={','.join(IATI_FIELDS)}&wt=csv&rows=5000000"


def get_and_write_csv_from_url(url, filename):
    try:
        with requests.get(url, stream=True) as r:
            with open(filename, "wb+") as f:
                shutil.copyfileobj(r.raw, f)
    except (SSLCertVerificationError, requests.exceptions.SSLError) as e:
        print(f"Exception: {e}")
        with requests.get(url, stream=True, verify=False) as r:
            with open(filename, "wb+") as f:
                shutil.copyfileobj(r.raw, f)
    print("Download Complete: {}".format(format_size(os.path.getsize(filename))))


def download_data():
    """
    Downloads the data from the new IATI datastore API
    """
    download_url = get_download_url()
    # check if the file already exists
    raw_data_filepath = get_raw_data_filepath()
    if Path(raw_data_filepath).is_file():
        print(
            "WARNING! There is already a file here of size {}".format(
                format_size(os.path.getsize(raw_data_filepath))
            )
        )
        do_you_want_to_continue = "Do you want to continue? [yes/no]: "
        input_error_message = "Input not understood. Please input 'yes' or 'no'"

        response = input(do_you_want_to_continue).lower()
        print(response)
        while response not in ["yes", "y", "no", "n"]:
            print(input_error_message)
            response = input(do_you_want_to_continue).lower()
        if response in ["yes", "y"]:
            print("Deleting {}".format(raw_data_filepath))
            os.remove(raw_data_filepath)

            print("Downloading data")
            print("WARNING! This may take some time, as the file is over 1GB in size")
            get_and_write_csv_from_url(download_url, raw_data_filepath)
        elif response in ["no", "n"]:
            print("Aborting")
    else:
        print("Downloading data")
        print("WARNING! This may take some time, as the file is over 1GB in size")
        get_and_write_csv_from_url(download_url, raw_data_filepath)


def main():
    start_time = time.time()

    download_data()

    print("completed in {} seconds".format(time.time() - start_time))


if __name__ == "__main__":
    main()
