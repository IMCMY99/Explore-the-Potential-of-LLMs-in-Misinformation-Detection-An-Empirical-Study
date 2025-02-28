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
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        # stream=True  # 是否开启流式输出
    )
    return completion.choices[0].message.content

print(detect('你好'))

print(detect('有什么办法可以让你记住上次对话？'))

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

prompt_1_0 = f"Given the following news [claim_text] ,We need you to detect fake news.\
     please determine whether each of the news is true or false, if it is true, please only answer '1', and if you cannot determine whether it is correct, please only answer 0\
    Do not reply any words other than 0 or 1, for each news you must give your answer."
prompt_1_1 = f"Given the following news [claim_text] ,We need you to detect fake news.  \
        please determine whether each of the news is true or false, if it is true, please only answer '1', and if you cannot determine whether it is correct, please only answer 0\
    Here are some examples of fake news examples:\
        News: [No Evidence Lisa Loring's Cause of Death Was COVID-19 Vaccine]  , Answer:[0]\
    Here are some examples of true news examples:\
        News: [A photo shows Ukrainian soldiers posing in front of a NATO flag, an Azov flag, and the swastika-bearing flag once used by the Hitler Youth] , Answer:[1]\
        Do not reply any words other than 0 or 1, for each news you must give your answer."
prompt_1_2=f"Given the following news [claim_text] ,We need you to detect fake news.  \
        please determine whether each of the news is true or false, if it is true, please only answer '1', and if you cannot determine whether it is correct, please only answer 0\
    Here are some examples of fake news examples:\
        News: [No Evidence Lisa Loring's Cause of Death Was COVID-19 Vaccine]  , Answer:[0]\
        News: [AP: Diamond's Cause of Death Was Heart Disease, Not COVID-19 Vaccine]  , Answer:[0]\
   Here are some examples of true news examples:\
        News: [A video authentically shows a March 2023 incident involving a U.S. surveillance drone and Russian Su-27 fighter jets]  , Answer:[1]\
        News: [A photo shows Ukrainian soldiers posing in front of a NATO flag, an Azov flag, and the swastika-bearing flag once used by the Hitler Youth] ,  Answer:[1]\
        Do not reply any words other than 0 or 1, for each news you must give your answer."


prompt_1_3 = f"Given the following news [claim_text] ,We need you to detect fake news.  \
        please determine whether each of the news is true or false, if it is true, please only answer '1', and if you cannot determine whether it is correct, please only answer 0\
    Here are some examples of fake news examples:\
        News: [No Evidence Lisa Loring's Cause of Death Was COVID-19 Vaccine]  , Answer:[0]\
        News: [AP: Diamond's Cause of Death Was Heart Disease, Not COVID-19 Vaccine]  , Answer:[0]\
        News: [The U.S. Department of Defense awarded a contract for COVID-19 research in Ukraine months before the virus was known.] ,  Answer:[0]\
   Here are some examples of true news examples:\
        News: [A photo shows Ukrainian soldiers posing in front of a NATO flag, an Azov flag, and the swastika-bearing flag once used by the Hitler Youth] , Answer:[1]\
        News: [A video authentically shows a March 2023 incident involving a U.S. surveillance drone and Russian Su-27 fighter jets]  , Answer:[1]\
        News: [HIV is contagious.] , Answer:[1]\
    Do not reply any words other than 0 or 1, for each news you must give your answer."

prompt_1_4=f"Given the following news [claim_text] ,We need you to detect fake news.  \
        please determine whether each of the news is true or false, if it is true, please only answer '1', and if you cannot determine whether it is correct, please only answer 0\
    Here are some examples of fake news examples:\
        News: [No Evidence Lisa Loring's Cause of Death Was COVID-19 Vaccine]  , Answer:[0]\
        News: [AP: Diamond's Cause of Death Was Heart Disease, Not COVID-19 Vaccine]  , Answer:[0]\
        News: [The U.S. Department of Defense awarded a contract for COVID-19 research in Ukraine months before the virus was known.] ,  Answer:[0]\
        News: [9 Doctored Pics and Deepfakes of Volodymyr Zelenskyy.]  ,  Answer:[0]\
   Here are some examples of true news examples:\
        News: [A photo shows Ukrainian soldiers posing in front of a NATO flag, an Azov flag, and the swastika-bearing flag once used by the Hitler Youth] , Answer:[1]\
        News: [A video authentically shows a March 2023 incident involving a U.S. surveillance drone and Russian Su-27 fighter jets]  , Answer:[1]\
        News: [HIV is contagious.] , Answer:[1]\
        News: [A video accurately depicts the eruption of the Shiveluch volcano in Russia, in which vast dust clouds engulf the sky. ] , Answer:[1]\
    Do not reply any words other than 0 or 1, for each news you must give your answer."

prompt_1_5=f"Given the following claims [claim_text], \
        please determine whether each of the claims is true or false, if it is true, please only answer '1', and if you cannot determine whether it is correct, please only answer 0\
    Here are some examples of fake news examples:\
        News: [No Evidence Lisa Loring's Cause of Death Was COVID-19 Vaccine]  , Answer:[0]\
        News: [AP: Diamond's Cause of Death Was Heart Disease, Not COVID-19 Vaccine]  , Answer:[0]\
        News: [The U.S. Department of Defense awarded a contract for COVID-19 research in Ukraine months before the virus was known.] ,  Answer:[0]\
        News: [9 Doctored Pics and Deepfakes of Volodymyr Zelenskyy.]  ,  Answer:[0]\
        News: [Explained: Secret American and NATO Ukraine Plans Came From Discord Server.] ,  Answer:[0]\
    Here are some examples of true news examples:\
        News: [A photo shows Ukrainian soldiers posing in front of a NATO flag, an Azov flag, and the swastika-bearing flag once used by the Hitler Youth] , Answer:[1]\
        News: [A video authentically shows a March 2023 incident involving a U.S. surveillance drone and Russian Su-27 fighter jets]  , Answer:[1]\
        News: [HIV is contagious.] , Answer:[1]\
        News: [A video accurately depicts the eruption of the Shiveluch volcano in Russia, in which vast dust clouds engulf the sky. ] , Answer:[1]\
        News: [A factory in Pennsylvania produces ammunition for the Ukrainian military.] , Answer:[1]\
    Do not reply any words other than 0 or 1, for each news you must give your answer."

