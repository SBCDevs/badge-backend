import os
import traceback
from discord import SyncWebhook, Embed
from datetime import datetime

def log_error(error):
    webhook = SyncWebhook.from_url(os.getenv('webhook'))
    try: raise error from error
    except Exception:
        webhook.send(
            embed=Embed(
                title="Error Report [WEB]",
                description=f"""Time: {datetime.now().strftime("%H:%M:%S")}\nDay: {datetime.now().strftime("%B %d, %Y ")}\nError: {error}\nTraceback:\n\n```py\n{traceback.format_exc()}\n```""",
                color=0xff0000
            ), username='Error Log'
        )