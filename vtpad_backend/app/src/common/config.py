import os

from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

class EnvConfig:
    def __init__(self):
        load_dotenv('.env')
        self.db_name: str = os.getenv('db_name')
        self.db_user: str = os.getenv('db_user')
        self.db_password: str = os.getenv('db_password')
        self.db_host: str = os.getenv('db_host')
        self.db_port: str = os.getenv('db_port')

        self.db_report_name: str = os.getenv('db_report_name')
        self.db_report_user: str = os.getenv('db_report_user')
        self.db_report_password: str = os.getenv('db_report_password')
        self.db_report_host: str = os.getenv('db_report_host')
        self.db_report_port: str = os.getenv('db_report_port')

        self.jaeger_host: str = os.getenv('jaeger_host') if os.getenv('jaeger_host') else 'localhost'

        self.news_url: str = f"{os.getenv('news_url')}"

        self.report_portal_url: str = f"{os.getenv('report_url')}"
        self.report_api_hash: str = os.getenv('report_api_hash')

        # redis config
        self.redis_host: str = os.getenv('redis_host') if os.getenv('redis_host') else "127.0.0.1"
        self.redis_port: str = os.getenv('redis_port') if os.getenv('redis_port') else "6379"
        self.redis_user: str | None = os.getenv('redis_user') if os.getenv('redis_user') else None
        self.redis_password: str | None = os.getenv('redis_password') if os.getenv('redis_password') else None

        # secret config
        self.secret_key: str = os.getenv('SECRET_KEY')
        self.algorithm: str = os.getenv('ALGORITHM')
        self.access_token_expire: int = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
        self.refresh_token_expire: int = int(os.getenv('REFRESH_TOKEN_EXPIRE_MINUTES'))

        # main admin id
        self.main_admin_id: str = os.getenv('main_admin_id')
        try:
            self.use_mail = True if os.getenv('use_mail') == '1' else False
        except Exception:
            self.use_mail = False
        if self.use_mail:
            self.mail_conf = ConnectionConfig(
                    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
                    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
                    MAIL_FROM=os.getenv('MAIL_FROM'),
                    MAIL_PORT=int(str(os.getenv('MAIL_PORT'))),
                    MAIL_SERVER=os.getenv('MAIL_SERVER'),
                    MAIL_STARTTLS=bool(os.getenv('MAIL_STARTTLS')),
                    MAIL_SSL_TLS=bool(os.getenv('MAIL_SSL_TLS')),
                    USE_CREDENTIALS=bool(os.getenv('USE_CREDENTIALS')),
                    VALIDATE_CERTS=bool(os.getenv('VALIDATE_CERTS'))
            )
        self.frontend_url = os.getenv('FRONTEND_URL')
        self.app_name = os.getenv('APP_NAME')

conf = EnvConfig()