prompt_1_6=f"Given the following claims [claim_text], \
        please determine whether each of the claims is true or false, if it is true, please only answer '1', and if you cannot determine whether it is correct, please only answer 0\
    Here are some examples of fake news examples:\
        News: [No Evidence Lisa Loring's Cause of Death Was COVID-19 Vaccine]  , Answer:[0]\
        News: [AP: Diamond's Cause of Death Was Heart Disease, Not COVID-19 Vaccine]  , Answer:[0]\
        News: [The U.S. Department of Defense awarded a contract for COVID-19 research in Ukraine months before the virus was known.] ,  Answer:[0]\
        News: [9 Doctored Pics and Deepfakes of Volodymyr Zelenskyy.]  ,  Answer:[0]\
        News: [Explained: Secret American and NATO Ukraine Plans Came From Discord Server.] ,  Answer:[0]\
        News: [In September 2021, Walmart Canada announced that, beginning in November, in-store customers would be required to show proof of vaccination against COVID-19.] , Answer:[0]\
    Here are some examples of true news examples:\
        News: [A photo shows Ukrainian soldiers posing in front of a NATO flag, an Azov flag, and the swastika-bearing flag once used by the Hitler Youth] , Answer:[1]\
        News: [A video authentically shows a March 2023 incident involving a U.S. surveillance drone and Russian Su-27 fighter jets]  , Answer:[1]\
        News: [HIV is contagious.] , Answer:[1]\
        News: [A video accurately depicts the eruption of the Shiveluch volcano in Russia, in which vast dust clouds engulf the sky. ] , Answer:[1]\
        News: [A factory in Pennsylvania produces ammunition for the Ukrainian military.] , Answer:[1]\
        News: [Members of Congress and their staffers are not subject to the federal vaccine mandate imposed by the Biden administration in September 2021.] , Answer:[1]\
    Do not reply any words other than 0 or 1, for each news you must give your answer."

prompt_1_7=f"Given the following claims [claim_text], \
        please determine whether each of the claims is true or false, if it is true, please only answer '1', and if you cannot determine whether it is correct, please only answer 0\
    Here are some examples of fake news examples:\
        News: [No Evidence Lisa Loring's Cause of Death Was COVID-19 Vaccine]  , Answer:[0]\
        News: [AP: Diamond's Cause of Death Was Heart Disease, Not COVID-19 Vaccine]  , Answer:[0]\
        News: [The U.S. Department of Defense awarded a contract for COVID-19 research in Ukraine months before the virus was known.] ,  Answer:[0]\
        News: [9 Doctored Pics and Deepfakes of Volodymyr Zelenskyy.]  ,  Answer:[0]\
        News: [Explained: Secret American and NATO Ukraine Plans Came From Discord Server.] ,  Answer:[0]\
        News: [In September 2021, Walmart Canada announced that, beginning in November, in-store customers would be required to show proof of vaccination against COVID-19.] , Answer:[0]\
        News: [COVID Researchers: Racial Disparities In Vaccine Booster Rates Persist.]  , Answer:[0]\
    Here are some examples of true news examples:\
        News: [A photo shows Ukrainian soldiers posing in front of a NATO flag, an Azov flag, and the swastika-bearing flag once used by the Hitler Youth] , Answer:[1]\
        News: [A video authentically shows a March 2023 incident involving a U.S. surveillance drone and Russian Su-27 fighter jets]  , Answer:[1]\
        News: [HIV is contagious.] , Answer:[1]\
        News: [A video accurately depicts the eruption of the Shiveluch volcano in Russia, in which vast dust clouds engulf the sky. ] , Answer:[1]\
        News: [A factory in Pennsylvania produces ammunition for the Ukrainian military.] , Answer:[1]\
        News: [Members of Congress and their staffers are not subject to the federal vaccine mandate imposed by the Biden administration in September 2021.] , Answer:[1]\
        News: [Sen. Marco Rubio 'helped write the law to raise prescription prices'.] , Answer:[1]\
    Do not reply any words other than 0 or 1, for each news you must give your answer."

prompt_1_8=f"Given the following claims [claim_text], \
        please determine whether each of the claims is true or false, if it is true, please only answer '1', and if you cannot determine whether it is correct, please only answer 0\
    Here are some examples of fake news examples:\
        News: [No Evidence Lisa Loring's Cause of Death Was COVID-19 Vaccine]  , Answer:[0]\
        News: [AP: Diamond's Cause of Death Was Heart Disease, Not COVID-19 Vaccine]  , Answer:[0]\
        News: [The U.S. Department of Defense awarded a contract for COVID-19 research in Ukraine months before the virus was known.] ,  Answer:[0]\
        News: [9 Doctored Pics and Deepfakes of Volodymyr Zelenskyy.]  ,  Answer:[0]\
        News: [Explained: Secret American and NATO Ukraine Plans Came From Discord Server.] ,  Answer:[0]\
        News: [In September 2021, Walmart Canada announced that, beginning in November, in-store customers would be required to show proof of vaccination against COVID-19.] , Answer:[0]\
        News: [COVID Researchers: Racial Disparities In Vaccine Booster Rates Persist.]  , Answer:[0]\
        News: [Viral 'Ukraine Windows' Photo Didn't Show Whole Picture.] , Answer:[0]\
    Here are some examples of true news examples:\
        News: [A photo shows Ukrainian soldiers posing in front of a NATO flag, an Azov flag, and the swastika-bearing flag once used by the Hitler Youth] , Answer:[1]\
        News: [A video authentically shows a March 2023 incident involving a U.S. surveillance drone and Russian Su-27 fighter jets]  , Answer:[1]\
        News: [HIV is contagious.] , Answer:[1]\
        News: [A video accurately depicts the eruption of the Shiveluch volcano in Russia, in which vast dust clouds engulf the sky. ] , Answer:[1]\
        News: [A factory in Pennsylvania produces ammunition for the Ukrainian military.] , Answer:[1]\
        News: [Members of Congress and their staffers are not subject to the federal vaccine mandate imposed by the Biden administration in September 2021.] , Answer:[1]\
        News: [Sen. Marco Rubio 'helped write the law to raise prescription prices'.] , Answer:[1]\
        News: [COVID-19 vaccine maker Moderna is a sponsor of the 2022 U.S. Open tennis tournament.] , Answer:[1]\
    Do not reply any words other than 0 or 1, for each news you must give your answer."

