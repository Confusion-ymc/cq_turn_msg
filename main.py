import subprocess
from aiocqhttp import CQHttp
import configparser
import json
import os, sys


def creat_config(qq):
    file_txt = '''{
    "host": "[::]",
    "port": 5700,
    "use_http": true,
    "ws_host": "[::]",
    "ws_port": 6700,
    "use_ws": false,
    "ws_reverse_url": "",
    "ws_reverse_reconnect_interval": 3000,
    "ws_reverse_reconnect_on_code_1000": true,
    "ws_reverse_api_url": "ws://127.0.0.1:8080/ws/api/",
    "ws_reverse_event_url": "ws://127.0.0.1:8080/ws/event/",
    "use_ws_reverse": true,
    "post_url": "",
    "access_token": "",
    "secret": "",
    "post_message_format": "string",
    "serve_data_files": false,
    "update_source": "github",
    "update_channel": "stable",
    "auto_check_update": false,
    "auto_perform_update": false,
    "show_log_console": true,
    "log_level": "info"
}'''
    with open('./CQAir/data/app/io.github.richardchien.coolqhttpapi/config/{}.json'.format(qq), 'w') as f:
        f.write(file_txt)


bot = CQHttp(api_root='http://127.0.0.1:5700/')


# 消息事件
@bot.on_message()
async def handle_msg(context):
    for plug in run_plug_list:
        await plug.parse_context(context)
    # return {'reply': context['message']} # 直接回复


# 通知
@bot.on_notice('group_increase')
async def handle_group_increase(context):
    print(context)
    await bot.send(context, message='欢迎新人～',
                   at_sender=True, auto_escape=True)


# 请求 添加好友
@bot.on_request('group', 'friend')
async def handle_request(context):
    return {'approve': True, 'reason': '拒绝理由'}


# 自动转发消息插件
class TurnMsgPlug:
    def __init__(self):
        config_cfg = "./default.ini"
        config_raw = configparser.RawConfigParser()
        config_raw.read(config_cfg)
        login_qq = config_raw.get('login_id', 'qq')
        creat_config(login_qq)
        self.turn_rules = {}
        for i in range(100):
            try:
                from_id = config_raw.getint('turn_rule_{}'.format(i + 1), 'from_id')
                self.turn_rules[from_id] = {
                    'send_to_usr_id': json.loads(config_raw.get('turn_rule_{}'.format(i + 1), 'send_to_usr_id')),
                    'send_to_group_id': json.loads(config_raw.get('turn_rule_{}'.format(i + 1), 'send_to_group_id'))
                }
            except:
                break

    # 转发消息
    async def parse_context(self, context):
        if context.get('group_id', None) in self.turn_rules or (
                context.get('user_id', None) in self.turn_rules and context['message_type'] == 'private'):
            from_id_type = ''
            if context['message_type'] == 'private':
                from_id_type = 'user_id'
            elif context['message_type'] == 'group':
                from_id_type = 'group_id'
            if from_id_type not in ['group_id', 'user_id']:
                return
            # 发送私信
            for send_to_user_id in self.turn_rules[context[from_id_type]]['send_to_usr_id']:
                pass
                await bot.send_private_msg(message=context['message'], user_id=send_to_user_id)
            # 发送群消息
            for send_to_group_id in self.turn_rules[context[from_id_type]]['send_to_group_id']:
                pass
                await bot.send_group_msg(message=context['message'], group_id=send_to_group_id)


# 启动cq
def open_cq():
    base_dir = os.path.dirname(__file__)
    sys.path.append(base_dir)  # 临时修改环境变量
    cmd = base_dir + '/CQAir/CQA.exe'
    print(cmd)
    subprocess.Popen([cmd])


plug_switch = {
    TurnMsgPlug: True
}
run_plug_list = []
for plug, flag in plug_switch.items():
    if flag:
        run_plug_list.append(plug())

if __name__ == '__main__':
    open_cq()
    bot.run(host='127.0.0.1', port=8080)
