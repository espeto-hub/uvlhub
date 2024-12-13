from urllib.parse import unquote

from flask import render_template, redirect, url_for, request, abort
from flask_login import login_required, current_user

from app import apprise
from app.modules.auth.services import AuthenticationService
from app.modules.bot import bot_bp
from app.modules.bot.forms import BotForm
from app.modules.bot.services import BotService, BotMessagingService


@bot_bp.route('/bots/list', methods=['GET'])
@login_required
def list_bots():
    bots = BotService().get_all_by_user(current_user.id)
    return render_template('bot/index.html', bots=bots)


@bot_bp.route('/bots/create', methods=['GET', 'POST'])
@login_required
def create_bot():
    auth_service = AuthenticationService()
    profile = auth_service.get_authenticated_user_profile()
    if not profile:
        return redirect(url_for("public.index"))

    form = BotForm()
    form.user_id.data = profile.user_id
    if request.method == 'POST' and form.validate_on_submit():
        service = BotService()
        if form.test.data:
            message_service = BotMessagingService()
            url = form.service_url.data
            result, message = message_service.send_test_message(url)
            if result:
                form.is_tested.data = 'true'
            else:
                form.is_tested.data = 'false'
                form.test.errors.append(message)
            return render_template('bot/create_edit.html', form=form, title='Create bot')
        elif form.submit.data:
            if form.is_tested.data == 'false':
                form.test.errors.append('Please test the bot first')
                return render_template('bot/create_edit.html', form=form, title='Create bot')
            if not service.is_bot_name_unique(form.name.data):
                form.name.errors.append('This name is already in use')
                return render_template('bot/create_edit.html', form=form, title='Edit bot')
            result = service.create_bot(form)
            return service.handle_service_response(
                result, None, 'bot.list_bots', 'Bot created successfully', 'bot/create_edit.html', form
            )

    return render_template('bot/create_edit.html', form=form, title='Create bot')


@bot_bp.route('/bots/edit/<int:bot_id>', methods=['GET', 'POST'])
@login_required
def edit_bot(bot_id):
    auth_service = AuthenticationService()
    profile = auth_service.get_authenticated_user_profile()
    if not profile:
        return redirect(url_for("public.index"))

    service = BotService()
    bot = service.get_or_404(bot_id)

    if bot.user_id != profile.user_id:
        abort(403)

    form = BotForm(obj=bot)
    if request.method == 'POST' and form.validate_on_submit():
        if form.test.data:
            message_service = BotMessagingService()
            url = form.service_url.data
            result, message = message_service.send_test_message(url)
            if result:
                form.is_tested.data = 'true'
            else:
                form.is_tested.data = 'false'
                form.test.errors.append(message)
            return render_template('bot/create_edit.html', form=form, title='Edit bot')
        elif form.submit.data:
            if form.is_tested.data == 'false':
                form.test.errors.append('Please test the bot first')
                return render_template('bot/create_edit.html', form=form, title='Edit bot')
            if not service.is_bot_name_unique(form.name.data, bot_id):
                form.name.errors.append('This name is already in use')
                return render_template('bot/create_edit.html', form=form, title='Edit bot')
            result = service.update_bot(bot, form)
            return service.handle_service_response(
                result, None, 'bot.list_bots', 'Bot edited successfully', 'bot/create_edit.html', form
            )

    return render_template('bot/create_edit.html', form=form, title='Edit bot')


@bot_bp.route('/bots/delete/<int:bot_id>', methods=['POST'])
@login_required
def delete_bot(bot_id):
    service = BotService()
    bot = service.get_or_404(bot_id)

    auth_service = AuthenticationService()
    profile = auth_service.get_authenticated_user_profile()
    if not profile:
        return redirect(url_for("public.index"))

    if bot.user_id != profile.user_id:
        abort(403)

    service.delete(bot)
    return redirect(url_for('bot.list_bots'))


@bot_bp.route('/bots/guide/<service_name>', methods=['GET'])
@login_required
def guide(service_name):
    auth_service = AuthenticationService()
    profile = auth_service.get_authenticated_user_profile()
    if not profile:
        return redirect(url_for("public.index"))

    service_name = unquote(service_name)
    if service_name not in apprise.service_names:
        abort(404)
    return apprise.html_guide(service_name)
