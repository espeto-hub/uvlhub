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


@bot_bp.route('/bots/edit/<int:bot_id>', methods=['GET', 'POST'])
@login_required
def edit_bot(bot_id):
    bot = BotService().get_by_id(bot_id)
    if not bot:
        return redirect(url_for('bot.list_bots'))

    return render_template('bot/edit.html', bot=bot)


@bot_bp.route('/bots/delete/<int:bot_id>', methods=['GET'])
@login_required
def delete_bot(bot_id):
    bot = BotService().get_by_id(bot_id)
    if not bot:
        return redirect(url_for('bot.list_bots'))

    BotService().delete(bot)
    return redirect(url_for('bot.list_bots'))
