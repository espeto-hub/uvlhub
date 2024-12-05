from flask import render_template, redirect, url_for
from flask_login import login_required, current_user

from app.modules.auth.services import AuthenticationService
from app.modules.bot import bot_bp
from app.modules.bot.services import BotService


@bot_bp.route('/bots/list', methods=['GET'])
@login_required
def list_bots():
    bots = BotService().get_all_by_user(current_user.id)
    return render_template('bot/index.html', bots=bots)

@bot_bp.route('/bots/create', methods=['GET', 'POST'])
@login_required
def create_bot():
    auth_service = AuthenticationService()
    profile = auth_service.get_authenticated_user_profile
    if not profile:
        return redirect(url_for("public.index"))

    return render_template('bot/create.html')