prompt_1_9=f"Given the following claims [claim_text], \
        please determine whether each of the claims is true or false, if it is true, please only answer '1', and if you cannot determine whether it is correct, please only answer 0\
    Here are some examples of fake news examples:\
        News: [No Evidence Lisa Loring's Cause of Death Was COVID-19 Vaccine]  , Answer:[0]\
        News: [AP: Diamond's Cause of Death Was Heart Disease, Not COVID-19 Vaccine]  , Answer:[0]\
        News: [The U.S. Department of Defense awarded a contract for COVID-19 research in Ukraine months before the virus was known.] ,  Answer:[0]\
        News: [9 Doctored Pics and Deepfakes of Volodymyr Zelenskyy.]  ,  Answer:[0]\
        News: [Explained: Secret American and NATO Ukraine Plans Came From Discord Server.] ,  Answer:[0]\
        News: [In September 2021, Walmart Canada announced that, beginning in November, in-store customers would be required to show proof of vaccination against COVID-19.] , Answer:[0]\
        News: [COVID Researchers: Racial Disparities In Vaccine Booster Rates Persist.]  , Answer:[0]\
        News: [Viral 'Ukraine Windows' Photo Didn't Show Whole Picture.] , Answer:[0]\
        News: [Says 86% of COVID-19 cases in Israel in July were in fully vaccinated individuals.] , Answer:[0]\
    Here are some examples of true news examples:\
        News: [A photo shows Ukrainian soldiers posing in front of a NATO flag, an Azov flag, and the swastika-bearing flag once used by the Hitler Youth] , Answer:[1]\
        News: [A video authentically shows a March 2023 incident involving a U.S. surveillance drone and Russian Su-27 fighter jets]  , Answer:[1]\
        News: [HIV is contagious.] , Answer:[1]\
        News: [A video accurately depicts the eruption of the Shiveluch volcano in Russia, in which vast dust clouds engulf the sky. ] , Answer:[1]\
        News: [A factory in Pennsylvania produces ammunition for the Ukrainian military.] , Answer:[1]\
        News: [Members of Congress and their staffers are not subject to the federal vaccine mandate imposed by the Biden administration in September 2021.] , Answer:[1]\
        News: [Sen. Marco Rubio 'helped write the law to raise prescription prices'.] , Answer:[1]\
        News: [COVID-19 vaccine maker Moderna is a sponsor of the 2022 U.S. Open tennis tournament.] , Answer:[1]\
        News: [‘The pharmaceutical industry has 1,400 lobbyists on Capitol Hill right now trying to stop’ Medicare drug price negotiation.] , Answer:[1]\
    Do not reply any words other than 0 or 1, for each news you must give your answer."



prompt_2_0 = f"Now you are an annotator to determine whether a given news is fake news.The news is given in the form that 'Is [News] a true news? Answer: [Answer]'.\
 You need to give an answer in the [Answer] slot. There are two available answers that you can choose to fill the slot: 0 and 1,\
  if the news is true, you are supposed to answer 1, otherwise you should answer 0. You have to choose one of the two answers from 1 and 0. No need to answer any other words expect 1 and 0. "
prompt_2_1 = f"Now you are an annotator to determine whether a given news is fake news. The news is given in the form that 'Is [News] a true news? Answer: [Answer]'.\
 You need to give an answer in the [Answer] slot. There are two available answers that you can choose to fill the slot: 0 and 1, \
 if the news is true, you are supposed to answer 1, otherwise you should answer 0. \
     Here are some examples of fake news examples:\
        News: [No Evidence Lisa Loring's Cause of Death Was COVID-19 Vaccine]  , Answer:[0]\
    Here are some examples of true news examples:\
        News: [A photo shows Ukrainian soldiers posing in front of a NATO flag, an Azov flag, and the swastika-bearing flag once used by the Hitler Youth] , Answer:[1]\
    You have to choose one of the two answers from 1 and 0. No need to answer any other words expect 1 and 0."
prompt_2_2=f"Now you are an annotator to determine whether a given news is fake news. The news is given in the form that 'Is [News] a true news? Answer: [Answer]'.\
 You need to give an answer in the [Answer] slot. There are two available answers that you can choose to fill the slot: 0 and 1, \
 if the news is true, you are supposed to answer 1, otherwise you should answer 0. \
   Here are some examples of fake news examples:\
        News: [No Evidence Lisa Loring's Cause of Death Was COVID-19 Vaccine]  , Answer:[0]\
        News: [AP: Diamond's Cause of Death Was Heart Disease, Not COVID-19 Vaccine]  , Answer:[0]\
   Here are some examples of true news examples:\
        News: [A photo shows Ukrainian soldiers posing in front of a NATO flag, an Azov flag, and the swastika-bearing flag once used by the Hitler Youth] , Answer:[1]\
        News: [A video authentically shows a March 2023 incident involving a U.S. surveillance drone and Russian Su-27 fighter jets]  , Answer:[1]\
    You have to choose one of the two answers from 1 and 0. No need to answer any other words expect 1 and 0."

prompt_2_3=f"Now you are an annotator to determine whether a given news is fake news. The news is given in the form that 'Is [News] a true news? Answer: [Answer]'.\
 You need to give an answer in the [Answer] slot. There are two available answers that you can choose to fill the slot: 0 and 1, \
 if the news is true, you are supposed to answer 1, otherwise you should answer 0. \
    Here are some examples of fake news examples:\
        News: [No Evidence Lisa Loring's Cause of Death Was COVID-19 Vaccine]  , Answer:[0]\
        News: [AP: Diamond's Cause of Death Was Heart Disease, Not COVID-19 Vaccine]  , Answer:[0]\
        News: [The U.S. Department of Defense awarded a contract for COVID-19 research in Ukraine months before the virus was known.] ,  Answer:[0]\
   Here are some examples of true news examples:\
        News: [A photo shows Ukrainian soldiers posing in front of a NATO flag, an Azov flag, and the swastika-bearing flag once used by the Hitler Youth] , Answer:[1]\
        News: [A video authentically shows a March 2023 incident involving a U.S. surveillance drone and Russian Su-27 fighter jets]  , Answer:[1]\
        News: [HIV is contagious.] , Answer:[1]\
    You have to choose one of the two answers from 1 and 0. No need to answer any other words expect 1 and 0."

