from handlers.handlers import Source, TestCrawl, Search, EngineInstances, SourceLink, ErrorLogs, MyNews, ExtLogin, News,\
    Run, Home, Fuck, ConfirmUser, Categories, PremiumPackages, Payment
from handlers.upload import Upload
from handlers.user_operations import Register, Login, Profile, ForgotPassword, ResetPassword, ResendVerificationCode


url_patterns = [
    ("/v1/search/?([^/]+)?", Search, None, "search"),
    ("/v1/sources/?([^/]+)?", Source, None, "sources"),
    ("/v1/categories/?([^/]+)?", Categories, None, "categories"),
    ("/v1/source_links/?([^/]+)?", SourceLink, None, "source_links"),
    ("/v1/error_logs/?([^/]+)?", ErrorLogs, None, "error_logs"),
    ("/v1/engine_instances/?([^/]+)?", EngineInstances, None, "engine_instances"),
    ("/v1/test_crawl/?([^/]+)?", TestCrawl, None, "test_crawl"),
    ("/v1/my_news/?([^/]+)?", MyNews, None, "my_news"),
    ("/v1/news/?([^/]+)?", News, None, "news"),
    ("/v1/upload/?([^/]+)?", Upload, None, "upload"),
    ("/v1/ext_login/?([^/]+)?", ExtLogin, None, "ext_login"),
    ("/v1/run/?([^/]+)?", Run, None, "run"),
    ("/v1/premium_packages/?([^/]+)?", PremiumPackages, None, "premium_packages"),
    ("/v1/premium_package_orders/?([^/]+)?", PremiumPackages, None, "premium_package_orders"),

    ("/v1/payments/?([^/]+)?", Payment, None, "payments"),

    ("/v1/", Home, None, "home"),
    ("/v1/register", Register, None, "register"),
    ("/v1/login", Login, None, "login"),
    ("/v1/profile", Profile, None, "profile"),
    ("/v1/forgot_password", ForgotPassword, None, "forgot_password_v1"),

    ("/v1/fuck", Fuck, None, "fuck"),
    # ("/v1/fuck2", Fuck2, None, "fuck2"),
    ("/v1/confirm_user", ConfirmUser, None, "confirm_user"),
    ("/v1/reset_password", ResetPassword, None, "reset_password_v1"),
    ("/v1/resend_verification_code", ResendVerificationCode, None, "resend_verification_code_v1"),
]
