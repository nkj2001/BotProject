class Notice():
    def __init__(self, channel, user, app):
        self.channel = f"@{user}"
        self.user = user
        self.timestamp = ""
        self.read = False
        _user = app.client.users_info(user=user)
        _ch = app.client.conversations_info(channel=channel)
        self._user_name = _user.get("user").get("real_name")
        self._ch_name = _ch.get("channel").get("name")
        self.NOTICE_TEXT = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"*{self._user_name}*님!!\n"
                    f"{self._ch_name} 채널에 오신것을 환영합니다.\n\n"
                    "*바른말 고운말을 씁시다!*"
                )
            }
        }
        self.DIVIDER = {"type": "divider"}
    
    def get_message(self):
        return {
            "text": "공지사항 입니다.",
            "ts": self.timestamp,
            "channel": self.channel,
            "username": "남박사 슬랙봇",
            "blocks": [
                self.NOTICE_TEXT,
                self.DIVIDER,
                self.__get_reaction()
            ]
        }
    
    def __get_reaction(self):
        if not self.read:
            emoji = ":white_large_square:"
            text = f"{emoji} *리액션을 해주셔야 공지 확인 처리가 됩니다.*"
        else:
            emoji = ":white_check_mark:"
            text = f"{emoji} *공지를 확인하셨습니다.*"
        return {"type": "section", "text": {"type": "mrkdwn", "text": text}}