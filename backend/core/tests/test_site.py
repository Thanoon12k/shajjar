import io
import shutil
import tempfile
from datetime import timedelta

from django.contrib.admin.sites import site as admin_site
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from accounts.models import User
from campaigns.models import Campaign, CampaignParticipant
from core.stats import impact_stats, survival_rate
from planting.models import PlantingSite
from reports.models import EnvironmentalReport
from species.models import TreeSpecies
from tree_requests.models import TreeRequest
from trees.models import Health, Tree

MEDIA = tempfile.mkdtemp()


def png(name="p.png"):
    buf = io.BytesIO()
    Image.new("RGB", (10, 10), "green").save(buf, "PNG")
    return SimpleUploadedFile(name, buf.getvalue(), content_type="image/png")


@override_settings(MEDIA_ROOT=MEDIA)
class BaseCase(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user("a@x.iq", "pass-Str0ng-1", full_name="أحمد علي")
        self.other = User.objects.create_user("b@x.iq", "pass-Str0ng-1", full_name="بكر")
        self.staff = User.objects.create_user("s@x.iq", "pass-Str0ng-1", full_name="مشرف", role="supervisor", is_staff=True)
        self.sp = TreeSpecies.objects.create(arabic_name="النبك", heat_tolerance=5, drought_tolerance=5, suitable_for_streets=True)


class PublicPagesTests(BaseCase):
    def test_public_pages_render(self):
        PlantingSite.objects.create(name="غابة", latitude=36.3, longitude=43.1, total_trees=10, alive_trees=9)
        for name in ["core:home", "planting:map", "planting:data", "species:list", "campaigns:list", "content:list", "content:law", "content:contribute", "core:impact", "core:about", "accounts:login", "accounts:register"]:
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)

    def test_map_data_contains_sites(self):
        PlantingSite.objects.create(name="شارع الشلالات", latitude=36.38, longitude=43.15, total_trees=120, alive_trees=118)
        data = self.client.get(reverse("planting:data")).json()
        self.assertEqual(data["features"][0]["name"], "شارع الشلالات")

    def test_species_finder_ranks(self):
        TreeSpecies.objects.create(arabic_name="يوكالبتوس", drought_tolerance=2, heat_tolerance=5)
        r = self.client.get(reverse("species:list"), {"place": "streets", "sun": "strong", "water": "low"})
        self.assertEqual(r.context["species"][0].arabic_name, "النبك")


class AuthTests(BaseCase):
    def test_register_and_login(self):
        r = self.client.post(reverse("accounts:register"), {"full_name": "سارة", "email": "Sara@X.iq", "city": "الموصل", "district": "", "phone_number": "", "password1": "Tree-Mosul-2026", "password2": "Tree-Mosul-2026", "wants_to_volunteer": "on"})
        self.assertRedirects(r, reverse("core:activity"))
        u = User.objects.get(email="sara@x.iq")
        self.assertEqual(u.role, "volunteer")
        self.client.logout()
        r = self.client.post(reverse("accounts:login"), {"username": "sara@x.iq", "password": "Tree-Mosul-2026"})
        self.assertEqual(r.status_code, 302)

    def test_protected_pages_redirect(self):
        for name in ["tree_requests:new", "reports:new", "trees:my", "core:activity"]:
            self.assertEqual(self.client.get(reverse(name)).status_code, 302)

    def test_dashboard_team_only(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("core:dashboard")).status_code, 302)
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(reverse("core:dashboard")).status_code, 200)


