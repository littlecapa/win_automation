from urllib.error import HTTPError
import os, zipfile
from urllib.request import urlparse, urlretrieve
import requests, time
from env import Environment as e

HTTP_ERROR = int(404)

def concat_pgn_files(path):
    pgn_files = [filename for filename in os.listdir(path) if filename.endswith(".pgn")]
    # Open the output file in write mode
    with open(os.path.join(path, "import.pgn"), "w") as output:
        for pgn_file in pgn_files:
            with open(os.path.join(path, pgn_file), "r") as input_file:
                output.write(input_file.read())
                output.write("\n")
        output.close()
    for pgn_file in pgn_files:
        os.remove(os.path.join(path, pgn_file))
        pass

def readZip(twicNr, baseUrl, folder , attempts):

  filename = "twic" + str(twicNr) + "g.zip"
  url = baseUrl + "/" + filename
  file = folder + "/" + filename
  if not os.path.exists(folder):
    os.mkdir(folder)
  # User Agent is required by TWIC / see https://deviceatlas.com/blog/list-of-user-agent-strings
  ua = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7)'
  for attempt in range(1, attempts+1):
        try:
            print("Try ", url)
            if attempt > 1:
                time.sleep(10)  # 10 seconds wait time between downloads
            with requests.get(url, headers={"User-Agent": ua}, stream=True) as response:
                print ("Status: ", response.status_code)
                if response.status_code == HTTP_ERROR:
                    print ("Ende")
                    concat_pgn_files(folder)
                    return True
                response.raise_for_status()
                with open(file, 'wb') as out_file:
                    print("File open")
                    for chunk in response.iter_content(chunk_size=1024*1024):  # 1MB chunks
                        out_file.write(chunk)
                print("Success")

        except Exception as ex:
            print("Error: ", str(ex))
            raise ex

  with zipfile.ZipFile(file, 'r') as zip_file:
    zip_file.extractall(folder)
  os.remove(file)
  # Noch nicht zu Ende
  return False

if __name__ == "__main__":
    x = e()
    nextIssue = x.get_next_twic_nr()
    while True:
      try:
        last = readZip(nextIssue, baseUrl = x.get_twic_baseurl(), folder = x.get_cbm_import_path(), attempts = x.get_twic_attempts())
        print ("Last: ", str(last), str(nextIssue))
        if last:
            break
      except Exception as ex:
        print ("error: ", str(ex))
        raise ex
      nextIssue +=1