prompt_2_4=f"Now you are an annotator to determine whether a given news is fake news. The news is given in the form that 'Is [News] a true news? Answer: [Answer]'.\
 You need to give an answer in the [Answer] slot. There are two available answers that you can choose to fill the slot: 0 and 1, \
 if the news is true, you are supposed to answer 1, otherwise you should answer 0. \
    Here are some examples of fake news examples:\
        News: [No Evidence Lisa Loring's Cause of Death Was COVID-19 Vaccine]  , Answer:[0]\
        News: [AP: Diamond's Cause of Death Was Heart Disease, Not COVID-19 Vaccine]  , Answer:[0]\
        News: [The U.S. Department of Defense awarded a contract for COVID-19 research in Ukraine months before the virus was known.] ,  Answer:[0]\
        News: [9 Doctored Pics and Deepfakes of Volodymyr Zelenskyy.]  ,  Answer:[0]\
   Here are some examples of true news examples:\
        News: [A photo shows Ukrainian soldiers posing in front of a NATO flag, an Azov flag, and the swastika-bearing flag once used by the Hitler Youth] , Answer:[1]\
        News: [A video authentically shows a March 2023 incident involving a U.S. surveillance drone and Russian Su-27 fighter jets]  , Answer:[1]\
        News: [HIV is contagious.] , Answer:[1]\
        News: [A video accurately depicts the eruption of the Shiveluch volcano in Russia, in which vast dust clouds engulf the sky. ] , Answer:[1]\
    You have to choose one of the two answers from 1 and 0. No need to answer any other words expect 1 and 0."

prompt_2_5=f"Now you are an annotator to determine whether a given news is fake news. The news is given in the form that 'Is [News] a true news? Answer: [Answer]'.\
 You need to give an answer in the [Answer] slot. There are two available answers that you can choose to fill the slot: 0 and 1, \
 if the news is true, you are supposed to answer 1, otherwise you should answer 0. \
    Here are some examples of fake news examples:\
        News: [No Evidence Lisa Loring's Cause of Death Was COVID-19 Vaccine]  , Answer:[0]\
        News: [AP: Diamond's Cause of Death Was Heart Disease, Not COVID-19 Vaccine]  , Answer:[0]\
        News: [The U.S. Department of Defense awarded a contract for COVID-19 research in Ukraine months before the virus was known.] ,  Answer:[0]\
        News: [9 Doctored Pics and Deepfakes of Volodymyr Zelenskyy.]  ,  Answer:[0]\
        News: [Explained: Secret American and NATO Ukraine Plans Came From Discord Server.] ,  Answer:[0]\
    Here are some examples of true news examples:\
        News: [A photo shows Ukrainian soldiers posing in front of a NATO flag, an Azov flag, and the swastika-bearing flag once used by the Hitler Youth] , Answer:[1]\
        News: [A video authentically shows a March 2023 incident involving a U.S. surveillance drone and Russian Su-27 fighter jets]  , Answer:[1]\
        News: [HIV is contagious.] , Answer:[1]\
        News: [A video accurately depicts the eruption of the Shiveluch volcano in Russia, in which vast dust clouds engulf the sky. ] , Answer:[1]\
        News: [A factory in Pennsylvania produces ammunition for the Ukrainian military.] , Answer:[1]\
    You have to choose one of the two answers from 1 and 0. No need to answer any other words expect 1 and 0."


prompt_2_6=f"Now you are an annotator to determine whether a given news is fake news. The news is given in the form that 'Is [News] a true news? Answer: [Answer]'.\
 You need to give an answer in the [Answer] slot. There are two available answers that you can choose to fill the slot: 0 and 1, \
 if the news is true, you are supposed to answer 1, otherwise you should answer 0. \
    Here are some examples of fake news examples:\
        News: [No Evidence Lisa Loring's Cause of Death Was COVID-19 Vaccine]  , Answer:[0]\
        News: [AP: Diamond's Cause of Death Was Heart Disease, Not COVID-19 Vaccine]  , Answer:[0]\
        News: [The U.S. Department of Defense awarded a contract for COVID-19 research in Ukraine months before the virus was known.] ,  Answer:[0]\
        News: [9 Doctored Pics and Deepfakes of Volodymyr Zelenskyy.]  ,  Answer:[0]\
        News: [Explained: Secret American and NATO Ukraine Plans Came From Discord Server.] ,  Answer:[0]\
        News: [In September 2021, Walmart Canada announced that, beginning in November, in-store customers would be required to show proof of vaccination against COVID-19.] , Answer:[0]\
    Here are some examples of true news examples:\
        News: [A photo shows Ukrainian soldiers posing in front of a NATO flag, an Azov flag, and the swastika-bearing flag once used by the Hitler Youth] , Answer:[1]\
        News: [A video authentically shows a March 2023 incident involving a U.S. surveillance drone and Russian Su-27 fighter jets]  , Answer:[1]\
        News: [HIV is contagious.] , Answer:[1]\
        News: [A video accurately depicts the eruption of the Shiveluch volcano in Russia, in which vast dust clouds engulf the sky. ] , Answer:[1]\
        News: [A factory in Pennsylvania produces ammunition for the Ukrainian military.] , Answer:[1]\
        News: [Members of Congress and their staffers are not subject to the federal vaccine mandate imposed by the Biden administration in September 2021.] , Answer:[1]\
    You have to choose one of the two answers from 1 and 0. No need to answer any other words expect 1 and 0."


