#!/usr/bin/env bash


#CDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
#
#mkdir -p exp
#
##for audio in $(ls Signals/Bed002)
#for audio in $(ls example/audios/16k)
#do
#  filename=$(echo "${audio}" | cut -f 1 -d '.')
#  if [[ -d "example/audios/16k/${filename}" ]]
#  then
#      echo "This dir already exists.."
#  else
#      echo ${filename} > exp/list.txt
#
#      # Creating the lab file
#      python VAD/energy_VAD.py \
#          --in-audio-dir example/audios/16k\
#          --vad-out-dir example/vad \
#          --list exp/list.txt \
#          --in-format ${filename}.lab
#
#      # Overlap speech detection + making a new lab accordingly
#      python OSD/osd_detection.py \
#          --in-audio-path example/audios/16k/${filename}.wav\
#          --in-lab-path  example/vad/${filename}.lab\
#          --out-lab-path  example/fixed_vad/${filename}.lab
#
#      # Source separation
#      python SS/source_separation.py \
#          --in-audio-path example/audios/16k/${filename}.wav\
#          --in-lab-path  example/fixed_vad/${filename}.lab\
#
#      echo ${filename}_combined > exp/list.txt
#
#      # Creating the lab file
#      python VAD/energy_VAD.py \
#          --in-audio-dir example/audios/16k/${filename}/combined \
#          --vad-out-dir example/audios/16k/${filename}/vad \
#          --wav-name ${filename}_combined \
#          --list exp/list.txt \
#          --in-format ${filename}.lab
#
#
#
###
###      python OSD/separate_labs.py\
###        --in-lab-path example/audios/16k/${filename}/vad/${filename}_combined.lab\
###        --out-regular-lab-path example/audios/16k/${filename}/vad/${filename}_regular.lab\
###        --out-overlap-lab-path example/audios/16k/${filename}/vad/${filename}_overlap.lab
##
##
##
##      # run feature and x-vectors extraction
##      python VBx/predict.py \
##          --in-file-list exp/list.txt \
##          --in-lab-dir example/audios/16k/${filename}/vad \
##          --in-wav-dir example/audios/16k/${filename}/combined \
##          --out-ark-fn exp/${filename}.ark \
##          --out-seg-fn exp/${filename}.seg \
##          --weights VBx/models/ResNet101_16kHz/nnet/final.onnx \
##          --backend onnx

#
#      # run variational bayes on top of x-vectors
#      python VBx/vbhmm.py \
#          --init AHC+VB \
#          --out-rttm-dir exp/${filename}\
#          --xvec-ark-file exp/${filename}.ark \
#          --segments-file exp/${filename}.seg \
#          --xvec-transform VBx/models/ResNet101_16kHz/transform.h5 \
#          --plda-file VBx/models/ResNet101_16kHz/plda \
#          --threshold -0.015 \
#          --lda-dim 128 \
#          --Fa 0.3 \
#          --Fb 17 \
#          --loopP 0.99
#
#
#      # check if there is ground truth .rttm file
#      if [ -f example/rttm/${filename}.rttm ]
#      then
#          # run dscore
#          python dscore/score.py -r example/rttm/${filename}.rttm -s exp/${filename}.rttm --collar 0.25 --ignore_overlaps
#      fi
#  fi
#done



# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Working well <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


CDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

mkdir -p exp

# shellcheck disable=SC2045
for audio in $(ls example/audios/16k)
do
      filename=$(echo "${audio}" | cut -f 1 -d '.')
      echo ${filename} > exp/list.txt

       # Creating the lab file
      python VAD/energy_VAD.py \
          --in-audio-dir example/audios/16k\
          --vad-out-dir example/vad \
          --list exp/list.txt \
          --in-format ${filename}.lab

      # Overlap speech detection
      python OSD/osd_detection.py \
          --in-audio-path example/audios/16k/${filename}.wav\
          --in-lab-path  example/vad/${filename}.lab\
          --out-lab-path  example/fixed_vad/${filename}.lab

      # run feature and x-vectors extraction
      python VBx/predict.py \
          --in-file-list exp/list.txt \
          --in-lab-dir example/fixed_vad \
          --in-wav-dir example/audios/16k \
          --out-ark-fn exp/${filename}.ark \
          --out-seg-fn exp/${filename}.seg \
          --weights VBx/models/ResNet101_16kHz/nnet/final.onnx \
          --backend onnx

      # run variational bayes on top of x-vectors
      python VBx/vbhmm.py \
          --init AHC+VB \
          --out-rttm-dir exp/${filename}\
          --xvec-ark-file exp/${filename}.ark \
          --segments-file exp/${filename}.seg \
          --xvec-transform VBx/models/ResNet101_16kHz/transform.h5 \
          --plda-file VBx/models/ResNet101_16kHz/plda \
          --threshold -0.015 \
          --lda-dim 128 \
          --Fa 0.3 \
          --Fb 17 \
          --loopP 0.99

#      # Overlap speech detection
#      python OSD/osd_detection.py \
#          --in-audio-path example/audios/16k/${filename}.wav\
#          --in-rttm-path  exp/${filename}/${filename}.rttm \

      # check if there is ground truth .rttm file
      if [ -f example/rttm/${filename}.rttm ]
      then
          # run dscore
          python dscore/score.py -r example/rttm/${filename}.rttm -s exp/${filename}/${filename}.rttm --collar 0.25 --ignore_overlaps
      fi
done