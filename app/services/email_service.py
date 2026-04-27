import random
import string
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.core.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


async def send_2fa_email(recipient_email: str):
    """Gera um código de 6 dígitos e envia para o usuário."""

    code = "".join(random.choices(string.digits, k=6))
    print(f"\n🚀 [DEBUG] CÓDIGO DE VERIFICAÇÃO PARA {recipient_email}: {code}\n")
    html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color: #2D3E50;">Verificação PrecedentIA</h2>
            <p>Olá! Você solicitou um acesso ou cadastro no nosso sistema.</p>
            <p>Seu código de verificação é:</p>
            <div style="background: #F4F7F6; padding: 20px; text-align: center; font-size: 24px; font-weight: bold; letter-spacing: 5px; border-radius: 8px;">
                {code}
            </div>
            <p style="font-size: 12px; color: #777;">Este código expira em 10 minutos. Se você não solicitou este e-mail, ignore-o.</p>
        </body>
    </html>
    """

    message = MessageSchema(
        subject="Seu código de segurança - PrecedentIA",
        recipients=[recipient_email],
        body=html,
        subtype=MessageType.html,
    )

    fm = FastMail(conf)
    await fm.send_message(message)

    return code