prompt_2_7=f"Now you are an annotator to determine whether a given news is fake news. The news is given in the form that 'Is [News] a true news? Answer: [Answer]'.\
 You need to give an answer in the [Answer] slot. There are two available answers that you can choose to fill the slot: 0 and 1, \
 if the news is true, you are supposed to answer 1, otherwise you should answer 0. \
    Here are some examples of fake news examples:\
        News: [No Evidence Lisa Loring's Cause of Death Was COVID-19 Vaccine]  , Answer:[0]\
        News: [AP: Diamond's Cause of Death Was Heart Disease, Not COVID-19 Vaccine]  , Answer:[0]\
        News: [The U.S. Department of Defense awarded a contract for COVID-19 research in Ukraine months before the virus was known.] ,  Answer:[0]\
        News: [9 Doctored Pics and Deepfakes of Volodymyr Zelenskyy.]  ,  Answer:[0]\
        News: [Explained: Secret American and NATO Ukraine Plans Came From Discord Server.] ,  Answer:[0]\
        News: [In September 2021, Walmart Canada announced that, beginning in November, in-store customers would be required to show proof of vaccination against COVID-19.] , Answer:[0]\
        News: [COVID Researchers: Racial Disparities In Vaccine Booster Rates Persist.]  , Answer:[0]\
    Here are some examples of true news examples:\
        News: [A photo shows Ukrainian soldiers posing in front of a NATO flag, an Azov flag, and the swastika-bearing flag once used by the Hitler Youth] , Answer:[1]\
        News: [A video authentically shows a March 2023 incident involving a U.S. surveillance drone and Russian Su-27 fighter jets]  , Answer:[1]\
        News: [HIV is contagious.] , Answer:[1]\
        News: [A video accurately depicts the eruption of the Shiveluch volcano in Russia, in which vast dust clouds engulf the sky. ] , Answer:[1]\
        News: [A factory in Pennsylvania produces ammunition for the Ukrainian military.] , Answer:[1]\
        News: [Members of Congress and their staffers are not subject to the federal vaccine mandate imposed by the Biden administration in September 2021.] , Answer:[1]\
        News: [Sen. Marco Rubio 'helped write the law to raise prescription prices'.] , Answer:[1]\
    You have to choose one of the two answers from 1 and 0. No need to answer any other words expect 1 and 0."

prompt_2_8=f"Now you are an annotator to determine whether a given news is fake news. The news is given in the form that 'Is [News] a true news? Answer: [Answer]'.\
 You need to give an answer in the [Answer] slot. There are two available answers that you can choose to fill the slot: 0 and 1, \
 if the news is true, you are supposed to answer 1, otherwise you should answer 0. \
    Here are some examples of fake news examples:\
        News: [No Evidence Lisa Loring's Cause of Death Was COVID-19 Vaccine]  , Answer:[0]\
        News: [AP: Diamond's Cause of Death Was Heart Disease, Not COVID-19 Vaccine]  , Answer:[0]\
        News: [The U.S. Department of Defense awarded a contract for COVID-19 research in Ukraine months before the virus was known.] ,  Answer:[0]\
        News: [9 Doctored Pics and Deepfakes of Volodymyr Zelenskyy.]  ,  Answer:[0]\
        News: [Explained: Secret American and NATO Ukraine Plans Came From Discord Server.] ,  Answer:[0]\
        News: [In September 2021, Walmart Canada announced that, beginning in November, in-store customers would be required to show proof of vaccination against COVID-19.] , Answer:[0]\
        News: [COVID Researchers: Racial Disparities In Vaccine Booster Rates Persist.]  , Answer:[0]\
        News: [Viral 'Ukraine Windows' Photo Didn't Show Whole Picture.] , Answer:[0]\
    Here are some examples of true news examples:\
        News: [A photo shows Ukrainian soldiers posing in front of a NATO flag, an Azov flag, and the swastika-bearing flag once used by the Hitler Youth] , Answer:[1]\
        News: [A video authentically shows a March 2023 incident involving a U.S. surveillance drone and Russian Su-27 fighter jets]  , Answer:[1]\
        News: [HIV is contagious.] , Answer:[1]\
        News: [A video accurately depicts the eruption of the Shiveluch volcano in Russia, in which vast dust clouds engulf the sky. ] , Answer:[1]\
        News: [A factory in Pennsylvania produces ammunition for the Ukrainian military.] , Answer:[1]\
        News: [Members of Congress and their staffers are not subject to the federal vaccine mandate imposed by the Biden administration in September 2021.] , Answer:[1]\
        News: [Sen. Marco Rubio 'helped write the law to raise prescription prices'.] , Answer:[1]\
        News: [COVID-19 vaccine maker Moderna is a sponsor of the 2022 U.S. Open tennis tournament.] , Answer:[1]\
    You have to choose one of the two answers from 1 and 0. No need to answer any other words expect 1 and 0."

prompt_2_9=f"Now you are an annotator to determine whether a given news is fake news. The news is given in the form that 'Is [News] a true news? Answer: [Answer]'.\
 You need to give an answer in the [Answer] slot. There are two available answers that you can choose to fill the slot: 0 and 1, \
 if the news is true, you are supposed to answer 1, otherwise you should answer 0. \
    Here are some examples of fake news examples:\
        News: [No Evidence Lisa Loring's Cause of Death Was COVID-19 Vaccine]  , Answer:[0]\
        News: [AP: Diamond's Cause of Death Was Heart Disease, Not COVID-19 Vaccine]  , Answer:[0]\
        News: [The U.S. Department of Defense awarded a contract for COVID-19 research in Ukraine months before the virus was known.] ,  Answer:[0]\
        News: [9 Doctored Pics and Deepfakes of Volodymyr Zelenskyy.]  ,  Answer:[0]\
        News: [Explained: Secret American and NATO Ukraine Plans Came From Discord Server.] ,  Answer:[0]\
        News: [In September 2021, Walmart Canada announced that, beginning in November, in-store customers would be required to show proof of vaccination against COVID-19.] , Answer:[0]\
        News: [COVID Researchers: Racial Disparities In Vaccine Booster Rates Persist.]  , Answer:[0]\
        News: [Viral 'Ukraine Windows' Photo Didn't Show Whole Picture.] , Answer:[0]\
        News: [Says 86% of COVID-19 cases in Israel in July were in fully vaccinated individuals.] , Answer:[0]\
    Here are some examples of true news examples:\
        News: [A photo shows Ukrainian soldiers posing in front of a NATO flag, an Azov flag, and the swastika-bearing flag once used by the Hitler Youth] , Answer:[1]\
        News: [A video authentically shows a March 2023 incident involving a U.S. surveillance drone and Russian Su-27 fighter jets]  , Answer:[1]\
        News: [HIV is contagious.] , Answer:[1]\
        News: [A video accurately depicts the eruption of the Shiveluch volcano in Russia, in which vast dust clouds engulf the sky. ] , Answer:[1]\
        News: [A factory in Pennsylvania produces ammunition for the Ukrainian military.] , Answer:[1]\
        News: [Members of Congress and their staffers are not subject to the federal vaccine mandate imposed by the Biden administration in September 2021.] , Answer:[1]\
        News: [Sen. Marco Rubio 'helped write the law to raise prescription prices'.] , Answer:[1]\
        News: [COVID-19 vaccine maker Moderna is a sponsor of the 2022 U.S. Open tennis tournament.] , Answer:[1]\
        News: ['The pharmaceutical industry has 1,400 lobbyists on Capitol Hill right now trying to stop' Medicare drug price negotiation.] , Answer:[1]\
    You have to choose one of the two answers from 1 and 0. No need to answer any other words expect 1 and 0."


