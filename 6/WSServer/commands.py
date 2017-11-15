import json


def join(self, data):
    for handler in self.temp.handlers:
        handler.ws_send(json.dumps({'type': 'player_connected', 'data': self.id}))
    return {'type': 'join_ok', 'data': self.id}


def do_action(self, data):
    for handler in self.temp.handlers:
        resp = {
            'type': 'action',
            'data': {
                'action_type': data['action_type'],
                'player_id': self.id
            }
        }
        handler.ws_send(json.dumps(resp))
    return {'type': 'do_action_ok', 'data': ''}


def get_sync(self, data):
    for handler in self.temp.handlers:
        if handler.id != 1:
            handler.ws_send(json.dumps({'type': 'sync', 'data': data}))
    return {'type': 'sync_ok', 'data': ''}
