import os.path

from Sample import Sample

from lxml import etree

from os import listdir
import soundfile as sf
import librosa
from tqdm import tqdm

'''
def create_sample(db_path, noise_node):
   path = db_path + os.path.sep + noise_node.xpath("./relativeFilepath")[0].text
   sample_rate = int(noise_node.xpath("./sampleRate")[0].text)
   channels = int(noise_node.xpath("./numChannels")[0].text)
   duration = float(noise_node.xpath("./length")[0].text)
   return Sample(path, sample_rate, channels, duration)

def getAudioData(xml_path):
    tree = etree.parse(xml_path)
    root = tree.getroot()
    db_path = root.find("./databaseFolderPath").text
    tracks = root.findall(".//track")

    samples = list()

    for track in tracks:
        # Get mix and sources
        speech = create_sample(db_path, track.xpath(".//source[sourceName='Speech']")[0])
        mix = create_sample(db_path, track.xpath(".//source[sourceName='Mix']")[0])
        noise = create_sample(db_path, track.xpath(".//source[sourceName='Noise']")[0])

        samples.append((mix, noise, speech))

    return samples
'''

def downsample_all(audio_path, target_sr):
    out_path = audio_path + "_" + str(target_sr)

    if not os.path.exists(out_path):
        os.mkdir(out_path)

    file_list = listdir(audio_path)
    for i in tqdm(range(len(file_list))):
        item = file_list[i]
        file_path = os.path.join(out_path, item)
        if not os.path.exists(file_path):
            y, s = librosa.load(os.path.join(audio_path, item), sr = target_sr)
            sf.write(file_path, y, s)

# not using xml, only have mix and speech data
def create_sample(file_path):
    s, sr = sf.read(file_path)
    duration = s.shape[0] / sr
    return Sample(file_path, sr, 1, duration)

def getAudioData(noisy_path, speech_path):
    samples = list()
    file_list = listdir(noisy_path)

    for i in tqdm(range(len(file_list))):
        noisy = create_sample(os.path.join(noisy_path, item))
        speech = create_sample(os.path.join(speech_path, item))
        
        samples.append((noisy, speech))

    return samples