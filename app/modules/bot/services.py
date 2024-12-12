from app import apprise
from app.modules.bot.repositories import BotRepository
from core.services.BaseService import BaseService


class BotService(BaseService):
    def __init__(self):
        super().__init__(BotRepository())

    def get_all_by_user(self, user_id):
        return self.repository.get_all_by_user(user_id)

    def get_by_id(self, id):
        return self.repository.get_by_id(id)

    def delete(self, bot):
        return self.repository.delete(bot)

    def create_bot(self, form):
        created_instance = self.create(
            name=form.name.data,
            service_name=form.service_name.data,
            service_url=form.service_url.data,
            enabled=form.enabled.data,
            on_download_dataset=form.on_download_dataset.data,
            on_download_file=form.on_download_file.data,
            user_id=form.user_id.data,
        )
        return created_instance

    def get_by_user_and_name(self, user_id, name):
        return self.repository.get_by_user_and_name(user_id, name)

    def update_bot(self, bot, form):
        return self.repository.update(
            bot.id,
            name=form.name.data,
            service_name=form.service_name.data,
            service_url=form.service_url.data,
            enabled=form.enabled.data,
            on_download_dataset=form.on_download_dataset.data,
            on_download_file=form.on_download_file.data,
        )

    def get_on_download_dataset_bot_urls(self, uploader_id):
        return [b.service_url for b in self.repository.get_on_download_dataset_bots(uploader_id)]

    def get_on_download_file_bot_urls(self, uploader_id):
        return [b.service_url for b in self.repository.get_on_download_file_bots(uploader_id)]


class BotMessagingService(BaseService):
    def __init__(self):
        super().__init__(BotRepository())

    @staticmethod
    def send_test_message(urls: str | list[str]):
        return apprise.send_test_message(urls)

    @staticmethod
    def on_download_dataset(dataset, profile):
        uploader_id = dataset.user_id
        downloader_id = profile.user_id if profile else None
        if uploader_id == downloader_id:
            return

        title = "Someone downloaded your dataset!"
        body = f"Your dataset '{dataset.name()}' has been downloaded"
        if profile:
            body += f" by {profile.name} {profile.surname}"
        else:
            body = f" by an anonymous user"
        service = BotService()
        urls = service.get_on_download_dataset_bot_urls(uploader_id)
        apprise.send_message(urls, title=title, body=body)

    @staticmethod
    def on_download_file(file, profile, format='UVL'):
        uploader_id = file.feature_model.data_set.user_id
        downloader_id = profile.user_id if profile else None
        if uploader_id == downloader_id:
            return

        title = "Someone downloaded your file!"
        body = f"Your file '{file.name}' from the dataset {file.feature_model.data_set.name()} has been downloaded in {format} format"
        if profile:
            body += f" by {profile.name} {profile.surname}"
        else:
            body = f" by an anonymous user"
        service = BotService()
        urls = service.get_on_download_file_bot_urls(uploader_id)
        apprise.send_message(urls, title=title, body=body)
