import io
import json
import os
import requests
import sys
import tarfile

VERSION_URL = "https://ddragon.leagueoflegends.com/api/versions.json"


def get_latest_version():
    version = requests.get(VERSION_URL)
    return json.loads(version.text)[0]


def create_download_url(version):
    default_url = "https://ddragon.leagueoflegends.com/cdn/dragontail-{}.tgz".format(
        version)
    return default_url


def download_url(url, save_path, chunk_size=128):
    print("Downloading file {}...".format(url))
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        if save_path[-1] == "/" or save_path[-1] == "\\":
            fname = save_path + url.split("/")[-1]
        else:
            fname = save_path + "/" + url.split("/")[-1]
        print("... to {}".format(fname))
        with open(fname, 'wb') as f:
            f.write(r.raw.read())
        print("Extracting from {} to {}".format(fname, fname[:-4]))
        tar = tarfile.open(fname, "r:gz")
        tar.extractall(fname[:-4])
        tar.close()


def main():
    version = get_latest_version()
    url = create_download_url(version)
    print(url)
    if len(sys.argv) < 2:
        print("Usage:\n\tpython {} SAVE_PATH".format(os.path.basename(__file__)))
        return
    download_url(url, sys.argv[1])


if __name__ == "__main__":
    main()
