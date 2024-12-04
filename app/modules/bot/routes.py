from flask import render_template
from app.modules.bot import bot_bp


@bot_bp.route('/bot', methods=['GET'])
def index():
    return render_template('bot/index.html')
