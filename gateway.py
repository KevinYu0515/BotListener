import json, time
from websocket._exceptions import WebSocketConnectionClosedException

def send_json_request(ws, request):
    ws.send(json.dumps(request))

def recieve_json_response(ws):
    response = ws.recv()
    if response:
        return json.loads(response)
    # try:
    #     response = ws.recv()
    #     if response:
    #         return json.loads(response)
    # except WebSocketConnectionClosedException as e:
    #     print(e)
    #     return

def heartbeat(interval, ws):
    print('Heartbeat Begin')
    while True:
        time.sleep(interval)
        heartbeatJSON = {
            'op': 1,
            'd': 'null'
        }
        send_json_request(ws, heartbeatJSON)

# token = ''
payload = {
    'op': 2,
    'd': {
        'token': token,
        'properties': {
            '$os': "windows",
            '$browser': 'chrome',
            '$device': 'pc'
        }
    }
}