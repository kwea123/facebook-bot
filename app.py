import os
import sys
from bs4 import BeautifulSoup as bs
import requests
from flask import Flask, request, make_response, Response
import json
app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):  # someone sent us a message
                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text
                    if "beauty" in message_text:
                        text = ""
                        r = requests.get("https://www.ptt.cc/bbs/beauty/index.html")
                        soup = bs(r.text,"lxml")
                        page = soup.find("div", class_="btn-group-paging")
                        prev = page.find_all("a")[1]['href'] # previous page
                        r = requests.get("https://www.ptt.cc"+prev)
                        soup = bs(r.text,"lxml")
                        for div in soup.find_all("div", class_="r-ent"):
                            a = div.find_all("a")
                            if len(a)>0:
                                text += "https://www.ptt.cc"+a[0]['href']+' '
                        send_message(sender_id, text)
 
                if messaging_event.get("delivery"):  # delivery confirmation
                    pass
 
                if messaging_event.get("optin"):  # optin confirmation
                    pass
 
                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def send_message(recipient_id, message_text):

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)

def log(message):  # simple wrapper for logging to stdout on heroku
    print(str(message))
    sys.stdout.flush()

if __name__ == '__main__':
    app.run()

