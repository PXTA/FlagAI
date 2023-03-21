# coding=utf-8
# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Weighted Datasets."""

import sys
import torch

from build_index_mappings import _build_train_valid_test_weighted_datasets

from flagai.data.tokenizer import Tokenizer
model_dir = './'
model_name = "gpt2_new_100k"
cache_dir = model_dir + model_name
tokenizer = Tokenizer.from_pretrained(model_name, cache_dir=cache_dir)
print('tokenizer.token_end_id', tokenizer.token_end_id)

def collate_fn(batch):
    def padding(indice, max_length, pad_idx=tokenizer.token_end_id):
        pad_indice = [
            item.tolist() + [pad_idx] * max(0, max_length - len(item.tolist())) for item in indice
        ]
        return torch.tensor(pad_indice)

    input_ids = [data["input_ids"] for data in batch]
    max_length = max([len(t) for t in input_ids])
    input_ids = padding(input_ids, max_length)[:,:seq_length]

    data = {
        "input_ids": input_ids,
        "labels": input_ids
    }
    return data

if __name__ == '__main__':
    ## weight01, prefix01, weight02, prefix02, ...
    data_prefix = [
        2.7,
        '/share/project/ldwang/data/indexed_dataset/batch1_tok100k/cn_baike_text_document',
        2.91,
        '/share/project/ldwang/data/indexed_dataset/batch1_tok100k/cn_ebook_merge_maxlen_text_document',
        1.89,
        '/share/project/ldwang/data/indexed_dataset/batch1_tok100k/cn_zhihu_text_document',
        1.46,
        '/share/project/ldwang/data/indexed_dataset/batch1_tok100k/cn_wudao_base_text_document',
        1.01,
        '/share/project/ldwang/data/indexed_dataset/batch1_tok100k/cn_wudao_dedup_merged_text_document',
        0.9,
        '/share/project/ldwang/data/indexed_dataset/batch1_tok100k/en_dedup-md5-pile-arxiv_text_document',
        2.5,
        '/share/project/ldwang/data/indexed_dataset/batch1_tok100k/en_dedup-md5-pile-bookcorpus2_text_document',
        1.1,
        '/share/project/ldwang/data/indexed_dataset/batch1_tok100k/en_dedup-md5-pile-books3_text_document',
        1.38,
        '/share/project/ldwang/data/indexed_dataset/batch1_tok100k/en_dedup-md5-pile-gutenberg_pg-19_text_document',
        2.82,
        '/share/project/ldwang/data/indexed_dataset/batch1_tok100k/en_dedup-md5-pile-openwebtext2_text_document',
        1.01,
        '/share/project/ldwang/data/indexed_dataset/batch1_tok100k/en_dedup-md5-pile-pile-cc_text_document',
        0.95,
        '/share/project/ldwang/data/indexed_dataset/batch1_tok100k/en_dedup-md5-pile-pubmed_abstracts_text_document',
        0.95,
        '/share/project/ldwang/data/indexed_dataset/batch1_tok100k/en_dedup-md5-pile-pubmed_central_text_document',
        2.08,
        '/share/project/ldwang/data/indexed_dataset/batch1_tok100k/en_dedup-md5-pile-stackexchange_text_document',
        1.46,
        '/share/project/ldwang/data/indexed_dataset/batch1_tok100k/en_dedup-md5-pile-wikipedia_en_text_document',
    ]
    data_impl = 'mmap'
    ## splits_string len should same as train_valid_test_num_samples len
    splits_string = '9999,1'
    ## rebuilding if no npy files for train_valid_test_num_samples config
    ## 400B
    train_valid_test_num_samples = [390585937, 39063]
    seq_length = 2048
    seed = 2023
    skip_warmup = True

    train_dataset, valid_dataset, _ = _build_train_valid_test_weighted_datasets(
        data_prefix, data_impl, splits_string,
        train_valid_test_num_samples,
        seq_length, seed, skip_warmup)
    print(len(train_dataset))
    print(len(valid_dataset))

    loader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=1,
        sampler=None,
        num_workers=4,
        drop_last=False,
        pin_memory=False,
        prefetch_factor=4,
        collate_fn=collate_fn)
    
    for iteration_, batch in enumerate(loader, 0):
        print(f"step={iteration_}", flush=True)
    print("Ended loader")