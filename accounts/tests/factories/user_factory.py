import factory
from core.constants import ROLE_USER
from core.constants import LOGIN_EMAIL_PASSWORD
from accounts.models import User, UserSecurity, UserPresence

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True
        
    email = factory.Sequence(lambda n: f"user{n}@test.com")
    username = factory.Sequence(lambda n: f"user{n}")
    
    role = ROLE_USER
    is_active = True
    is_staff = False
    is_superuser = False
    
    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        pwd = extracted or "StrongPass123!"
        self.set_password(pwd)
        if create:
            self.save()
    