prompt_3_0 = f"Now we need you to detect fake news.  Below, I will provide you with a news. If the news is true, please reply with 1.If the news is fake, please reply with 0. Do not reply any other words except 1 and 0."


prompt_3_1 =  f"Now we need you to detect fake news. Below, I will provide you with a news. If the news is true, please reply with 1.If the news is false, please reply with 0. Do not reply any other words except 1 and 0.\
        Here are some examples of fake news examples:\
        News: [No Evidence Lisa Loring's Cause of Death Was COVID-19 Vaccine]  , Answer:[0]\
    Here are some examples of true news examples:\
        News: [A photo shows Ukrainian soldiers posing in front of a NATO flag, an Azov flag, and the swastika-bearing flag once used by the Hitler Youth] , Answer:[1]\
        "
prompt_3_2 = f"Now we need you to detect fake news.  Below, I will provide you with a news. If the news is true, please reply with 1.If the news is false, please reply with 0. Do not reply any other words except 1 and 0.\
    Here are some examples of fake news examples:\
        News: [No Evidence Lisa Loring's Cause of Death Was COVID-19 Vaccine]  , Answer:[0]\
        News: [AP: Diamond's Cause of Death Was Heart Disease, Not COVID-19 Vaccine]  , Answer:[0]\
   Here are some examples of true news examples:\
        News: [A video authentically shows a March 2023 incident involving a U.S. surveillance drone and Russian Su-27 fighter jets]  , Answer:[1]\
        News: [A photo shows Ukrainian soldiers posing in front of a NATO flag, an Azov flag, and the swastika-bearing flag once used by the Hitler Youth] ,  Answer:[1]\
        "


prompt_3_3 = f"Now we need you to detect fake news.  Below, I will provide you with a news. If the news is true, please reply with 1.If the news is false, please reply with 0. Do not reply any other words except 1 and 0.\
        Here are some examples of fake news examples:\
        News: [No Evidence Lisa Loring's Cause of Death Was COVID-19 Vaccine]  , Answer:[0]\
        News: [AP: Diamond's Cause of Death Was Heart Disease, Not COVID-19 Vaccine]  , Answer:[0]\
        News: [The U.S. Department of Defense awarded a contract for COVID-19 research in Ukraine months before the virus was known.] ,  Answer:[0]\
   Here are some examples of true news examples:\
        News: [A photo shows Ukrainian soldiers posing in front of a NATO flag, an Azov flag, and the swastika-bearing flag once used by the Hitler Youth] , Answer:[1]\
        News: [A video authentically shows a March 2023 incident involving a U.S. surveillance drone and Russian Su-27 fighter jets]  , Answer:[1]\
        News: [HIV is contagious.] , Answer:[1]\
        "

prompt_3_4= f"Now we need you to detect fake news.  Below, I will provide you with a news. If the news is true, please reply with 1.If the news is false, please reply with 0. Do not reply any other words except 1 and 0.\
        Here are some examples of fake news examples:\
        News: [No Evidence Lisa Loring's Cause of Death Was COVID-19 Vaccine]  , Answer:[0]\
        News: [AP: Diamond's Cause of Death Was Heart Disease, Not COVID-19 Vaccine]  , Answer:[0]\
        News: [The U.S. Department of Defense awarded a contract for COVID-19 research in Ukraine months before the virus was known.] ,  Answer:[0]\
        News: [9 Doctored Pics and Deepfakes of Volodymyr Zelenskyy.]  ,  Answer:[0]\
   Here are some examples of true news examples:\
        News: [A photo shows Ukrainian soldiers posing in front of a NATO flag, an Azov flag, and the swastika-bearing flag once used by the Hitler Youth] , Answer:[1]\
        News: [A video authentically shows a March 2023 incident involving a U.S. surveillance drone and Russian Su-27 fighter jets]  , Answer:[1]\
        News: [HIV is contagious.] , Answer:[1]\
        News: [A video accurately depicts the eruption of the Shiveluch volcano in Russia, in which vast dust clouds engulf the sky. ] , Answer:[1]\
        "

prompt_3_5 = f"Now we need you to detect fake news. Below, I will provide you with a news. If the news is true, please reply with 1.If the news is false, please reply with 0. Do not reply any other words except 1 and 0.\
       Here are some examples of fake news examples:\
        News: [No Evidence Lisa Loring's Cause of Death Was COVID-19 Vaccine]  , Answer:[0]\
        News: [AP: Diamond's Cause of Death Was Heart Disease, Not COVID-19 Vaccine]  , Answer:[0]\
        News: [The U.S. Department of Defense awarded a contract for COVID-19 research in Ukraine months before the virus was known.] ,  Answer:[0]\
        News: [9 Doctored Pics and Deepfakes of Volodymyr Zelenskyy.]  ,  Answer:[0]\
        News: [Explained: Secret American and NATO Ukraine Plans Came From Discord Server.] ,  Answer:[0]\
    Here are some examples of true news examples:\
        News: [A photo shows Ukrainian soldiers posing in front of a NATO flag, an Azov flag, and the swastika-bearing flag once used by the Hitler Youth] , Answer:[1]\
        News: [A video authentically shows a March 2023 incident involving a U.S. surveillance drone and Russian Su-27 fighter jets]  , Answer:[1]\
        News: [HIV is contagious.] , Answer:[1]\
        News: [A video accurately depicts the eruption of the Shiveluch volcano in Russia, in which vast dust clouds engulf the sky. ] , Answer:[1]\
        News: [A factory in Pennsylvania produces ammunition for the Ukrainian military.] , Answer:[1]\
        "

