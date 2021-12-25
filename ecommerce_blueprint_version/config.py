class Config:
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245'
    # SQLALCHEMY_DATABASE_URI = 'mysql://root:Nulifendou8!@127.0.0.1:3306/ecommerce'
    # SQLALCHEMY_DATABASE_URI = 'mysql://greedprp_production_user:Nulifendou8!@server52.web-hosting.com:3306/greedprp_production_db'
    SQLALCHEMY_DATABASE_URI = 'mysql://greedprp_test:Nulifendou8!@server52.web-hosting.com:3306/greedprp_modernfoodie'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'zuck.mail.sender@gmail.com'
    MAIL_PASSWORD = 'mailsender1'
    ADMIN_TEAM = ['ziangxuu@gmail.com', 'modernfoodieMTL@gmail.com']
