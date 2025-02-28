# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 15:16:32 2023

@author: 陈梦阳
"""
import requests as s
import json
from time import sleep
from tqdm import tqdm
from sklearn.metrics import accuracy_score, f1_score, recall_score
import openpyxl
from sklearn.metrics import classification_report
from openai import OpenAI
import openai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    retry_if_exception_type
)  # for exponential backoff

@retry(
    retry=retry_if_exception_type((openai.APIError, openai.APIConnectionError, openai.RateLimitError, openai.Timeout,openai.BadRequestError)),
    wait=wait_random_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(10)
)

def chat_completion_with_backoff(**kwargs):
    return openai.ChatCompletion.create(**kwargs)

client = OpenAI(
    # 输入转发API Key
    api_key="sk-ybI42RFALGkBYvTSb8xSFNUL92LbcKfXlWFWYdtaCBPHvfWc",
    base_url="https://api.chatanywhere.com.cn/v1"
)
def chat_completion_with_backoff(**kwargs):
    return client.chat.completions.create(**kwargs)
def detect(prompt):
    completion = chat_completion_with_backoff(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        # stream=True  # 是否开启流式输出
    )
    return completion.choices[0].message.content


# Press the green button in the gutter to run the script.
def read_xlsx_file(file_path):
    workbook = openpyxl.load_workbook(file_path)
    # 选择工作表
    sheet = workbook.active
    # 读取所有行并将它们存储为子列表
    data = []
    for row in sheet.iter_rows():
        row_data = [cell.value for cell in row]
        data.append(row_data)
    return data

def read_tsv_file(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            fields = line.strip().split('\t')
            data.append(fields)
    return data


# 假设你的tsv文件名为 'data.tsv'

data_file_path = 'test_dataset_time.xlsx'
# data_file_path='val.tsv'

# 读取tsv文件
# Data = read_tsv_file(data_file_path)
Data = read_xlsx_file(data_file_path)

test_labels = []
pred = []

claims = []

labels = []

Prompts = []

prompt_1_z = f"Given the following news [claim_text] ,We need you to detect fake news.  \
    please determine whether each of the news is true or false, if it is true, please only answer '1', and if it is false, please only answer 0\
    For each news you must think it step by step and then give your answer from 0 and 1, along with your think process."


prompt_2_z = f"Now you are an annotator to determine whether a given news is fake news.The news is given in the form that 'Is [News] a true news? Answer: [Answer]'.\
 You need to give an answer in the [Answer] slot. There are two available answers that you can choose to fill the slot: 0 and 1,\
  if the news is true, you are supposed to answer 1, otherwise you should answer 0. You have to think step by step and then choose one of the two answers from 1 and 0 and give your thinking process."

prompt_3_z = f"Now we need you to detect fake news.  Below, I will provide you with a news. If the news is true, please reply with 1.If the news is fake, please reply with 0. Please consider the authenticity of the news step by step before replying. Do not reply any other words except 1 and 0."

for n, entry in tqdm(enumerate(Data), total=len(Data)):

    if n >= 1 and entry[3]!=None:
    # if n>=1:
        claim = entry[1]
        claim_label = entry[3]

        claims.append(claim)

        labels.append(claim_label)

Prompts = [prompt_1_z, prompt_2_z,  prompt_3_z]
for i in range(3):
    pred = []
    # if i==0:
    #     for n, claim in tqdm(enumerate(claims), total=len(claims)):
    #         prompts = Prompts[i] + f"Given the news [{claim}] , you are supposed to answer: "
    #
    #         p = detect(prompts)
    #         pred.append(p)
    #         # sleep(3)
    #     p1 = []
    #     l1 = []
    #     for j, text in tqdm(enumerate(pred), total=len(pred)):
    #         if '1' in text and '0' not in text:
    #             output = '1'
    #             p1.append(output)
    #             l1.append(labels[j])
    #         elif '0' in text and '1' not in text:
    #             output = '0'
    #             p1.append(output)
    #             l1.append(labels[j])
    #     # test_labels=convert_list(labels)
    #     p1 = [int(x) for x in p1]
    #     l1 = [int(label) for label in l1]
    #     print("This is " + str(i) + "epoch/n")
    #     print(classification_report(l1, p1, digits=4))
    #     with open("raw+COT_prompt1"+ ".txt", "w", encoding='utf-8') as file:
    #         for n, claim in tqdm(enumerate(claims), total=len(claims)):
    #
    #             if n == 0:
    #
    #                 file.write(
    #                     'claim' + '\t' + 'label' + '\t' + 'pred' + '\n' + str(claim) + '\t' + str(
    #                         labels[n]) + '\t' + str(
    #                         pred[n]) + '\n')
    #             else:
    #                 file.write(str(claim) + '\t' + str(labels[n]) + '\t' + str(pred[n]) + '\n')

    if i ==1:
        for n, claim in tqdm(enumerate(claims), total=len(claims)):
            prompts = Prompts[i] + f" Is [{claim}] a true statement? Your answer is: "

            p = detect(prompts)
            print(p)
            pred.append(p.replace('\n', '').replace('\r', ''))
            # sleep(3)
        p1 = []
        l1 = []
        for j, text in tqdm(enumerate(pred), total=len(pred)):
            if '1' in text and '0' not in text:
                output = '1'
                p1.append(output)
                l1.append(labels[j])
            elif '0' in text and '1' not in text:
                output = '0'
                p1.append(output)
                l1.append(labels[j])
        # test_labels=convert_list(labels)
        p1 = [int(x) for x in p1]
        l1 = [int(label) for label in l1]
        print("This is " + str(i) + "epoch/n")
        print(classification_report(l1, p1, digits=4))

        with open("COT_幻觉" + ".txt", "w", encoding='utf-8') as file:
            for n, claim in tqdm(enumerate(claims), total=len(claims)):

                if n == 0:

                    file.write(
                        'claim' + '\t' + 'label' + '\t' + 'pred' + '\n' + str(claim) + '\t' + str(
                            labels[n]) + '\t' + str(
                            pred[n]) + '\n')
                else:
                    file.write(str(claim) + '\t' + str(labels[n]) + '\t' + str(pred[n]) + '\n')

    # if i ==2:
    #     for n, claim in tqdm(enumerate(claims), total=len(claims)):
    #         prompts = Prompts[
    #                       i] + f" For the news [{claim}], you must judge its authenticity and you can only reply with 0 or 1. So your answer is:"
    #         p = detect(prompts)
    #         pred.append(p)
    #         # sleep(3)
    #     p1 = []
    #     l1 = []
    #     for j, text in tqdm(enumerate(pred), total=len(pred)):
    #         if '1' in text and '0' not in text:
    #             output = '1'
    #             p1.append(output)
    #             l1.append(labels[j])
    #         elif '0' in text and '1' not in text:
    #             output = '0'
    #             p1.append(output)
    #             l1.append(labels[j])
    #     # test_labels=convert_list(labels)
    #     p1 = [int(x) for x in p1]
    #     l1 = [int(label) for label in l1]
    #     print("This is " + str(i) + "epoch/n")
    #     print(classification_report(l1, p1, digits=4))
    #     with open("raw+COT_prompt3"+ ".txt", "w", encoding='utf-8') as file:
    #         for n, claim in tqdm(enumerate(claims), total=len(claims)):
    #
    #             if n == 0:
    #
    #                 file.write(
    #                     'claim' + '\t' + 'label' + '\t' + 'pred' + '\n' + str(claim) + '\t' + str(
    #                         labels[n]) + '\t' + str(
    #                         pred[n]) + '\n')
    #             else:
    #                 file.write(str(claim) + '\t' + str(labels[n]) + '\t' + str(pred[n]) + '\n')