#!/bin/bash
export CUDA_DEVICE_MAX_CONNECTIONS=1
DIR=`pwd`

# Guide:
# This script supports distributed training on multi-gpu workers (as well as single-worker training).
# Please set the options below according to the comments.
# For multi-gpu workers training, these options should be manually set for each worker.
# After setting the options, please run the script on each worker.

MODEL="/opt/large-model/qwen/qwen1.5/Qwen1.5-0.5B-Chat/" # Set the path if you do not want to load from huggingface directly
# ATTENTION: specify the path to your training data, which should be a json file consisting of a list of conversations.
# See the section for finetuning in README for more information.
DATA="/opt/large-model/qwen/qwen1.5/Qwen1.5/examples/sft/新车价格问答_2024-03-26_18-22-04.json"

function usage() {
    echo '
Usage: bash finetune/finetune_ds.sh [-m MODEL_PATH] [-d DATA_PATH]
'
}

while [[ "$1" != "" ]]; do
    case $1 in
        -m | --model )
            shift
            MODEL=$1
            ;;
        -d | --data )
            shift
            DATA=$1
            ;;
        -h | --help )
            usage
            exit 0
            ;;
        * )
            echo "Unknown argument ${1}"
            exit 1
            ;;
    esac
    shift
done

export CUDA_VISIBLE_DEVICES=0
# gradient_accumulation_steps 是batch_size的倍数
python \
/opt/large-model/qwen/qwen1.5/Qwen1.5/examples/sft/finetune.py \
    --model_name_or_path $MODEL \
    --data_path $DATA \
    --bf16 True \
    --output_dir /opt/large-model/qwen/qwen1.5/Qwen1.5/examples/sft/output_qwen1.5 \
    --num_train_epochs 20 \
    --per_device_train_batch_size 10 \
    --per_device_eval_batch_size 1 \
    --gradient_accumulation_steps 1 \
    --evaluation_strategy "no" \
    --save_strategy "steps" \
    --save_steps 1000 \
    --save_total_limit 10 \
    --learning_rate 1e-5 \
    --weight_decay 0.1 \
    --adam_beta2 0.95 \
    --warmup_ratio 0.01 \
    --lr_scheduler_type "cosine" \
    --logging_steps 1 \
    --report_to "none" \
    --model_max_length 512 \
    --gradient_checkpointing True \
    --lazy_preprocess True \
    --deepspeed /opt/large-model/qwen/qwen1.5/Qwen1.5/examples/sft/ds_config_zero3.json
