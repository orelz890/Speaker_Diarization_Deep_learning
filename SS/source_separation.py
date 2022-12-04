import argparse
import errno
import os
import os.path
from pydub import AudioSegment
from speechbrain.pretrained import SepformerSeparation as separator
import torchaudio


def extract_sub_recording_from_wav(input_wav_path, start, end, overlap_flag):
    without_extra_slash = os.path.normpath(input_wav_path)
    file_name = os.path.basename(without_extra_slash).removesuffix(".wav")
    parent_path = os.path.dirname(os.path.normpath(input_wav_path))

    # If current wav folder or its overlap folder don't exist, make it.
    out_folder = f"{parent_path}/{file_name}"
    try:
        os.makedirs(out_folder)
        if overlap_flag:
            os.makedirs(f"{out_folder}/overlap")
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(out_folder) or overlap_flag:
            if overlap_flag:
                try:
                    os.makedirs(f"{out_folder}/overlap")
                except OSError as exc2:
                    if exc2.errno == errno.EEXIST and os.path.isdir(f"{out_folder}/overlap"):
                        pass
                    else:
                        raise
            pass
        else:
            raise

    # Extraction
    t1 = start * 1000  # Works in milliseconds
    t2 = end * 1000
    newAudio = AudioSegment.from_wav(input_wav_path)
    newAudio = newAudio[t1:t2]
    if overlap_flag:
        newAudio.export(f'{out_folder}/overlap/{start}_{end}.wav',
                        format="wav")  # Exports to a wav file in the current path.
        source_separation(f'{out_folder}/overlap/{start}_{end}.wav')
        # Adding to the combined wav
        combine_wav(f"{out_folder}/{start}_{end}_a.wav", out_folder, f"{file_name}_combined")
        combine_wav(f"{out_folder}/{start}_{end}_b.wav", out_folder, f"{file_name}_combined")
    else:
        newAudio.export(f'{out_folder}/{start}_{end}.wav',
                        format="wav")  # Exports to a wav file in the current path.
        # Adding to the combined wav
        combine_wav(f'{out_folder}/{start}_{end}.wav', out_folder, f"{file_name}_combined")


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


def combine_wav(addition_wav_path, out_folder_path, new_wav_name):
    try:
        os.makedirs(out_folder_path)
        os.makedirs(f"{out_folder_path}/combined")
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and (os.path.isdir(out_folder_path) or os.path.isdir(f"{out_folder_path}/combined")):
            if os.path.isdir(out_folder_path):
                try:
                    os.makedirs(f"{out_folder_path}/combined")
                except OSError as exc2:
                    if exc2.errno == errno.EEXIST and os.path.isdir(f"{out_folder_path}/combined"):
                        pass
                    else:
                        raise
            pass
        else:
            raise
    # Check if a combined wav exist
    is_exist = os.path.exists(f"{out_folder_path}/combined/{new_wav_name}.wav")
    # This can cause trouble.. try:
    # silence = AudioSegment.from_wav(os.path.abspath("../example/audios/output_16k/silence.wav"))
    parent_path = os.path.abspath("..")
    silence = AudioSegment.from_wav(f"{parent_path}/Speaker_Diarization_Deep_learning/example/audios/output_16k/silence.wav")
    out_wav_path = f"{out_folder_path}/combined/{new_wav_name}.wav"
    # print(f"out_wav_path = {out_wav_path}")
    if is_exist:
        # Add silence to the last output
        sound1 = AudioSegment.from_wav(out_wav_path)
        combined_sounds = sound1 + silence
        combined_sounds.export(out_wav_path, format="wav")
        # Add the new addition
        # print(f"Additional path = {addition_wav_path}")
        sound1 = AudioSegment.from_wav(out_wav_path)
        sound2 = AudioSegment.from_wav(addition_wav_path)
        combined_sounds = sound1 + sound2
        combined_sounds.export(out_wav_path, format="wav")
    else:
        sound1 = AudioSegment.from_wav(addition_wav_path)
        sound1.export(out_wav_path, format="wav")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--in-audio-path', type=str, help="Input audio path")
    parser.add_argument('--in-lab-path', type=str, help="Input lab path")
    args = parser.parse_args()

    SAMPLE_WAV = args.in_audio_path
    SAMPLE_LAB = args.in_lab_path

    ignoring_value = 1.5
    with open(SAMPLE_LAB, 'r') as reader:
            i = 0
            for x in reader:
                data = x.split('\t')
                TalkStart = round(float(data[0]), 3)
                TalkEnd = round(float(data[1]), 3)
                overlap_flag = False
                if data[3].replace("\n", "") == "True":
                    overlap_flag = True
                # print(data[3].replace("\n", "") == "True", ">>>>>> ", overlap_flag)
                extract_sub_recording_from_wav(SAMPLE_WAV, TalkStart, TalkEnd, overlap_flag)
