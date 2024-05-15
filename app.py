
import json
import requests


class Bot:
    def __init__(self,api_key):
        __VERSION__ = '0.1'
        self.API_KEY = api_key
        print("starting... ")
        result = self.get_update()
        try:
            self.chat_id = str(result["result"][-1]["message"]["from"]["id"])
            self.current_update_id = result["result"][-1]["update_id"] 
        except:
            self.chat_id = str(result["result"][-1]["callback_query"]["from"]["id"])
            self.current_update_id = result["result"][-1]["update_id"] 
        self.send_message("Bot Successfully Initialize...")
        print("Bot Successfully Initialize...")  
        print("chat id= ",self.chat_id)
        print("update id= ",self.current_update_id)
        
        self.life_style_note_path = 'notes/life-style.json'
        
    def get_update(self):
        rqst = 'https://api.telegram.org/bot'+self.API_KEY+'/getUpdates'
        r = requests.get(rqst)
        result_json_string = r.content.decode()
        result = json.loads(result_json_string)
        return result
    def send_message(self,msg):
        send_message = 'https://api.telegram.org/bot'+self.API_KEY+'/sendMessage'
        payload={
                "chat_id":self.chat_id,
                "text":msg
                }
        requests.post(send_message,json=payload)
    def send_message_with_payload(self,payload):
        send_message = 'https://api.telegram.org/bot'+self.API_KEY+'/sendMessage'
        requests.post(send_message,json=payload)
        
    def reply_inline_options(self,notes):
        buttons = []
        for note in notes:
            buttons.append([{"text":note['title'],"callback_data":note['id']}])
        payload = {
                'chat_id': self.chat_id,
                'text':'\t\tসম্পর্কিত কিছু নোট ⏬⏬',
                'reply_markup': 
                    {	
                        'inline_keyboard': buttons
                            
                    }
                    }
        self.send_message_with_payload(payload)
    def search_query(self,input_query=None):
        
        querys = input_query.split(" ")
        found_notes = []
        with open(self.life_style_note_path, 'r', encoding='utf-8') as file:
            life_style_notes = json.load(file)
            for note in life_style_notes:
                note_id = note['id']
                note_score = 0
                tags = note['tags']
                for query in querys:
                    if query in tags:
                        note_score += 1
                if note_score > 0:
                    note = dict(note)
                    note['score'] = note_score
                    found_notes.append(note)
        found_notes = sorted(found_notes, key=lambda k: k['score'], reverse=True)
        return found_notes
                
    def main(self):
        while True:
            raw_result = self.get_update()
            results = raw_result["result"]
            for result in results:
                update_id = result["update_id"]
                if update_id == self.current_update_id+1:
                    try:
                        reply_msg = result["message"]["text"]
                        print("New Message > ",reply_msg)
                        
                        if reply_msg == "who are you?":
                            self.send_message("I am your assistant bot")
                        elif reply_msg == "আমি":
                            self.send_message('তুমি')
                        else:
                            found_notes = self.search_query(reply_msg)
                            if len(found_notes) > 0:
                                self.reply_inline_options(found_notes)
                            else:
                                self.send_message("আপনার জিজ্ঞাসাটির জবাব পাওয়া যায়নি।")  
                                
                    except KeyError:
                        if 'callback_query' in result.keys():
                            callback_msg = result["callback_query"]["data"]
                            print('callback: ',callback_msg)
                            with open(self.life_style_note_path, 'r', encoding='utf-8') as file:
                                life_style_notes = json.load(file)
                                for note in life_style_notes:
                                    if note['id'] == callback_msg:
                                        self.send_message(f"{note['title']}\n\n {note['body']}")
                                        break 
                    self.current_update_id +=1

if __name__ == '__main__':
    b = Bot(api_key="5991793049:AAE66lMJlaui26nzRa0-MeUt6sB319OlRtk")
    b.main()