class TreeRequestTests(BaseCase):
    def payload(self, **kw):
        d = {"location_type": "home", "requested_tree_count": 3, "latitude": "36.3456123", "longitude": "43.145", "address_description": "حي التعليم", "city": "الموصل", "district": "حي التعليم", "watering_commitment": "yes", "contact_phone": "", "notes": ""}
        d.update(kw)
        return d

    def test_create_request_with_photos(self):
        self.client.force_login(self.user)
        r = self.client.post(reverse("tree_requests:new"), {**self.payload(), "photos": [png("a.png"), png("b.png")]})
        req = TreeRequest.objects.get()
        self.assertTrue(req.request_code.startswith("SH-"))
        self.assertEqual(req.images.count(), 2)
        self.assertTrue(req.watering_commitment)
        self.assertRedirects(r, req.get_absolute_url() + "?new=1")
        self.assertEqual(self.user.notifications.count(), 1)

    def test_invalid_count_and_missing_location(self):
        self.client.force_login(self.user)
        r = self.client.post(reverse("tree_requests:new"), self.payload(requested_tree_count=0, latitude=""))
        self.assertEqual(r.status_code, 200)
        self.assertIn("requested_tree_count", r.context["form"].errors)
        self.assertIn("latitude", r.context["form"].errors)
        self.assertFalse(TreeRequest.objects.exists())

    def test_rejects_non_image_and_too_many(self):
        self.client.force_login(self.user)
        bad = SimpleUploadedFile("x.png", b"not an image", content_type="image/png")
        r = self.client.post(reverse("tree_requests:new"), {**self.payload(), "photos": [bad]})
        self.assertIn("photos", r.context["form"].errors)
        r = self.client.post(reverse("tree_requests:new"), {**self.payload(), "photos": [png(f"{i}.png") for i in range(6)]})
        self.assertIn("photos", r.context["form"].errors)

    def test_other_user_cannot_view(self):
        req = TreeRequest.objects.create(user=self.user, location_type="home", requested_tree_count=1, latitude=36, longitude=43, address_description="x")
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(req.get_absolute_url()).status_code, 404)
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(req.get_absolute_url()).status_code, 200)

    def test_timeline_states(self):
        req = TreeRequest(status=TreeRequest.Status.APPROVED)
        states = [s for _, s in req.timeline()]
        self.assertEqual(states[:3], ["done", "done", "current"])
        self.assertEqual(TreeRequest(status="rejected").timeline()[-1][1], "rejected")

    def test_admin_planted_action_registers_trees(self):
        req = TreeRequest.objects.create(user=self.user, location_type="home", requested_tree_count=2, latitude=36, longitude=43, address_description="x", status="distributed")
        ma = admin_site._registry[TreeRequest]
        request = RequestFactory().post("/")
        request.user = self.staff
        request._messages = type("M", (), {"add": lambda *a, **k: None})()
        ma.planted_register_trees(request, TreeRequest.objects.filter(pk=req.pk))
        req.refresh_from_db()
        self.assertEqual(req.status, "planted")
        self.assertEqual(Tree.objects.filter(owner=self.user).count(), 2)
        self.assertTrue(Tree.objects.first().tree_code.startswith("SHJ-"))


class TreeTests(BaseCase):
    def setUp(self):
        super().setUp()
        self.tree = Tree.objects.create(species=self.sp, owner=self.user, planting_date=timezone.localdate() - timedelta(days=184))

    def test_public_profile_and_qr(self):
        r = self.client.get(self.tree.get_absolute_url())
        self.assertContains(r, self.tree.tree_code)
        r = self.client.get(reverse("trees:qr", args=[self.tree.tree_code]))
        self.assertEqual(r["Content-Type"], "image/svg+xml")
        self.assertIn(b"xmlns", r.content)
        self.assertEqual(self.tree.age_days, 184)

    def test_owner_update_changes_tree(self):
        self.client.force_login(self.user)
        r = self.client.post(reverse("trees:update", args=[self.tree.tree_code]), {"photo": png(), "height_cm": 150, "health_status": "excellent", "notes": "", "latitude": "", "longitude": ""})
        self.assertEqual(r.status_code, 302)
        self.tree.refresh_from_db()
        self.assertEqual(self.tree.height_cm, 150)
        self.assertEqual(self.tree.health_status, Health.EXCELLENT)
        self.assertFalse(self.tree.updates.get().verified)

    def test_dead_update_marks_tree_dead(self):
        self.client.force_login(self.staff)
        self.client.post(reverse("trees:update", args=[self.tree.tree_code]), {"photo": png(), "health_status": "dead"})
        self.tree.refresh_from_db()
        self.assertEqual(self.tree.status, Tree.Status.DEAD)
        self.assertTrue(self.tree.updates.get().verified)

    def test_stranger_cannot_update(self):
        self.client.force_login(self.other)
        r = self.client.post(reverse("trees:update", args=[self.tree.tree_code]), {"photo": png(), "health_status": "good"})
        self.assertEqual(r.status_code, 403)

    def test_lookup(self):
        r = self.client.get(reverse("trees:lookup"), {"code": str(self.tree.pk)})
        self.assertRedirects(r, self.tree.get_absolute_url())


