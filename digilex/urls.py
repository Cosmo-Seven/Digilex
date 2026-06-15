from django.contrib import admin
from django.urls import include, path, re_path
from django.conf.urls.static import static
from django.conf import settings
from views.dashboard import (
    auth_views,
    user_views,
    role_views,
    language_views,
    text_key_views,
    law_views,
    chapter_views,
    section_views,
)

from views.website import (
    page_views
)
from views.dashboard import page_views as dashboard_page_views
from views.website import page_views as website_page_views
from views.website import auth_views as website_auth_views

handler500 = dashboard_page_views.internal_server_error

urlpatterns = (
    [
    path(settings.ADMIN_LOGIN_URL, admin.site.urls),
    # ================================================================================================
    # DASHBOARD URL
    # ================================================================================================
    path("lcno*@$/", dashboard_page_views.dashboard, name="dashboard"),
    path(
        "under-maintenance/",
        dashboard_page_views.under_maintenance,
        name="under_maintenance",
    ),
    path(
        settings.DASHBOARD_LOGIN_URL,
        auth_views.dashboard_login,
        name="dashboard_login",
    ),
    path(
        settings.DASHBOARD_LOGOUT_URL,
        auth_views.dashboard_logout,
        name="dashboard_logout",
    ),
    path("dashboard/profile/", auth_views.profile, name="dashboard_profile"),
    path(
        "dashboard/site-settings/",
        dashboard_page_views.site_settings,
        name="site_settings",
    ),
    # ========================
    # UserModel
    # ========================
    path("dashboard/user/list/", user_views.user_list, name="user_list"),
    path("dashboard/user/create/", user_views.user_create, name="user_create"),
    path(
        "dashboard/user/update/<uuid:pk>/",
        user_views.user_update,
        name="user_update",
    ),
    path(
        "dashboard/user/delete/<uuid:pk>/",
        user_views.user_delete,
        name="user_delete",
    ),
    path(
        "dashboard/user/approve/<uuid:pk>/",
        user_views.user_approve,
        name="user_approve",
    ),
    path(
        "dashboard/user/export/excel/",
        user_views.user_export_excel,
        name="user_export_excel",
    ),
    path(
        "dashboard/user/export/pdf/",
        user_views.user_export_pdf,
        name="user_export_pdf",
    ),
    # ========================
    # RoleModel
    # ========================
    path("dashboard/role/list/", role_views.role_list, name="role_list"),
    path("dashboard/role/create/", role_views.role_create, name="role_create"),
    path(
        "dashboard/role/update/<uuid:pk>/",
        role_views.role_update,
        name="role_update",
    ),
    path(
        "dashboard/role/delete/<uuid:pk>/",
        role_views.role_delete,
        name="role_delete",
    ),
    path(
        "dashboard/role/export/excel/",
        role_views.role_export_excel,
        name="role_export_excel",
    ),
    path(
        "dashboard/role/export/pdf/",
        role_views.role_export_pdf,
        name="role_export_pdf",
    ),
    # ========================
    # LanguageModel
    # ========================
    path(
        "dashboard/language/list/",
        language_views.language_list,
        name="language_list",
    ),
    path("set-language/", language_views.set_language, name="set_language"),
    path(
        "dashboard/language/create/",
        language_views.language_create,
        name="language_create",
    ),
    path(
        "dashboard/language/update/<uuid:pk>/",
        language_views.language_update,
        name="language_update",
    ),
    path(
        "dashboard/language/delete/<uuid:pk>/",
        language_views.language_delete,
        name="language_delete",
    ),
    # ========================
    # TextKeyModel
    # ========================
    path(
        "dashboard/text-key/list/",
        text_key_views.text_key_list,
        name="text_key_list",
    ),
    path(
        "dashboard/text-key/create/",
        text_key_views.text_key_create,
        name="text_key_create",
    ),
    path(
        "dashboard/text-key/update/<uuid:pk>/",
        text_key_views.text_key_update,
        name="text_key_update",
    ),
    path(
        "dashboard/text-key/delete/<uuid:pk>/",
        text_key_views.text_key_delete,
        name="text_key_delete",
    ),
    path(
        "dashboard/translations/save/",
        text_key_views.save_translation,
        name="save_translation",
    ),
    # ========================
    # PWA
    # ========================
    path("", include("pwa.urls")),

    # ========================
    # Law
    # ========================
    path("dashboard/law/list/", law_views.law_list, name="law_list"),
    path("dashboard/law/create/", law_views.law_create, name="law_create"),
    path("dashboard/law/update/<uuid:id>/", law_views.law_update, name="law_update"),
    path("dashboard/law/delete/<uuid:id>/", law_views.law_delete, name="law_delete"),

    # ========================
    # Chapter
    # ========================
    path("dashboard/law/<uuid:law_id>/chapters/", chapter_views.chapter_list, name="chapter_list"),
    path("dashboard/law/<uuid:law_id>/chapters/create/", chapter_views.chapter_create, name="chapter_create"),
    path("dashboard/law/<uuid:law_id>/chapters/update/<uuid:pk>/", chapter_views.chapter_update, name="chapter_update"),
    path("dashboard/law/<uuid:law_id>/chapters/delete/<uuid:pk>/", chapter_views.chapter_delete, name="chapter_delete"),

    # ========================
    # Section
    # ========================
    path("dashboard/chapter/<uuid:chapter_id>/sections/", section_views.section_list, name="section_list"),
    path("dashboard/chapter/<uuid:chapter_id>/sections/create/", section_views.section_create, name="section_create"),
    path("dashboard/chapter/<uuid:chapter_id>/sections/update/<uuid:pk>/", section_views.section_update, name="section_update"),
    path("dashboard/chapter/<uuid:chapter_id>/sections/delete/<uuid:pk>/", section_views.section_delete, name="section_delete"),

    # ========================
    # WEBSITE URLS
    # ========================
    path("", website_page_views.index, name="index"),
    path("law/chapters/<uuid:law_id>/", website_page_views.chapter, name="chapter"),
    path("chapter/sections/<uuid:chapter_id>/", website_page_views.section, name="section"),
    path("section/<uuid:section_id>/", website_page_views.section_detail, name="section_detail"),
    path("search/", website_page_views.global_search, name="global_search"),
    path("profile/", website_page_views.profile, name="profile"),
    path("privacy/policy/", website_page_views.privacy_policy, name="privacy_policy"),
    path("bookmarks/", website_page_views.bookmarks, name="bookmarks"),
    path("bookmark/toggle/", website_page_views.toggle_bookmark, name="toggle_bookmark"),
    path("downloads/", website_page_views.downloads, name="downloads"),
    # path("section/download/pdf/<uuid:section_id>/", website_page_views.download_section_pdf, name="download_section_pdf"),
    # path("section/download/txt/<uuid:section_id>/", website_page_views.download_section_txt, name="download_section_txt"),

    # ========================
    # WEBSITE AUTH URLS
    # ========================
    path("login/", website_auth_views.user_login, name="login"),
    path("logout/", website_auth_views.user_logout, name="logout"),
    path("register/", website_auth_views.user_register, name="register"),
    path("subscribe/", website_auth_views.subscribe, name="subscribe"),
    path("change_password/", website_auth_views.change_password, name="change_password"),
    path("reset_password/", website_auth_views.reset_password, name="reset_password"),
    path("request_reset_password/", website_auth_views.request_reset_password, name="request_reset_password"),
    path("resend_otp/", website_auth_views.resend_otp, name="resend_otp"),
    path("update_profile/", website_auth_views.update_profile),
    path("verify_otp/", website_auth_views.verify_otp, name="verify_otp"),
    path(settings.LOGIN_URL, website_auth_views.user_login),
]
+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)