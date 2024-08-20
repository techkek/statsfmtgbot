from config import ENV

def send_long_message(bot, chat_id, text, parse_mode=None):
    max_message_length = 4096
    start = 0
    
    while start < len(text):
        end = start + max_message_length

        if end < len(text):
            end = text.rfind('\n', start, end)
            if end == -1:
                end = start + max_message_length
        try:
            bot.send_message(chat_id, text[start:end], parse_mode=parse_mode, disable_web_page_preview=True)
        except Exception as e:
            if ENV == "development" or ENV == "debug":
                print(f"Error sending message: {e}")
            cleaned_text = text[start:end].replace('_', '').replace('*', '').replace('`', '').replace('[', '').replace(']', '')
            bot.send_message(chat_id, cleaned_text, parse_mode=parse_mode, disable_web_page_preview=True)

        start = end
        
        if start < len(text) and text[start] == '\n':
            start += 1

def format_listening_time(ms):
    seconds = ms // 1000
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m {seconds}s"
