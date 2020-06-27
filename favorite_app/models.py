
# core Django import
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.functional import cached_property
from django.utils import timezone


class BaseModel(models.Model):
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True


class Category(BaseModel):
    """
    Category model
    """

    name = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        unique=True)

    @cached_property
    def favorite_in_category_count(self):
        return self.favorites.count()

    def __str__(self):
        return "Name: %s" % (self.name)


class FavoriteThings(BaseModel):
    """
    FavoriteThing model
    """

    title = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        unique=True)
    description = models.TextField(blank=True, null=True)
    ranking = models.IntegerField(blank=False, null=False)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='favorites')
    metadata = JSONField(default=dict)
    audit_log = JSONField(default=list)

    class Meta:
        ordering = ('ranking',)

    @cached_property
    def max_ranking(self):
        return FavoriteThings.objects.filter(
            category_id=self.category.id).order_by('-ranking').first().ranking

    def __str__(self):
        return "Title: %s" % (self.title)
