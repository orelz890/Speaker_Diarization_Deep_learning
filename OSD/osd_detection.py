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


def write_to_lab_and_extract_from_wav(wav_path, writer_to_lab, write_start, write_end, extract_start, extract_end,
                                      overlap_flag):
    writer_to_lab.write(str(write_start) + "\t" + str(write_end) + f"\tspeech\t{overlap_flag}\n")
    extract_sub_recording_from_wav(wav_path, extract_start, extract_end, overlap_flag=overlap_flag)


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
    parser.add_argument('--out-lab-path', type=str, help="Output lab path")
    args = parser.parse_args()

    # SAMPLE_URI = "ES2005a"
    # SAMPLE_WAV = f"../example/audios/16k/{SAMPLE_URI}.wav"
    # SAMPLE_REF = f"../exp/{SAMPLE_URI}.rttm"

    SAMPLE_WAV = args.in_audio_path
    SAMPLE_LAB = args.in_lab_path
    SAMPLE_LAB_OUT = args.out_lab_path

    # 1. visit hf.co/pyannote/segmentation and accept user conditions
    # 2. visit hf.co/settings/tokens to create an access token
    # 3. instantiate pretrained model

    model = Model.from_pretrained("pyannote/segmentation",
                                  use_auth_token="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")

    # Voice activity detection
    pipeline = VoiceActivityDetection(segmentation=model)
    HYPER_PARAMETERS = {
        # onset/offset activation thresholds
        "onset": 0.5, "offset": 0.5,
        # remove speech regions shorter than that many seconds.
        "min_duration_on": 0.0,
        # fill non-speech regions shorter than that many seconds.
        "min_duration_off": 0.0
    }
    pipeline.instantiate(HYPER_PARAMETERS)

    # vad = pipeline(SAMPLE_WAV)
    # `vad` is a pyannote.core.Annotation instance containing speech regions

    # Overlapped speech detection
    pipeline = OverlappedSpeechDetection(segmentation=model)
    pipeline.instantiate(HYPER_PARAMETERS)
    osd = pipeline(SAMPLE_WAV)
    # `osd` is a pyannote.core.Annotation instance containing overlapped speech regions

    # print(len(osd))
    dic = osd.for_json()
    # print(dic)
    # print("\n------------------------------------------------------------\n")

    fixed_value = 0.001
    StartOverlap = []
    EndOverlap = []
    for a in dic['content']:
        for key, value in a['segment'].items():
            if key == 'start':
                StartOverlap.append(round(value, 3))
            elif key == 'end':
                EndOverlap.append(round(value, 3))
    # print("StartOverlaping-> ", StartOverlap)
    # print("EndOverlaping-> ", EndOverlap, "\n------------------------------------------\n")

    # Open the output_folder for the output lab("fixed_vad")
    parent_path = os.path.dirname(os.path.normpath(SAMPLE_LAB_OUT))
    try:
        os.makedirs(parent_path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(parent_path):
            pass
        else:
            raise

    # Start writing the fixed lab file with T/F if there is an overlap + source separation
    # ignoring_value = float('-inf')
    ignoring_value = 1.5
    with open(SAMPLE_LAB, 'r') as reader:
        with open(SAMPLE_LAB_OUT, 'w') as writer:
            i = 0
            for x in reader:
                data = x.split('\t')
                TalkStart = round(float(data[0]), 3)
                TalkEnd = round(float(data[1]), 3)
                flag_las_then_90_sec = False
                if i < len(StartOverlap):
                    if TalkStart <= StartOverlap[i] <= TalkEnd:
                        if EndOverlap[i] < TalkEnd:
                            if EndOverlap[i] - round(StartOverlap[i] + fixed_value, 3) >= ignoring_value:
                                write_to_lab_and_extract_from_wav(SAMPLE_WAV, writer, TalkStart, StartOverlap[i],
                                                                  TalkStart, StartOverlap[i], overlap_flag=False)
                                write_to_lab_and_extract_from_wav(SAMPLE_WAV, writer,
                                                                  round(StartOverlap[i] + fixed_value, 3), EndOverlap[i]
                                                                  , StartOverlap[i], EndOverlap[i], overlap_flag=True)
                                write_to_lab_and_extract_from_wav(SAMPLE_WAV, writer,
                                                                  round(EndOverlap[i] + fixed_value, 3), TalkEnd
                                                                  , EndOverlap[i], TalkEnd, overlap_flag=False)
                            else:
                                write_to_lab_and_extract_from_wav(SAMPLE_WAV, writer, TalkStart, TalkEnd,
                                                                  TalkStart, TalkEnd, overlap_flag=False)
                        else:
                            if TalkEnd - round(StartOverlap[i] + fixed_value, 3) >= ignoring_value:
                                write_to_lab_and_extract_from_wav(SAMPLE_WAV, writer, TalkStart, StartOverlap[i],
                                                                  TalkStart, StartOverlap[i], overlap_flag=False)
                                write_to_lab_and_extract_from_wav(SAMPLE_WAV, writer,
                                                                  round(StartOverlap[i] + fixed_value, 3), TalkEnd,
                                                                  StartOverlap[i], TalkEnd, overlap_flag=True)
                            else:
                                write_to_lab_and_extract_from_wav(SAMPLE_WAV, writer, TalkStart, TalkEnd,
                                                                  TalkStart, TalkEnd, overlap_flag=False)

                    # impossible in our case because the segments r divided by fluent of speech
                    elif StartOverlap[i] <= TalkStart <= EndOverlap[i]:
                        if EndOverlap[i] < TalkEnd:
                            if EndOverlap[i] - TalkStart >= ignoring_value:
                                write_to_lab_and_extract_from_wav(SAMPLE_WAV, writer, TalkStart, EndOverlap[i],
                                                                  TalkStart, EndOverlap[i], overlap_flag=True)
                                write_to_lab_and_extract_from_wav(SAMPLE_WAV, writer,
                                                                  round(EndOverlap[i] + fixed_value, 3), TalkEnd,
                                                                  EndOverlap[i], TalkEnd, overlap_flag=False)
                            else:
                                write_to_lab_and_extract_from_wav(SAMPLE_WAV, writer, TalkStart, TalkEnd,
                                                                  TalkStart, TalkEnd, overlap_flag=False)
                        else:
                            if TalkEnd - TalkStart >= ignoring_value:
                                write_to_lab_and_extract_from_wav(SAMPLE_WAV, writer, TalkStart, TalkEnd,
                                                                  TalkStart, TalkEnd, overlap_flag=True)
                            else:
                                write_to_lab_and_extract_from_wav(SAMPLE_WAV, writer, TalkStart, TalkEnd,
                                                                  TalkStart, TalkEnd, overlap_flag=False)
                    else:
                        write_to_lab_and_extract_from_wav(SAMPLE_WAV, writer, TalkStart, TalkEnd, TalkStart, TalkEnd,
                                                          overlap_flag=False)
                    # Overlap still not over
                    if TalkEnd < EndOverlap[i]:
                        i -= 1
                else:
                    write_to_lab_and_extract_from_wav(SAMPLE_WAV, writer, TalkStart, TalkEnd, TalkStart, TalkEnd,
                                                      overlap_flag=False)
                i += 1
            # print(f"begin = {begging} and duration = {duration}\n")

    # print(overlap)
    # print(len(overlap))

    # # Resegmentation
    # pipeline = Resegmentation(segmentation=model,
    #                           diarization="baseline")
    # pipeline.instantiate(HYPER_PARAMETERS)
    # resegmented_baseline = pipeline({"audio": SAMPLE_WAV, "baseline": vad})
    # # where `baseline` should be provided as a pyannote.core.Annotation instance

    # # Raw scores:
    # inference = Inference(model)
    # segmentation = inference(SAMPLE_WAV)

    # # `segmentation` is a pyannote.core.SlidingWindowFeature
    # # instance containing raw segmentation scores like the
    # # one pictured above (output)
    #
