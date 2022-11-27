import argparse
import errno
import os
import os.path

from pyannote.audio import Model
from pyannote.audio.pipelines import OverlappedSpeechDetection
from pyannote.audio.pipelines import VoiceActivityDetection
from pydub import AudioSegment
from speechbrain.pretrained import SepformerSeparation as separator
import torchaudio


def source_separation(input_wav_path):
    model = separator.from_hparams(source="speechbrain/sepformer-wsj02mix",
                                   savedir='pretrained_models/sepformer-wsj02mix')
    without_extra_slash = os.path.normpath(input_wav_path)
    file_name = os.path.basename(without_extra_slash).removesuffix(".wav")
    # Current wav folder path
    parent_path = os.path.dirname(os.path.normpath(input_wav_path))
    parent_path = os.path.dirname(os.path.normpath(parent_path))

    est_sources = model.separate_file(path=input_wav_path)
    torchaudio.save(f"{parent_path}/{file_name}_a.wav", est_sources[:, :, 0].detach().cpu(), 8000)
    torchaudio.save(f"{parent_path}/{file_name}_b.wav", est_sources[:, :, 1].detach().cpu(), 8000)

    # if os.path.isfile(input_wav_path):
    #   os.remove(input_wav_path)

if __name__ == '__main__':
    path = "/home/orelzam/PycharmProjects/Speaker_Diarization_Deep_learning/OSD/5.258_7.805.wav"
    source_separation(path)
