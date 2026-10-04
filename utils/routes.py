from django.urls import reverse_lazy


def routes(request):
    return {
        # ======================================== Auth ========================================
        "dashboard_login_url": reverse_lazy("dashboard_login"),
        "dashboard_logout_url": reverse_lazy("dashboard_logout"),
        "dashboard_profile_url": reverse_lazy("dashboard_profile"),
        "admin_url": reverse_lazy("admin"),
        "site_settings_url": reverse_lazy("site_settings"),
        # ======================================== Dashboard ========================================
        "dashboard_url": reverse_lazy("dashboard"),
        # ======================================== UserModel ========================================
        "user_list_url": reverse_lazy("user_list"),
        "user_create_url": reverse_lazy("user_create"),
        "user_export_excel_url": reverse_lazy("user_export_excel"),
        "user_export_pdf_url": reverse_lazy("user_export_pdf"),
        
        # ======================================== LanguageModel ========================================
        "language_list_url": reverse_lazy("language_list"),
        "language_create_url": reverse_lazy("language_create"),
        # ======================================== TextKeyModel ========================================
        "text_key_list_url": reverse_lazy("text_key_list"),
        "text_key_create_url": reverse_lazy("text_key_create"),
        # ======================================== RoleModel ========================================
        "role_list_url": reverse_lazy("role_list"),
        "role_create_url": reverse_lazy("role_create"),
        "role_export_excel_url": reverse_lazy("role_export_excel"),
        "role_export_pdf_url": reverse_lazy("role_export_pdf"),
        # ======================================== LawModel ========================================
        "law_list_url": reverse_lazy("law_list"),
        "law_create_url": reverse_lazy("law_create"),
        # ======================================== Unfinished Page ========================================
        # ========================
        # Stock / Inventory
        # ========================
        "index_url": reverse_lazy("index"),
        "chapter_url": reverse_lazy("chapter"),
        "section_url": reverse_lazy("section"),
        "profile_url": reverse_lazy("profile"),
        "privacy_policy_url": reverse_lazy("privacy_policy"),
        "bookmarks_url": reverse_lazy("bookmarks"),
        "history_url": reverse_lazy("history"),
        "downloads_url": reverse_lazy("downloads"),

        "login_url": reverse_lazy("login"),
        "register_url": reverse_lazy("register"),
        "logout_url": reverse_lazy("logout"),
        "verify_otp_url": reverse_lazy("verify_otp"),
        "reset_password_url": reverse_lazy("reset_password"),
        "request_reset_password_url": reverse_lazy("request_reset_password"),
        "resend_otp_url": reverse_lazy("resend_otp"),
    }
