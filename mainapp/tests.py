from types import SimpleNamespace
from unittest.mock import Mock

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils.translation import override

from mainapp.admin import MAX_ARTICLE_IMAGE_SIZE, validate_article_image_size
from mainapp.models import (
    Article,
    ArticleCategory,
    Scenario,
    article_img_path,
)
from mainapp.templatetags.my_tags import render_article_text


class ArticleListPageTests(TestCase):
    def test_article_list_renders_featured_article_without_image(self):
        category = ArticleCategory.objects.create(title="Guides")
        article = Article.objects.create(
            title="A practical smart home guide",
            category=category,
            preambule="A short introduction to the guide.",
            text="Article body.",
        )

        response = self.client.get(reverse("mainapp:articles"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "article-featured-card")
        self.assertContains(response, article.title)
        self.assertContains(response, "article-image-placeholder")
        self.assertContains(
            response,
            reverse("mainapp:article_detail", kwargs={"slug": article.slug}),
        )

        category_response = self.client.get(
            reverse(
                "mainapp:articles_category",
                kwargs={"cat_slug": category.slug},
            )
        )

        self.assertEqual(category_response.status_code, 200)
        self.assertContains(category_response, "article-featured-card")


class SearchFunctionalityTests(TestCase):
    def setUp(self):
        category = ArticleCategory.objects.create(title="Guides")
        self.article = Article.objects.create(
            title="Яркая статья",
            category=category,
            text="Текст статьи.",
        )
        self.scenario = Scenario.objects.create(
            title="Яркий сценарий",
            text="Текст сценария.",
        )

    def test_search_is_case_insensitive_for_cyrillic(self):
        self.assertTrue(
            Article.objects.search("ЯРКАЯ")
            .filter(pk=self.article.pk)
            .exists()
        )
        self.assertTrue(
            Article.objects.search("ТЕКСТ СТАТЬИ")
            .filter(pk=self.article.pk)
            .exists()
        )
        self.assertTrue(
            Scenario.objects.search("ЯРКИЙ").filter(pk=self.scenario.pk).exists()
        )

    def test_short_search_returns_results_without_error(self):
        for query in ("я", "яр"):
            with self.subTest(query=query):
                response = self.client.get(
                    reverse("mainapp:search"),
                    {"q": query},
                )

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, self.article.title)
                self.assertContains(response, self.scenario.title)
                self.assertContains(
                    response,
                    self.scenario.get_absolute_url(),
                )

    def test_search_treats_regex_metacharacters_as_plain_text(self):
        self.article.title = "Температура + датчик"
        self.article.save(update_fields=["title"])

        self.assertTrue(
            Article.objects.search("+").filter(pk=self.article.pk).exists()
        )

    def test_search_results_use_styled_cards_and_escape_article_html(self):
        self.article.text = '<p>Содержимое</p><script>alert("unsafe")</script>'
        self.article.save(update_fields=["text"])

        response = self.client.get(
            reverse("mainapp:search"),
            {"q": "ЯРКАЯ"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "search-result-card")
        self.assertContains(response, "search-results-count")
        self.assertContains(response, "Содержимое")
        self.assertNotContains(
            response,
            '<script>alert("unsafe")</script>',
        )

    def test_search_page_shows_empty_states_for_empty_and_unmatched_queries(self):
        empty_response = self.client.get(reverse("mainapp:search"))
        no_results_response = self.client.get(
            reverse("mainapp:search"),
            {"q": "несуществующий запрос"},
        )

        self.assertEqual(empty_response.status_code, 200)
        self.assertContains(empty_response, "search-empty-state--welcome")
        self.assertEqual(no_results_response.status_code, 200)
        self.assertContains(no_results_response, "search-empty-state")


class TagResultsPageTests(TestCase):
    def setUp(self):
        category = ArticleCategory.objects.create(title="Guides")
        self.article = Article.objects.create(
            title="Tagged article",
            category=category,
            preambule="Article summary",
            text="Article body",
        )
        self.scenario = Scenario.objects.create(
            title="Tagged scenario",
            description="Scenario summary",
            text="Scenario body",
        )
        self.article.tags.add("smart-home")
        self.scenario.tags.add("smart-home")

    def test_tag_page_renders_tagged_articles_and_scenarios_as_cards(self):
        with override("ru"):
            response = self.client.get(
                reverse(
                    "mainapp:list_by_tag",
                    kwargs={"tag_slug": "smart-home"},
                )
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Поиск по тегу")
        self.assertContains(response, "tag-results-heading")
        self.assertContains(response, "search-result-card")
        self.assertContains(response, self.article.title)
        self.assertContains(response, self.scenario.title)
        self.assertContains(
            response,
            reverse("mainapp:article_detail", kwargs={"slug": self.article.slug}),
        )
        self.assertContains(response, self.scenario.get_absolute_url())

    def test_tag_page_handles_invalid_page_numbers(self):
        response = self.client.get(
            reverse("mainapp:list_by_tag", kwargs={"tag_slug": "smart-home"}),
            {"page": "invalid"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article.title)


class ArticleImageRenderingTests(SimpleTestCase):
    def test_renders_safe_formatting_and_uploaded_image_token(self):
        image = SimpleNamespace(
            pk=7,
            image=SimpleNamespace(url="/media/articles_img/article/photo.png"),
            alt='<unsafe "caption">',
        )
        article = SimpleNamespace(
            images=SimpleNamespace(
                filter=Mock(return_value=[image]),
            )
        )

        rendered = render_article_text(
            '<p><strong>Important</strong></p><script>alert("xss")</script>'
            '\n[[article-image:7]]',
            article,
        )

        self.assertIn("<p><strong>Important</strong></p>", rendered)
        self.assertNotIn("<script>", rendered)
        self.assertIn('alert("xss")', rendered)
        self.assertIn(
            '<img src="/media/articles_img/article/photo.png" '
            'alt="&lt;unsafe &quot;caption&quot;&gt;" '
            'class="img-fluid article-inline-image" '
            'style="max-height:600px;width:auto;max-width:100%;object-fit:contain;">',
            rendered,
        )
        self.assertIn("<br>", rendered)

    def test_removes_unsafe_attributes_and_javascript_links(self):
        article = SimpleNamespace(
            images=SimpleNamespace(filter=Mock(return_value=[])),
        )

        rendered = render_article_text(
            '<p onclick="alert(1)">Text</p>'
            '<a href="javascript:alert(1)">link</a>',
            article,
        )

        self.assertEqual(rendered, "<p>Text</p><a>link</a>")

    def test_preserves_article_images_tables_and_youtube_embeds(self):
        article = SimpleNamespace(
            images=SimpleNamespace(filter=Mock(return_value=[])),
        )

        rendered = render_article_text(
            '<table border="1"><tr><td>Cell</td></tr></table>'
            '<img src="/media/photo.jpg" alt="Photo" width="640">'
            '<iframe src="https://www.youtube.com/embed/video-id" '
            'width="640" height="360"></iframe>',
            article,
        )

        self.assertIn('<table border="1">', rendered)
        self.assertIn('<img src="/media/photo.jpg" alt="Photo" width="640">', rendered)
        self.assertIn(
            '<iframe src="https://www.youtube.com/embed/video-id" '
            'width="640" height="360"></iframe>',
            rendered,
        )

    def test_converts_local_development_media_urls_to_relative_urls(self):
        article = SimpleNamespace(
            images=SimpleNamespace(filter=Mock(return_value=[])),
        )

        rendered = render_article_text(
            '<img src="http://0.0.0.0:8000/media/articles_img/photo.jpg" alt="Photo">'
            "<img src='https://localhost:8000/media/articles_img/other.jpg'>",
            article,
        )

        self.assertIn(
            '<img src="/media/articles_img/photo.jpg" alt="Photo">',
            rendered,
        )
        self.assertIn(
            '<img src="/media/articles_img/other.jpg">',
            rendered,
        )
        self.assertNotIn("0.0.0.0", rendered)
        self.assertNotIn("localhost:8000", rendered)

    def test_removes_untrusted_iframe_sources(self):
        article = SimpleNamespace(
            images=SimpleNamespace(filter=Mock(return_value=[])),
        )

        rendered = render_article_text(
            '<iframe src="https://attacker.example/embed/content"></iframe>',
            article,
        )

        self.assertNotIn("attacker.example", rendered)
        self.assertNotIn('src="', rendered)

    def test_unknown_image_token_is_rendered_as_text(self):
        article = SimpleNamespace(
            images=SimpleNamespace(filter=Mock(return_value=[])),
        )

        rendered = render_article_text("[[article-image:9]]", article)

        self.assertEqual(rendered, "[[article-image:9]]")

    def test_article_image_upload_uses_related_article_slug(self):
        image = SimpleNamespace(article=SimpleNamespace(slug="an-article"))

        self.assertEqual(
            article_img_path(image, "photo.png"),
            "articles_img/an-article/photo.png",
        )

    def test_article_image_upload_rejects_files_over_10_mib(self):
        image = SimpleNamespace(size=MAX_ARTICLE_IMAGE_SIZE + 1)

        with self.assertRaises(ValidationError):
            validate_article_image_size(image)

    def test_article_image_upload_accepts_files_at_10_mib(self):
        image = SimpleNamespace(size=MAX_ARTICLE_IMAGE_SIZE)

        validate_article_image_size(image)
