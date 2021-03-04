from tqdm import tqdm
import os
import sys
import argparse
from urllib.request import urlretrieve
import subprocess
import time


"""
    Google AudioSet data downloader using python only.
    
    Audio set : https://research.google.com/audioset/
    
    prerequist
        youtube-dl
        ffmepg
    
"""

# Meta Data URL
_EVAL_SEGMENTS = "http://storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/eval_segments.csv"
_BALANCED_TRAIN_SEGMENTS = "http://storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/balanced_train_segments.csv"
_UNBALANCED_TRAIN_SEGMENTS = "http://storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/unbalanced_train_segments.csv"
_CLASS_LABEL_INDICES = "http://storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/class_labels_indices.csv"
_META_URL_LIST = [_EVAL_SEGMENTS, _BALANCED_TRAIN_SEGMENTS, _UNBALANCED_TRAIN_SEGMENTS, _CLASS_LABEL_INDICES]

# DATA META FILE LIST
_META_FILE_ROOT = 'meta_data'
_BALANCED_TRAIN_SEGMENTS_FILE = 'balanced_train_segments.csv'
_EVAL_SEGMENTS_FILE = 'eval_segments.csv'
_UNBALANCED_TRAIN_SEGMENTS_FILE = 'unbalanced_train_segments.csv'
_META_DATA_LIST = [_BALANCED_TRAIN_SEGMENTS_FILE, _EVAL_SEGMENTS_FILE, _UNBALANCED_TRAIN_SEGMENTS_FILE]

# CLASS META FILE LIST
_CLASS_LABEL_INDICES_FILE = 'class_labels_indices.csv'
label2class = {}
class2label = {}


def download_metadata():
    """
    Download all meta data
    https://research.google.com/audioset/
    """

    os.makedirs("meta_data", exist_ok = True)
    def reporthook(blocknum, blocksize, totalsize):
        readsofar = blocknum * blocksize
        if totalsize > 0:
            percent = readsofar * 1e2 / totalsize
            s = "\r%5.1f%% %*d / %d" % (
                percent, len(str(totalsize)), readsofar, totalsize)
            sys.stderr.write(s)
            if readsofar >= totalsize:  # near the end
                sys.stderr.write("\n")
        else:  # total size is unknown
            sys.stderr.write("read %d\n" % (readsofar,))

    print("Download Meta data")
    for url in _META_URL_LIST:
        file_name = url.split("/")[-1]

        # exist check
        if os.path.isfile(f"meta_data/{file_name}"):
            print(f"...{file_name} already exist")
            continue
        else:
            print(f"... {file_name}")
            urlretrieve(url, f"meta_data/{file_name}", reporthook)


def wav_from_youtube(youtubeID:str, start_time:int, end_time:int, save_path:str):
    url = f"http://www.youtube.com/v/{youtubeID}?start={start_time}&end={end_time}&version=3"



    # get data url
    command = f'youtube-dl -x --extract-audio --audio-format wav -g "{url}"'
    audio_url, error = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()
    audio_url = audio_url.decode('utf8').replace('\n', '')


    # download and convert wav
    command2 = f"ffmpeg -n -v quiet -i \"{audio_url}\" -ss {start_time} -to {end_time} -ac 2 -f wav {save_path}"

    ''' ffmpeg command
        # -n : if exist do not overwrite
        # -v quiet : quiet mode
        # -i : input file
        # -ss : start second
        # -to : end second
        # -ac 2 : stero 
        # -f wav : format wav
    '''

    subprocess.call(command2, shell = True)


def load_class():
    with open(_CLASS_LABEL_INDICES_FILE, 'r', encoding='utf8') as f:
        indexes = f.readline()
        for line in f.readlines():
            splited = line.replace('\n','').split(',')
            label = splited[1]
            classes = splited[2].replace(' ','_')

            label2class[label]=classes
            class2label[classes]=label


def download_audios_from_metadata(meta_file, meta_root = 'meta_data', save_root = 'data'):

    # file root
    save_path = os.path.join(save_root, meta_file.split('.csv')[0])
    meta_file = os.path.join(meta_root, meta_file)

    # meta file check
    if not os.path.isfile(meta_file):
        raise FileNotFoundError

    # save directory check
    if not os.path.isdir(save_path):
        os.makedirs(save_path, exist_ok = True)
        print(f"create directory : {save_path}")

    # open metafile and download audio
    with open(meta_file, 'r', encoding= 'utf8') as f:
        for _ in range(3):
            print(f.readline().replace('\n',''))

        for line in tqdm(f.readlines()):
            # parsing
            youtubeID, start_time, end_time, classes = line.replace('\n','').split(', ')
            classes = classes.replace("\"", '').split(',')

            # file exist check
            if os.path.isfile(f'{save_path}/audioset{youtubeID}.txt'):
                continue
            # download audio
            audiodata_file = os.path.join(save_path, f'audioset{youtubeID}.wav')
            wav_from_youtube(youtubeID, start_time, end_time, audiodata_file)

            # create class info file
            audioinfo_file = os.path.join(save_path, f'audioset{youtubeID}.txt')
            with open(audioinfo_file, 'w', encoding='utf8') as c:
                c.write(', '.join(classes))

            time.sleep(2.0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--meta', action = 'store',
                        help = 'select meta_data file [eval_segments.csv | balanced_train_segments.csv | unbalanced_train_segments.csv]',
                        default = None, type = str)
    args = parser.parse_args()

    # meta data download
    download_metadata()
    print()

    if args.meta is None:
        for meta_data in _META_DATA_LIST:
            download_audios_from_metadata(meta_data)

    elif args.meta in _META_DATA_LIST:
        download_audios_from_metadata(args.meta)

    else:
        raise FileNotFoundError("check meta file")


if __name__ == '__main__':
    main()

    # import glob
    # wavs = glob.glob(f'data/balanced_train_segments/*.wav')
