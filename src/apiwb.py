import os
import time
from tqdm import tqdm
from progress.bar import IncrementalBar
import requests
from database_connection import *
from dateutil.parser import parse
from dotenv import load_dotenv
import os

load_dotenv()
WB_TOKEN = os.environ.get('WB_TOKEN')

COLORS = dict()


def take_feedbacks(take: int, skip: int, isAnswered: bool) -> dict:
    url = "https://feedbacks-api.wildberries.ru/api/v1/feedbacks"
    payload = {"isAnswered": isAnswered, "take": take, "skip": skip}
    headers = {'Authorization': WB_TOKEN}
    res = requests.get(url, params=payload, headers=headers)
    return res.json()


def gather_all_feedbacks() -> list:
    all_feedbacks = []
    take = 5000
    skip = 0
    isAnswered = False
    print("Collecting unanswered feedbacks...")
    while True:
        res = take_feedbacks(take, skip, isAnswered)
        if res['error']:
            print(res)
        data = res["data"]
        feedbacks = data["feedbacks"]
        if not feedbacks:
            break
        feedbacks = process_feedbacks(feedbacks, isAnswered)
        all_feedbacks += feedbacks
        skip += take

    take = 5000
    skip = 0
    isAnswered = True
    print("Collecting answered feedbacks...")
    while True:
        res = take_feedbacks(take, skip, isAnswered)
        data = res["data"]
        feedbacks = data["feedbacks"]
        if not feedbacks:
            break
        feedbacks = process_feedbacks(feedbacks, isAnswered)
        all_feedbacks += feedbacks
        skip += take

    return all_feedbacks


def process_feedbacks(feedbacks: list, isAnswered: bool) -> list:
    result = []
    # bar = IncrementalBar('Feedbacks', max=len(feedbacks))
    for feedback in tqdm(feedbacks):
        # bar.next()
        processed_feedback = process_feedback(feedback, isAnswered)
        # print(processed_feedback)
        result.append(processed_feedback)
    # bar.finish()
    return result


def process_feedback(feedback: dict, isAnswered: bool) -> list:
    id = feedback["id"]
    text = feedback["text"]
    productValuation = feedback["productValuation"]
    createdDate = feedback["createdDate"]
    createdDate = parse(createdDate).replace(tzinfo=None)
    answer = feedback["answer"] if not feedback["answer"] else feedback["answer"]["text"]
    state = feedback["state"]
    supplierComplaint = feedback["supplierComplaint"]
    isCreationSupplierComplaint = feedback["isCreationSupplierComplaint"]
    photoLinks = feedback["photoLinks"]
    userName = feedback["userName"]
    wasViewed = feedback["wasViewed"]

    productDetails = feedback["productDetails"]

    imtId = productDetails["imtId"]
    nmId = productDetails["nmId"]
    productName = productDetails["productName"]
    supplierArticle = productDetails["supplierArticle"]
    supplierName = productDetails["supplierName"]
    brandName = productDetails["brandName"]
    size = productDetails["size"]
    look = size.lower()
    if nmId in COLORS.keys():
        color = COLORS[nmId]
        look = color + ", " + look
    else:
        detail = requests.get(f"https://card.wb.ru/cards/detail?nm={nmId}", timeout=(2, 2.2))
        if detail.ok:
            products = detail.json()['data']['products']
            if products:
                color = products[0]["colors"][0]["name"]
                COLORS.update({nmId: color})
                look = color + ", " + look

    images = ""
    if photoLinks:
        for photo in photoLinks:
            images += photo['fullSize'] + ","
        images = images.rstrip(",")

    return [
        id,
        productName,
        supplierArticle,
        nmId,
        createdDate,
        look,
        "null" if not text else text,
        productValuation,
        userName,
        wasViewed,
        isAnswered,
        answer,
        images,
    ]


def give_an_answer(id: str, text: str) -> None:
    url = "https://feedbacks-api.wb.ru/api/v1/feedbacks"
    headers = {'Authorization': WB_TOKEN}
    data = {
        "id": id,
        "text": text
    }
    resp = requests.patch(url, headers=headers, json=data)
    print(resp.status_code)
def test():
    review_id = "iDUbHIgBNO444I63fDkI"
    url = "https://feedbacks-api.wildberries.ru/api/v1/feedbacks/archive?take=5000&skip=0"
    # url = "https://feedbacks-api.wb.ru/api/v1/feedbacks"
    headers = {'Authorization': WB_TOKEN,
               }
    resp = requests.get(url, headers=headers)
    print(resp.status_code)
    content = resp.json()
    print(content["data"]["feedbacks"])

def main():
    values = gather_all_feedbacks()
    insert_into_reviews(values)


if __name__ == '__main__':

    test()