prompt_3_6=f"Now we need you to detect fake news. Below, I will provide you with a news. If the news is true, please reply with 1.If the news is false, please reply with 0. Do not reply any other words except 1 and 0.\
       Here are some examples of fake news examples:\
        News: [No Evidence Lisa Loring's Cause of Death Was COVID-19 Vaccine]  , Answer:[0]\
        News: [AP: Diamond's Cause of Death Was Heart Disease, Not COVID-19 Vaccine]  , Answer:[0]\
        News: [The U.S. Department of Defense awarded a contract for COVID-19 research in Ukraine months before the virus was known.] ,  Answer:[0]\
        News: [9 Doctored Pics and Deepfakes of Volodymyr Zelenskyy.]  ,  Answer:[0]\
        News: [Explained: Secret American and NATO Ukraine Plans Came From Discord Server.] ,  Answer:[0]\
        News: [In September 2021, Walmart Canada announced that, beginning in November, in-store customers would be required to show proof of vaccination against COVID-19.] , Answer:[0]\
    Here are some examples of true news examples:\
        News: [A photo shows Ukrainian soldiers posing in front of a NATO flag, an Azov flag, and the swastika-bearing flag once used by the Hitler Youth] , Answer:[1]\
        News: [A video authentically shows a March 2023 incident involving a U.S. surveillance drone and Russian Su-27 fighter jets]  , Answer:[1]\
        News: [HIV is contagious.] , Answer:[1]\
        News: [A video accurately depicts the eruption of the Shiveluch volcano in Russia, in which vast dust clouds engulf the sky. ] , Answer:[1]\
        News: [A factory in Pennsylvania produces ammunition for the Ukrainian military.] , Answer:[1]\
        News: [Members of Congress and their staffers are not subject to the federal vaccine mandate imposed by the Biden administration in September 2021.] , Answer:[1]\
        "

prompt_3_7=f"Now we need you to detect fake news. Below, I will provide you with a news. If the news is true, please reply with 1.If the news is false, please reply with 0. Do not reply any other words except 1 and 0.\
       Here are some examples of fake news examples:\
        News: [No Evidence Lisa Loring's Cause of Death Was COVID-19 Vaccine]  , Answer:[0]\
        News: [AP: Diamond's Cause of Death Was Heart Disease, Not COVID-19 Vaccine]  , Answer:[0]\
        News: [The U.S. Department of Defense awarded a contract for COVID-19 research in Ukraine months before the virus was known.] ,  Answer:[0]\
        News: [9 Doctored Pics and Deepfakes of Volodymyr Zelenskyy.]  ,  Answer:[0]\
        News: [Explained: Secret American and NATO Ukraine Plans Came From Discord Server.] ,  Answer:[0]\
        News: [In September 2021, Walmart Canada announced that, beginning in November, in-store customers would be required to show proof of vaccination against COVID-19.] , Answer:[0]\
        News: [COVID Researchers: Racial Disparities In Vaccine Booster Rates Persist.]  , Answer:[0]\
    Here are some examples of true news examples:\
        News: [A photo shows Ukrainian soldiers posing in front of a NATO flag, an Azov flag, and the swastika-bearing flag once used by the Hitler Youth] , Answer:[1]\
        News: [A video authentically shows a March 2023 incident involving a U.S. surveillance drone and Russian Su-27 fighter jets]  , Answer:[1]\
        News: [HIV is contagious.] , Answer:[1]\
        News: [A video accurately depicts the eruption of the Shiveluch volcano in Russia, in which vast dust clouds engulf the sky. ] , Answer:[1]\
        News: [A factory in Pennsylvania produces ammunition for the Ukrainian military.] , Answer:[1]\
        News: [Members of Congress and their staffers are not subject to the federal vaccine mandate imposed by the Biden administration in September 2021.] , Answer:[1]\
        News: [Sen. Marco Rubio 'helped write the law to raise prescription prices'.] , Answer:[1]\
        "

prompt_3_8=f"Now we need you to detect fake news. Below, I will provide you with a news. If the news is true, please reply with 1.If the news is false, please reply with 0. Do not reply any other words except 1 and 0.\
       Here are some examples of fake news examples:\
        News: [No Evidence Lisa Loring's Cause of Death Was COVID-19 Vaccine]  , Answer:[0]\
        News: [AP: Diamond's Cause of Death Was Heart Disease, Not COVID-19 Vaccine]  , Answer:[0]\
        News: [The U.S. Department of Defense awarded a contract for COVID-19 research in Ukraine months before the virus was known.] ,  Answer:[0]\
        News: [9 Doctored Pics and Deepfakes of Volodymyr Zelenskyy.]  ,  Answer:[0]\
        News: [Explained: Secret American and NATO Ukraine Plans Came From Discord Server.] ,  Answer:[0]\
        News: [In September 2021, Walmart Canada announced that, beginning in November, in-store customers would be required to show proof of vaccination against COVID-19.] , Answer:[0]\
        News: [COVID Researchers: Racial Disparities In Vaccine Booster Rates Persist.]  , Answer:[0]\
        News: [Viral 'Ukraine Windows' Photo Didn't Show Whole Picture.] , Answer:[0]\
    Here are some examples of true news examples:\
        News: [A photo shows Ukrainian soldiers posing in front of a NATO flag, an Azov flag, and the swastika-bearing flag once used by the Hitler Youth] , Answer:[1]\
        News: [A video authentically shows a March 2023 incident involving a U.S. surveillance drone and Russian Su-27 fighter jets]  , Answer:[1]\
        News: [HIV is contagious.] , Answer:[1]\
        News: [A video accurately depicts the eruption of the Shiveluch volcano in Russia, in which vast dust clouds engulf the sky. ] , Answer:[1]\
        News: [A factory in Pennsylvania produces ammunition for the Ukrainian military.] , Answer:[1]\
        News: [Members of Congress and their staffers are not subject to the federal vaccine mandate imposed by the Biden administration in September 2021.] , Answer:[1]\
        News: [Sen. Marco Rubio 'helped write the law to raise prescription prices'.] , Answer:[1]\
        News: [COVID-19 vaccine maker Moderna is a sponsor of the 2022 U.S. Open tennis tournament.] , Answer:[1]\
        "
