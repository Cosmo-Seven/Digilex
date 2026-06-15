def sidebar(request):
    try:
        from core.models import LawModel
        laws = LawModel.objects.all()
    except Exception:
        laws = []

    law_items = []
    for law in laws:
        law_items.append({
            "label": law.title,
            "url": f"/dashboard/law/{law.id}/chapters/",
            "icon": "ti ti-file-text",
            "is_dynamic": True,
            "permission": "view_chaptermodel",
        })

    return {
        "SIDEBAR_MENU": 
        [
            {
                "title": "main",
                "permissions": ["is_staff"],
                "items": [
                    {
                        "label": "dashboard",
                        "url_name": "dashboard",
                        "icon": "ti ti-layout-grid",
                    },
                    {
                        "label": "laws",
                        "url_name": "law_list",
                        "icon": "ti ti-gavel",
                        "permission": "view_lawmodel",
                    },
                ],
            },
            {
                "title": "manage_chapters",
                "permissions": ["is_staff"],
                "items": law_items
            },
            {
                "title": "settings",
                "permissions": [
                    "view_sitemodel",
                    "view_languagemodel",
                    "view_textkeymodel",
                ],
                "items": [
                    {
                        "label": "company_settings",
                        "url_name": "site_settings",
                        "icon": "ti ti-building",
                        "permission": "view_sitemodel",
                    },
                    {
                        "label": "language_settings",
                        "url_name": "language_list",
                        "icon": "ti ti-language",
                        "permission": "view_languagemodel",
                    },
                    {
                        "label": "translate_key_settings",
                        "url_name": "text_key_list",
                        "icon": "ti ti-message-language",
                        "permission": "view_textkeymodel",
                    },
                ],
            },
            {
                "title": "user_management",
                "permissions": [
                    "view_usermodel",
                    "view_rolemodel",
                ],
                "items": [
                    {
                        "label": "users",
                        "url_name": "user_list",
                        "icon": "ti ti-shield-up",
                        "permission": "view_usermodel",
                    },
                    {
                        "label": "roles_and_permissions",
                        "url_name": "role_list",
                        "icon": "ti ti-jump-rope",
                        "permission": "view_rolemodel",
                    },
                ],
            },
        ]
    }
