# Core Django import
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
# Local import
from favorite_app.models import Category, FavoriteThings
from favorite_app.mocks import data, set_up_data


class CategoryTestCase(APITestCase):
    """
    Setup test utility
    """

    def setUp(self):
        self.url = reverse('category-list')
        self.category = Category.objects.create(name='person')

    def detail_url(self):
        """
        create a detail url for update or delete
        """

        return reverse('category-detail', kwargs={'pk': self.category.pk})

    def test_create_category_succeeds(self):
        """
        test create new category
        """

        response = self.client.post(self.url, {'name': 'pet'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'pet')
        self.assertEqual(response.data['favorite_in_category_count'], 0)

    def test_get_category_list_succeed(self):
        """
        get list of category
        """

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data['results'], list)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_get_categories_with_favorite_things(self):
        """
        get categories with its assciated favorite things
        """

        url = f'{self.url}?include=children'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data['results'], list)
        self.assertIsInstance(response.data['results'][0]['favorites'], list)

    def test_update_cateory_succeed(self):
        """
        update a category
        """

        response = self.client.patch(self.detail_url(), {'name': 'person'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'person')
        self.assertEqual(response.data['favorite_in_category_count'], 0)

    def test_create_category_without_name_fails(self):
        """
        Ensure you cannot craete a category without name
        """

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_category_succeeeds(self):
        """
        delete category
        """

        response = self.client.delete(self.detail_url())
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class FavoriteThingsTestCase(APITestCase):
    """
    Favorite things test cases
    """

    def setUp(self):
        """
        Setup test utility
        """

        self.url = reverse('favorite-list')
        self.category = Category.objects.create(name='Movies')
        # favorite_data['category'] = self.category.pk
        self.favorte_thing = FavoriteThings.objects.create(
            category=self.category, **set_up_data)

    def detail_url(self):
        """
        create a detail url for update or delete
        """

        return reverse('favorite-detail', kwargs={'pk': self.favorte_thing.pk})

    def test_get_favorite_things_succeeds(self):
        """
        get list of favorite things
        """

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data['results'], list)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_create_favorite_things_succeeds(self):
        """
        create a new favorite things
        """

        data['category'] = self.category.pk
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], data['title'])
        self.assertEqual(
            response.data['description'],
            data['description'])
        self.assertEqual(response.data['ranking'], data['ranking'])

    def test_re_order_favorite_ranking_on_new_favorite_things_creation(self):
        """
        Ensure that a ranking of a favorite thing does not
        repeat and is re-ordered appropriately within a
        particular category
        """

        data['title'] = 'Super Girl'
        data['category'] = self.category.pk

        before_re_ordered_ranking = FavoriteThings.objects.get(
            pk=self.favorte_thing.pk)
        self.assertEqual(before_re_ordered_ranking.ranking, 1)

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['ranking'], 1)

        after_re_ordered_ranking = FavoriteThings.objects.get(
            pk=self.favorte_thing.pk)
        self.assertEqual(after_re_ordered_ranking.ranking, 2)

    def test_get_favorite_things_in_category_succeeds(self):
        """
        get all the favorite things in a category
        """

        url = f'{self.url}?categoryId={self.category.pk}&categoryName={self.category.name}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data['results'], list)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_search_favorites(self):
        """
        get all the favorite things in a category
        """

        url = f'{self.url}?search=Avengers'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data['results'], list)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_audit_log_on_update_succeeds(self):
        """
        Ensure that new changes are logged on update
        """

        before_update = FavoriteThings.objects.get(pk=self.favorte_thing.pk)
        self.assertEqual(len(before_update.audit_log), 0)

        data['title'] = 'Aquaman'
        after_update = self.client.patch(self.detail_url(), data)
        self.assertEqual(len(after_update.data['audit_log']), 1)

    def test_create_favorite_things_with_description_less_than_10_fails(self):
        """
        Ensure favorite tings is not created with description of a character
        less than 10
        """

        new_data = {
            'title': 'superman',
            'description': 'new',
            'category': self.category.pk,

        }
        response = self.client.post(self.url, new_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_favorite_things_with_invalid_querystring_fails(self):
        """
        validate category id in the query string
        """

        url = f'{self.url}?categoryId=any&categoryName={self.category.name}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_favoeite_succeeds(self):
        """
        Ensure that favorite can be deleted
        """

        response = self.client.delete(self.detail_url())
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