prompt_3_9=f"Now we need you to detect fake news. Below, I will provide you with a news. If the news is true, please reply with 1.If the news is false, please reply with 0. Do not reply any other words except 1 and 0.\
       Here are some examples of fake news examples:\
        News: [No Evidence Lisa Loring's Cause of Death Was COVID-19 Vaccine]  , Answer:[0]\
        News: [AP: Diamond's Cause of Death Was Heart Disease, Not COVID-19 Vaccine]  , Answer:[0]\
        News: [The U.S. Department of Defense awarded a contract for COVID-19 research in Ukraine months before the virus was known.] ,  Answer:[0]\
        News: [9 Doctored Pics and Deepfakes of Volodymyr Zelenskyy.]  ,  Answer:[0]\
        News: [Explained: Secret American and NATO Ukraine Plans Came From Discord Server.] ,  Answer:[0]\
        News: [In September 2021, Walmart Canada announced that, beginning in November, in-store customers would be required to show proof of vaccination against COVID-19.] , Answer:[0]\
        News: [COVID Researchers: Racial Disparities In Vaccine Booster Rates Persist.]  , Answer:[0]\
        News: [Viral 'Ukraine Windows' Photo Didn't Show Whole Picture.] , Answer:[0]\
        News: [Says 86% of COVID-19 cases in Israel in July were in fully vaccinated individuals.] , Answer:[0]\
    Here are some examples of true news examples:\
        News: [A photo shows Ukrainian soldiers posing in front of a NATO flag, an Azov flag, and the swastika-bearing flag once used by the Hitler Youth] , Answer:[1]\
        News: [A video authentically shows a March 2023 incident involving a U.S. surveillance drone and Russian Su-27 fighter jets]  , Answer:[1]\
        News: [HIV is contagious.] , Answer:[1]\
        News: [A video accurately depicts the eruption of the Shiveluch volcano in Russia, in which vast dust clouds engulf the sky. ] , Answer:[1]\
        News: [A factory in Pennsylvania produces ammunition for the Ukrainian military.] , Answer:[1]\
        News: [Members of Congress and their staffers are not subject to the federal vaccine mandate imposed by the Biden administration in September 2021.] , Answer:[1]\
        News: [Sen. Marco Rubio 'helped write the law to raise prescription prices'.] , Answer:[1]\
        News: [COVID-19 vaccine maker Moderna is a sponsor of the 2022 U.S. Open tennis tournament.] , Answer:[1]\
        News: ['The pharmaceutical industry has 1,400 lobbyists on Capitol Hill right now trying to stop' Medicare drug price negotiation.] , Answer:[1]\
        "

# 遍历数据并进行评估
# Data = Data[4475:]
for n, entry in tqdm(enumerate(Data), total=len(Data)):

    if n >= 1 and entry[3]!=None:
    # if n>=1:
        claim = entry[1]
        claim_label = entry[3]

        claims.append(claim)

        labels.append(claim_label)

Prompt1 = [prompt_1_0,prompt_1_1,prompt_1_2,prompt_1_3,prompt_1_4,prompt_1_5,prompt_1_6,prompt_1_7,prompt_1_8,prompt_1_9]
Prompt2 = [prompt_2_0,prompt_2_1,prompt_2_2,prompt_2_3,prompt_2_4,prompt_2_5,prompt_2_6,prompt_2_7,prompt_2_8,prompt_2_9]
Prompt3 = [prompt_3_0,prompt_3_1,prompt_3_2,prompt_3_3,prompt_3_4,prompt_3_5,prompt_3_6,prompt_3_7,prompt_3_8,prompt_3_9]


#Prompt1_test

print('prompt1 start!')

for i in range(10):
    pred = []

    for n, claim in tqdm(enumerate(claims), total=len(claims)):
            prompts = Prompt1[i] + f"Given the news [{claim}] , you are supposed to answer: "

            try:
                p = detect(prompts)
            except:
                p = None
            pred.append(p)
            # sleep(3)
    p1 = []
    l1 = []
    for j, text in tqdm(enumerate(pred), total=len(pred)):
            if text:
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
    with open("raw_prompt1_" + str(i) + ".txt", "w", encoding='utf-8') as file:
            for n, claim in tqdm(enumerate(claims), total=len(claims)):

                if n == 0:

                    file.write(
                        'claim' + '\t' + 'label' + '\t' + 'pred' + '\n' + str(claim) + '\t' + str(
                            labels[n]) + '\t' + str(
                            pred[n]) + '\n')
                else:
                    file.write(str(claim) + '\t' + str(labels[n]) + '\t' + str(pred[n]) + '\n')



#Prompt2_test
print('prompt2 start!')


for i in range(10):
    pred = []

    for n, claim in tqdm(enumerate(claims), total=len(claims)):
            prompts = Prompt2[i] + f" Is [{claim}] a true statement? Your answer is: "

            try:
                p = detect(prompts)
            except:
                p = None
            pred.append(p)
            sleep(3)
    p1 = []
    l1 = []
    for j, text in tqdm(enumerate(pred), total=len(pred)):
            if text!=None:
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

    with open("raw_prompt2_" + str(i) + ".txt", "w", encoding='utf-8') as file:
            for n, claim in tqdm(enumerate(claims), total=len(claims)):

                if n == 0:

                    file.write(
                        'claim' + '\t' + 'label' + '\t' + 'pred' + '\n' + str(claim) + '\t' + str(
                            labels[n]) + '\t' + str(
                            pred[n]) + '\n')
                else:
                    file.write(str(claim) + '\t' + str(labels[n]) + '\t' + str(pred[n]) + '\n')




#Prompt3_test
print('prompt3 start!')

for i in range(10):
    pred = []


    for n, claim in tqdm(enumerate(claims), total=len(claims)):
            prompts = Prompt3[
                          i] + f" For the news [{claim}], you must judge its authenticity and you can only reply with 0 or 1. So your answer is:"
            try:
                p = detect(prompts)
            except:
                p = 'failed'
            pred.append(p)
            sleep(3)
    p1 = []
    l1 = []
    for j, text in tqdm(enumerate(pred), total=len(pred)):
            if text:
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
    with open("raw_prompt3_" + str(i) + ".txt", "w", encoding='utf-8') as file:
            for n, claim in tqdm(enumerate(claims), total=len(claims)):

                if n == 0:

                    file.write(
                        'claim' + '\t' + 'label' + '\t' + 'pred' + '\n' + str(claim) + '\t' + str(
                            labels[n]) + '\t' + str(
                            pred[n]) + '\n')
                else:
                    file.write(str(claim) + '\t' + str(labels[n]) + '\t' + str(pred[n]) + '\n')