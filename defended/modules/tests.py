from rest_framework.test import APITestCase

from accounts.models import User

from .models import Enrollment, Module, Section


class RolePermissionTests(APITestCase):

    def setUp(self):
        self.learner = User.objects.create_user('learner', password='pw', role='USER')
        self.owner = User.objects.create_user('owner', password='pw', role='OWNER')
        self.other_owner = User.objects.create_user('other', password='pw', role='OWNER')
        self.admin = User.objects.create_user('admin', password='pw', role='ADMIN')

        self.published = Module.objects.create(
            title='Phishing', slug='phishing', description='d', category='c',
            created_by=self.owner, status='PUBLISHED'
        )
        self.draft = Module.objects.create(
            title='Draft', slug='draft', description='d', category='c',
            created_by=self.owner, status='DRAFT'
        )
        self.draft_section = Section.objects.create(module=self.draft, title='s', body='b')

    def _module_payload(self):
        return {'title': 'New', 'description': 'd', 'category': 'c'}

    def test_learner_cannot_create_module(self):
        self.client.force_authenticate(self.learner)
        self.assertEqual(self.client.post('/modules/', self._module_payload()).status_code, 403)

    def test_staff_flag_alone_does_not_grant_owner(self):
        self.learner.is_staff = True
        self.learner.save()
        self.client.force_authenticate(self.learner)
        self.assertEqual(self.client.post('/modules/', self._module_payload()).status_code, 403)

    def test_owner_can_create_module(self):
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.post('/modules/', self._module_payload()).status_code, 201)

    def test_owner_cannot_edit_another_owners_module(self):
        self.client.force_authenticate(self.other_owner)
        r = self.client.patch(f'/modules/{self.published.id}/', {'title': 'x'})
        self.assertEqual(r.status_code, 403)

    def test_admin_can_edit_any_module(self):
        self.client.force_authenticate(self.admin)
        r = self.client.patch(f'/modules/{self.draft.id}/', {'title': 'x'})
        self.assertEqual(r.status_code, 200)

    def test_learner_cannot_see_draft_module_or_its_sections(self):
        self.client.force_authenticate(self.learner)
        self.assertEqual(self.client.get(f'/modules/{self.draft.id}/').status_code, 404)
        self.assertEqual(self.client.get(f'/sections/{self.draft_section.id}/').status_code, 404)
        self.assertEqual(self.client.get(f'/modules/{self.draft.id}/schedule/').status_code, 404)

    def test_learner_cannot_edit_own_enrollment(self):
        enrollment = Enrollment.objects.create(user=self.learner, module=self.published)
        self.client.force_authenticate(self.learner)
        r = self.client.patch(f'/enrollments/{enrollment.id}/', {'source': 'ADMIN'})
        self.assertEqual(r.status_code, 403)

    def test_learner_cannot_assign_enrollments(self):
        self.client.force_authenticate(self.learner)
        r = self.client.post(
            '/enrollments/assign/',
            {'module': self.published.id, 'user_ids': [self.learner.id]},
            format='json'
        )
        self.assertEqual(r.status_code, 403)
