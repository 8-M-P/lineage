from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db.models import Q
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill


class LastName(models.Model):
    last_name = models.CharField(unique=True, max_length=55, verbose_name="Soy Adı")

    def __str__(self):
        return self.last_name

    class Meta:
        verbose_name = "Soy Adı"
        verbose_name_plural = "Soy Adları"


class CustomAccountManager(BaseUserManager):

    def create_superuser(self, full_name, password, **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self.create_user(full_name, password, **other_fields)

    def create_user(self, full_name, password, **other_fields):

        if not full_name:
            raise ValueError(_('You must provide an full_name'))

        user = self.model(full_name=full_name, **other_fields)
        user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=150, blank=True, verbose_name="İsim")
    last_name = models.CharField(max_length=150, blank=True, verbose_name="Soyisim")
    start_date = models.DateTimeField(default=now, verbose_name="Oluşturma Tarihi", help_text="Hesabı yaratma tarihi.")
    is_staff = models.BooleanField(default=False, verbose_name="Yetkili mi ?",
                                   help_text="Bu hesap site yetkisine sahip mi ?.")
    is_active = models.BooleanField(default=False, verbose_name="Aktif mi ?",
                                    help_text="Hesap kullanılabilirlik durumu.")
    # Custom Fields
    full_name = models.CharField(max_length=40, unique=True, verbose_name="İsim Soyisim")
    avatar = ProcessedImageField(default="avatar.jpeg", upload_to='avatars',
                                 processors=[ResizeToFill(250, 250)], format='JPEG', options={'quality': 60})
    father = models.ForeignKey("self", on_delete=models.SET_NULL, related_name="user_father", verbose_name="Baba",
                               null=True, blank=True)
    mother = models.ForeignKey("self", on_delete=models.SET_NULL, related_name="user_mother", verbose_name="Anne",
                               null=True, blank=True)

    class Gender(models.IntegerChoices):
        MAN = 1, _('Erkek')
        WOMAN = 2, _('Kadın')

    gender = models.PositiveSmallIntegerField(choices=Gender.choices, blank=True, null=True, verbose_name="Cinsiyet")
    birth_date = models.DateTimeField(blank=True, null=True, verbose_name="Doğum Tarihi")
    about = models.TextField(blank=True, verbose_name="Hakkında")
    roles = models.ManyToManyField(LastName, verbose_name="Aile İzinleri",
                                   help_text="Görmek için izinli olduğu soyadları.")
    has_admin_permit = models.BooleanField(default=False)

    objects = CustomAccountManager()
    USERNAME_FIELD = 'full_name'

    def get_roles(self):
        return "\n|\n".join([p.last_name for p in self.roles.all()])

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Kullanıcı"
        verbose_name_plural = "Kullanıcılar"


class Media(models.Model):
    family_tag = models.ManyToManyField(LastName, verbose_name="Aile Etiketleri")
    user_tag = models.ManyToManyField(User, verbose_name="Kişi Etiketleri")
    img_url = models.ImageField()
    thumbnail = ImageSpecField(source='img_url', processors=[ResizeToFill(500, 500)], format='JPEG',
                               options={'quality': 60})
    thumbnail_sm = ImageSpecField(source='img_url', processors=[ResizeToFill(350, 275)], format='JPEG',
                                  options={'quality': 60})
    alt_text = models.CharField(max_length=255, blank=True)
    is_only_my_family = models.BooleanField(default=False, verbose_name="Sadece Ailem görebilir ?")
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def get_family_tag(self):
        return "\n|\n".join([p.last_name for p in self.family_tag.all()])

    def get_user_tag(self):
        return "\n|\n".join([u.full_name for u in self.user_tag.all()])

    class Meta:
        verbose_name = "Resim"
        verbose_name_plural = "Resimler"

    def __str__(self):
        return "|".join([u.full_name for u in self.user_tag.all()])


STATUS_ACTIVE = True
STATUS_CANCELLED = False
STATUS_CHOICES = (
    (STATUS_ACTIVE, 'Aktif'),
    (STATUS_CANCELLED, 'Pasif'),
)


class RequestedUserPermitLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True, choices=STATUS_CHOICES, verbose_name="Durum")

    class Meta:
        verbose_name = "Giriş İzni"
        verbose_name_plural = "Giriş İzinleri"

    def __str__(self):
        return self.user.full_name

    def clean(self):
        if self.status == 1:
            if RequestedUserPermitLog.objects.filter(user=self.user, status=self.status).exists():
                raise ValidationError('Kullanıcı başına sadece 1 aktif istek olabilir.')
