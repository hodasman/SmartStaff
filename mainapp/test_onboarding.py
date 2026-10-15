from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from mainapp.models import Device, DeviceCategory, DeviceType, Platform


class OnboardingFlowTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="onboarding-user",
            first_name="Test",
            date_of_birth="1990-01-01",
            email="onboarding@example.test",
            password="Test-password-123",
        )
        self.user.is_active = True
        self.user.save(update_fields=["is_active"])
        self.client.force_login(self.user)

        self.platform_a = Platform.objects.create(
            title="Platform A",
            description="First ecosystem",
        )
        self.platform_b = Platform.objects.create(
            title="Platform B",
            description="Second ecosystem",
        )
        self.category = DeviceCategory.objects.create(title="Sensors")

    def create_device(self, title, platforms):
        device_type = DeviceType.objects.create(
            title=f"{title} type",
            category=self.category,
        )
        device = Device.objects.create(
            category=self.category,
            device_type=device_type,
            title=title,
            model_name=f"{title} model",
            size="Small",
            power="Battery",
            temperature="0-40 C",
            package_contents="1 device",
        )
        device.ecosystem.set(platforms)
        return device

    def test_answer_no_routes_directly_to_all_ecosystems(self):
        response = self.client.post(
            reverse("mainapp:onboarding_start"),
            {"has_devices": "no"},
        )

        self.assertRedirects(
            response,
            reverse("mainapp:onboarding_ecosystems"),
        )
        ecosystem_response = self.client.get(
            reverse("mainapp:onboarding_ecosystems")
        )
        self.assertContains(ecosystem_response, "Platform A")
        self.assertContains(ecosystem_response, "Platform B")

    def test_personal_account_shows_unselected_ecosystem_and_setup_link(self):
        with self.settings(LANGUAGE_CODE="en"):
            response = self.client.get(
                reverse(
                    "mainapp:personal_page",
                    kwargs={"username": self.user.username},
                )
            )

        self.assertContains(response, "My ecosystem")
        self.assertContains(response, "Choose ecosystem")
        self.assertContains(
            response,
            reverse("mainapp:onboarding_start"),
        )

    def test_personal_account_shows_selected_ecosystem_and_change_link(self):
        self.user.ecosystem = self.platform_a
        self.user.save(update_fields=["ecosystem"])

        with self.settings(LANGUAGE_CODE="en"):
            response = self.client.get(
                reverse(
                    "mainapp:personal_page",
                    kwargs={"username": self.user.username},
                )
            )

        self.assertContains(response, "My ecosystem")
        self.assertContains(response, "Platform A")
        self.assertContains(response, "Change")
        self.assertContains(
            response,
            reverse("mainapp:onboarding_start"),
        )

    def test_onboarding_pages_require_authentication(self):
        self.client.logout()

        response = self.client.get(reverse("mainapp:onboarding_start"))

        self.assertRedirects(
            response,
            f"{reverse('account_login')}?next={reverse('mainapp:onboarding_start')}",
        )

    def test_answer_yes_routes_to_searchable_device_selection(self):
        self.create_device("Motion sensor", [self.platform_a])

        response = self.client.post(
            reverse("mainapp:onboarding_start"),
            {"has_devices": "yes"},
        )

        self.assertRedirects(
            response,
            reverse("mainapp:onboarding_devices"),
        )
        search_response = self.client.get(
            reverse("mainapp:onboarding_devices"),
            {"q": "Motion"},
        )
        self.assertContains(search_response, "Motion sensor")
        self.assertNotContains(search_response, "No devices match your search.")

    def test_search_keeps_selected_devices_outside_current_results(self):
        first_device = self.create_device("Motion sensor", [self.platform_a])
        self.create_device("Door sensor", [self.platform_a])
        self.user.devices.add(first_device)
        self.client.post(
            reverse("mainapp:onboarding_start"),
            {"has_devices": "yes"},
        )

        search_response = self.client.get(
            reverse("mainapp:onboarding_devices"),
            {"q": "Door"},
        )

        self.assertContains(
            search_response,
            f'<input type="hidden" name="devices" value="{first_device.pk}">',
            html=True,
        )
        self.assertContains(search_response, "Door sensor")
        self.assertNotContains(search_response, "Motion sensor")

    def test_selected_devices_limit_ecosystems_and_finish_onboarding(self):
        existing_device = self.create_device(
            "Existing sensor",
            [self.platform_a, self.platform_b],
        )
        selected_device = self.create_device(
            "Selected sensor",
            [self.platform_a],
        )
        self.user.devices.add(existing_device)

        self.client.post(
            reverse("mainapp:onboarding_start"),
            {"has_devices": "yes"},
        )
        selection_response = self.client.post(
            reverse("mainapp:onboarding_devices"),
            {"devices": [str(selected_device.pk)]},
        )
        self.assertRedirects(
            selection_response,
            reverse("mainapp:onboarding_ecosystems"),
        )

        ecosystem_response = self.client.get(
            reverse("mainapp:onboarding_ecosystems")
        )
        self.assertContains(ecosystem_response, "Platform A")
        self.assertNotContains(ecosystem_response, "Platform B")

        completion_response = self.client.post(
            reverse("mainapp:onboarding_ecosystems"),
            {"ecosystem": str(self.platform_a.pk)},
        )
        self.assertRedirects(
            completion_response,
            reverse(
                "mainapp:personal_page",
                kwargs={"username": self.user.username},
            ),
        )

        self.user.refresh_from_db()
        self.assertEqual(self.user.ecosystem, self.platform_a)
        self.assertTrue(self.user.onboarding_completed)
        self.assertSetEqual(
            set(self.user.devices.values_list("pk", flat=True)),
            {existing_device.pk, selected_device.pk},
        )
        self.assertNotIn("onboarding_has_devices", self.client.session)
        self.assertNotIn("onboarding_device_ids", self.client.session)

    def test_incompatible_ecosystem_cannot_complete_onboarding(self):
        selected_device = self.create_device(
            "Selected sensor",
            [self.platform_a],
        )
        self.client.post(
            reverse("mainapp:onboarding_start"),
            {"has_devices": "yes"},
        )
        self.client.post(
            reverse("mainapp:onboarding_devices"),
            {"devices": [str(selected_device.pk)]},
        )

        response = self.client.post(
            reverse("mainapp:onboarding_ecosystems"),
            {"ecosystem": str(self.platform_b.pk)},
        )

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertFalse(self.user.onboarding_completed)
        self.assertIsNone(self.user.ecosystem)
