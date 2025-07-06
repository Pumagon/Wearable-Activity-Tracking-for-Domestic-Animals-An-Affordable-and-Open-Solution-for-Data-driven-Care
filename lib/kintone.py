import json

def uploadRecord(*, requests: Session, subDomain: str, apiToken: str, record: Dict[str, Any]) -> Optional[str]:
    url = "https://" + subDomain + ".kintone.com/k/v1/record.json"
    headers = {"X-Cybozu-API-Token": apiToken,
               "Content-Type": "application/json"}

    response = None

    try:
        response = requests.post(url, headers=headers, json=record)

        if response.status_code == 200 and "id" in json.loads(response.text):
            print("Record uploaded.", end=" ")
            recordId = json.loads(response.text)["id"]
            print("Record ID: " + recordId)
            return recordId
        else:
            print("Record upload failed. Status code: " + str(response.status_code))
            print("Response text:" + response.text)
            return None

    finally:
        if response is not None:
            response.close()

