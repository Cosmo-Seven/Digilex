from django.test import TestCase, Client
from django.urls import reverse
from core.models import LawModel, ChapterModel, SectionModel, UserModel

class LawAccessTestCase(TestCase):
    def setUp(self):
        # Create user
        self.user = UserModel.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123"
        )
        
        # Create a free law
        self.free_law = LawModel.objects.create(
            title="Free Law",
            description="This is a free law description",
            is_free=True
        )
        # Create a chapter for free law
        self.free_chapter = ChapterModel.objects.create(
            law=self.free_law,
            chapter_number="Chapter 1",
            title="Introduction to Free Law"
        )
        # Create a section for free chapter
        self.free_section = SectionModel.objects.create(
            chapter=self.free_chapter,
            section_number="Section 1",
            title="Free Section Title",
            offense="Some free offense",
            penalty="Some free penalty"
        )

        # Create a paid law
        self.paid_law = LawModel.objects.create(
            title="Paid Law",
            description="This is a paid law description",
            is_free=False
        )
        # Create a chapter for paid law
        self.paid_chapter = ChapterModel.objects.create(
            law=self.paid_law,
            chapter_number="Chapter 1",
            title="Introduction to Paid Law"
        )
        # Create a section for paid chapter
        self.paid_section = SectionModel.objects.create(
            chapter=self.paid_chapter,
            section_number="Section 1",
            title="Paid Section Title",
            offense="Some paid offense",
            penalty="Some paid penalty"
        )

        self.client = Client()

    def test_anonymous_user_can_access_free_law(self):
        # Access chapter page for free law
        response = self.client.get(reverse('chapter', kwargs={'law_id': self.free_law.id}))
        self.assertEqual(response.status_code, 200)

        # Access section page for free law chapter
        response = self.client.get(reverse('section', kwargs={'chapter_id': self.free_chapter.id}))
        self.assertEqual(response.status_code, 200)

        # Access section detail page for free law section
        response = self.client.get(reverse('section_detail', kwargs={'section_id': self.free_section.id}))
        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_cannot_access_paid_law(self):
        # Try accessing chapter page for paid law - should redirect to login
        response = self.client.get(reverse('chapter', kwargs={'law_id': self.paid_law.id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

        # Try accessing section page for paid law chapter - should redirect to login
        response = self.client.get(reverse('section', kwargs={'chapter_id': self.paid_chapter.id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

        # Try accessing section detail page for paid law section - should redirect to login
        response = self.client.get(reverse('section_detail', kwargs={'section_id': self.paid_section.id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

    def test_authenticated_user_can_access_any_law(self):
        # Log in the user
        self.client.login(email="testuser@example.com", password="password123")

        # Access chapter page for free law
        response = self.client.get(reverse('chapter', kwargs={'law_id': self.free_law.id}))
        self.assertEqual(response.status_code, 200)

        # Access chapter page for paid law
        response = self.client.get(reverse('chapter', kwargs={'law_id': self.paid_law.id}))
        self.assertEqual(response.status_code, 200)

        # Access section page for paid law chapter
        response = self.client.get(reverse('section', kwargs={'chapter_id': self.paid_chapter.id}))
        self.assertEqual(response.status_code, 200)

        # Access section detail page for paid law section
        response = self.client.get(reverse('section_detail', kwargs={'section_id': self.paid_section.id}))
        self.assertEqual(response.status_code, 200)

    def test_bookmark_toggle_flow(self):
        # 1. Unauthenticated user
        response = self.client.post(reverse('toggle_bookmark'), data={'section_id': str(self.free_section.id)}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content.decode(), {
            'success': False,
            'error': 'login_required',
            'message': 'Please login to bookmark sections.'
        })

        # 2. Authenticated user
        self.client.login(email="testuser@example.com", password="password123")
        
        # Toggle Bookmark (Add)
        response = self.client.post(reverse('toggle_bookmark'), data={'section_id': str(self.free_section.id)}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['bookmarked'])
        
        # Verify it exists in database
        from core.models import BookmarkModel
        self.assertTrue(BookmarkModel.objects.filter(user=self.user, section=self.free_section).exists())

        # Toggle Bookmark again (Remove)
        response = self.client.post(reverse('toggle_bookmark'), data={'section_id': str(self.free_section.id)}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertFalse(data['bookmarked'])
        
        # Verify removed from database
        self.assertFalse(BookmarkModel.objects.filter(user=self.user, section=self.free_section).exists())

    def test_bookmarks_page_requires_login(self):
        # 1. Anonymous user should redirect to login
        response = self.client.get(reverse('bookmarks'))
        self.assertEqual(response.status_code, 302)

        # 2. Logged in user can view
        self.client.login(email="testuser@example.com", password="password123")
        response = self.client.get(reverse('bookmarks'))
        self.assertEqual(response.status_code, 200)

    def test_chapter_page_paginates_six_per_page(self):
        law = LawModel.objects.create(title="Paginated Law", description="Many chapters", is_free=True)
        for i in range(1, 14):
            ChapterModel.objects.create(
                law=law,
                chapter_number=f"Chapter {i}",
                title=f"Title {i}"
            )

        response = self.client.get(reverse('chapter', kwargs={'law_id': law.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['chapters']), 6)
        self.assertEqual(response.context['page_obj'].paginator.num_pages, 3)

        page_two = self.client.get(reverse('chapter', kwargs={'law_id': law.id}), {'page': 2})
        self.assertEqual(page_two.status_code, 200)
        self.assertEqual(len(page_two.context['chapters']), 6)

    def test_download_section_pdf(self):
        # Download PDF as anonymous user for a free section
        response = self.client.get(reverse('download_section_pdf', kwargs={'section_id': self.free_section.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue('attachment' in response['Content-Disposition'])

    def test_download_section_txt(self):
        # Download TXT as anonymous user for a free section
        response = self.client.get(reverse('download_section_txt', kwargs={'section_id': self.free_section.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain; charset=utf-8')
        self.assertTrue('attachment' in response['Content-Disposition'])
