from types import SimpleNamespace
from unittest.mock import Mock

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from mainapp.admin import MAX_ARTICLE_IMAGE_SIZE, validate_article_image_size
from mainapp.models import article_img_path
from mainapp.templatetags.my_tags import render_article_text


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
