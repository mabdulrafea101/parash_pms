from django.contrib.auth.mixins import UserPassesTestMixin


class ManagerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.user_type == 'manager'


class TeamMemberRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.user_type == 'team_member'


class ClientRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.user_type == 'client'
