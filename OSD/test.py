# import argparse
# import errno
# import os
# import os.path
#
# from pyannote.audio import Model
# from pyannote.audio.pipelines import OverlappedSpeechDetection
# from pyannote.audio.pipelines import VoiceActivityDetection
# from pydub import AudioSegment
# from speechbrain.pretrained import SepformerSeparation as separator
# import torchaudio
#
# SAMPLE_URI = "blabla"
#
# SAMPLE_REF = f"../exp/{SAMPLE_URI}.rttm"
# from speechbrain.pretrained import SepformerSeparation as separator
# import torchaudio
#
#
# def extract_sub_recording_from_wav(input_wav_path: str, start: float, end: float, overlap_flag=True):
#     without_extra_slash = os.path.normpath(input_wav_path)
#     file_name = os.path.basename(without_extra_slash).removesuffix(".wav")
#     parent_path = os.path.dirname(os.path.normpath(input_wav_path))
#     out_folder = f"{parent_path}/{file_name}"
#     try:
#         os.makedirs(out_folder)
#         if overlap_flag:
#             os.makedirs(f"{out_folder}/overlap")
#     except OSError as exc:  # Python >2.5
#         if exc.errno == errno.EEXIST and os.path.isdir(out_folder):
#             if overlap_flag:
#                 os.makedirs(f"{out_folder}/overlap")
#                 if exc.errno == errno.EEXIST and os.path.isdir(f"{out_folder}/overlap"):
#                     pass
#                 else:
#                     raise
#             pass
#         else:
#             raise
#
#     t1 = start * 1000  # Works in milliseconds
#     t2 = end * 1000
#     newAudio = AudioSegment.from_wav(input_wav_path)
#     newAudio = newAudio[t1:t2]
#     if overlap_flag:
#         newAudio.export(f'{out_folder}/overlap/{start}_{end}.wav',
#                         format="wav")  # Exports to a wav file in the current path.
#     else:
#         newAudio.export(f'{out_folder}/{start}_{end}.wav',
#                         format="wav")  # Exports to a wav file in the current path.
#
#
# import errno
# import os
# from pydub import AudioSegment
#
#
# def combine_wav(addition_wav_path, out_folder_path, new_wav_name):
#     try:
#         os.makedirs(out_folder_path)
#     except OSError as exc:  # Python >2.5
#         if exc.errno == errno.EEXIST and os.path.isdir(out_folder_path):
#             pass
#         else:
#             raise
#     # print(f"is exist = {out_folder_path}/{new_wav_name}.wav")
#     is_exist = os.path.exists(f"{out_folder_path}/{new_wav_name}.wav")
#     silence = AudioSegment.from_wav("/home/orelzam/PycharmProjects/pythonProject/Speaker_Diarization_project/example/audios/output_16k/silence.wav")
#     out_wav_path = f"{out_folder_path}/{new_wav_name}.wav"
#     # print(f"out_wav_path = {out_wav_path}")
#     if is_exist:
#         # Add silence to the last output
#         sound1 = AudioSegment.from_wav(out_wav_path)
#         combined_sounds = sound1 + silence
#         combined_sounds.export(out_wav_path, format="wav")
#         # Add the new addition
#         # print(f"Additional path = {addition_wav_path}")
#         sound1 = AudioSegment.from_wav(out_wav_path)
#         sound2 = AudioSegment.from_wav(addition_wav_path)
#         combined_sounds = sound1 + sound2
#         combined_sounds.export(out_wav_path, format="wav")
#     else:
#         sound1 = AudioSegment.from_wav(addition_wav_path)
#         sound1.export(out_wav_path, format="wav")
#
#
#
# # def aggregate_wav(wav_name, input_path, out_path, out_wav):
# #
# #     for wav in input_path:
# #
# #         combine_wav(sound1_name, sound2_name, out_folder, out_wav)
#
# if __name__ == '__main__':
#     my_init_wav = "/home/orelzam/PycharmProjects/pythonProject/Speaker_Diarization_project/OSD/ES2005a.wav"
#     input_wav_path = "/home/orelzam/PycharmProjects/pythonProject/Speaker_Diarization_project/OSD/0.0_2.57.wav"
#     input_wav_path2 = "/home/orelzam/PycharmProjects/pythonProject/Speaker_Diarization_project/OSD/5.3.19_3.94.wav"
#     out_path = "/home/orelzam/PycharmProjects/pythonProject/Speaker_Diarization_project/OSD"
#     new_wav_name = "aaa"
#     combine_wav(input_wav_path, out_path, new_wav_name)
#     input_wav_path3 = "/home/orelzam/PycharmProjects/pythonProject/Speaker_Diarization_project/OSD/5.258_7.805.wav"
#     combine_wav(input_wav_path2, out_path, new_wav_name)
#     combine_wav(input_wav_path3, out_path, new_wav_name)
#
#     # extract_sub_recording_from_wav(my_init_wav, 274, 274.5, False)
