import smtplib
from email.message import EmailMessage

from ...config import settings


class EmailService:
    def send_password_reset_email(self, to_email: str, reset_link: str):
        # Para evitar vazamento de informação no endpoint (se o e-mail existe ou não),
        # o chamador deve capturar exceções e sempre retornar a mesma mensagem.
        print(
            f"[email] preparando envio reset: to={to_email} host={settings.SMTP_HOST} port={settings.SMTP_PORT} user={settings.SMTP_USERNAME} ssl={settings.SMTP_USE_SSL}",
            flush=True,
        )

        if not settings.SMTP_HOST or not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
            raise RuntimeError('SMTP não configurado (SMTP_HOST/SMTP_USERNAME/SMTP_PASSWORD)')

        msg = EmailMessage()
        msg['Subject'] = 'Recuperação de senha'

        from_email = settings.SMTP_FROM or settings.SMTP_USERNAME
        msg['From'] = from_email
        msg['To'] = to_email

        msg.set_content(
            '\n'.join(
                [
                    'Olá!',
                    '',
                    'Você solicitou a recuperação de senha.',
                    '',
                    'Clique no link abaixo para criar uma nova senha:',
                    reset_link,
                    '',
                    f'Este link expira em {settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES} minutos.',
                    '',
                    'Se você não solicitou isso, ignore este e-mail.',
                ]
            )
        )

        if settings.SMTP_USE_SSL:
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
                smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
                smtp.starttls()
                smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                smtp.send_message(msg)

        print(f"[email] enviado reset para {to_email}", flush=True)