class ReportTests(BaseCase):
    def data(self, **kw):
        d = {"category": "tree_cutting", "title": "", "description": "قطع ثلاث أشجار على الرصيف قرب الساحة", "latitude": "36.34", "longitude": "43.14", "address_description": "", "city": "الموصل"}
        d.update(kw)
        return d

    def test_create_report(self):
        self.client.force_login(self.user)
        self.client.post(reverse("reports:new"), self.data())
        rep = EnvironmentalReport.objects.get()
        self.assertTrue(rep.report_code.startswith("ENV-"))
        self.assertEqual(rep.public_stage, 0)

    def test_fire_is_urgent_and_short_description_rejected(self):
        self.client.force_login(self.user)
        self.client.post(reverse("reports:new"), self.data(category="fire"))
        self.assertEqual(EnvironmentalReport.objects.get().priority, "urgent")
        r = self.client.post(reverse("reports:new"), self.data(description="قطع"))
        self.assertIn("description", r.context["form"].errors)

    def test_rate_limit(self):
        self.client.force_login(self.user)
        for _ in range(7):
            self.client.post(reverse("reports:new"), self.data())
        self.assertEqual(EnvironmentalReport.objects.count(), 5)

    def test_privacy(self):
        rep = EnvironmentalReport.objects.create(reporter=self.user, category="waste", description="x" * 20, latitude=36, longitude=43)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(rep.get_absolute_url()).status_code, 404)


class CampaignTests(BaseCase):
    def make(self, **kw):
        d = dict(title="تشجير الغفران", description="-", location_name="الغفران", start_date=timezone.now() + timedelta(days=3), status="published", volunteers_needed=2)
        d.update(kw)
        return Campaign.objects.create(**d)

    def test_join_and_leave(self):
        c = self.make()
        self.client.force_login(self.user)
        self.client.post(reverse("campaigns:join", args=[c.pk]))
        self.client.post(reverse("campaigns:join", args=[c.pk]))
        self.assertEqual(c.participants.count(), 1)
        self.client.post(reverse("campaigns:leave", args=[c.pk]))
        self.assertEqual(c.participants.get().status, CampaignParticipant.Status.CANCELLED)
        self.client.post(reverse("campaigns:join", args=[c.pk]))
        self.assertEqual(c.participants.get().status, CampaignParticipant.Status.REGISTERED)

    def test_deadline_and_capacity(self):
        c = self.make(registration_deadline=timezone.now() - timedelta(hours=1))
        self.client.force_login(self.user)
        self.client.post(reverse("campaigns:join", args=[c.pk]))
        self.assertFalse(c.participants.exists())
        c2 = self.make(volunteers_needed=1)
        CampaignParticipant.objects.create(campaign=c2, user=self.other)
        self.client.post(reverse("campaigns:join", args=[c2.pk]))
        self.assertEqual(c2.participants.count(), 1)

    def test_draft_hidden(self):
        c = self.make(status="draft")
        self.assertEqual(self.client.get(c.get_absolute_url()).status_code, 404)


class StatsTests(BaseCase):
    def test_zero_safe(self):
        self.assertEqual(survival_rate(0, 0), 0)
        self.assertEqual(impact_stats()["survival_rate"], 0)

    def test_combined_stats(self):
        PlantingSite.objects.create(name="س", latitude=36, longitude=43, total_trees=100, alive_trees=90, dead_trees=10)
        Tree.objects.create(species=self.sp, health_status=Health.DEAD, status=Tree.Status.DEAD)
        Tree.objects.create(species=self.sp)
        s = impact_stats()
        self.assertEqual(s["trees"], 102)
        self.assertEqual(s["alive"], 91)
        self.assertEqual(s["survival_rate"], round(91 / 102 * 100, 1))
