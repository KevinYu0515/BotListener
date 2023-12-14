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

# token = 'MTExNzgxMTAyNDA4Nzc0NDU5NQ.Gw0eCr.rfAMF-_dSBiOVK7EYfPpRdn8BJIroX2kIlYS-c'
# token = 'NjQwMTAyNTE2NzM4MDk3MTYz.GUOxs_.bu_YcmodcCn8xJNUHbbf0nUrQ3pbu5N11YpeFc'
token = 'MTE2NzEzMTk4NzAyMzIzMzA0NA.GCOyry.i3WDnBYvi6RoAg9lIzI_tefqptfpduQsJJnWw8'
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