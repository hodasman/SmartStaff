import ssl

from django.core.mail.backends.smtp import EmailBackend as SMTPBackend
from django.utils.functional import cached_property


class EmailBackend(SMTPBackend):
    '''Для отправки писем при разработке. В продакшен раскоментировать в settings'''
    @cached_property
    def ssl_context(self):
        if self.ssl_certfile or self.ssl_keyfile:
            ssl_context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_CLIENT)
            ssl_context.load_cert_chain(self.ssl_certfile, self.ssl_keyfile)
            return ssl_context
        # Проверка серверного сертификата включена (защита от MITM).
        # Отключать проверку (CERT_NONE) в продакшене нельзя.
        return ssl.create_default_context()
