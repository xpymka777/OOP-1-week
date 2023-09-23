from django.test import TestCase
import datetime
from django.utils import timezone
# Create your tests here.
from django.contrib.auth.models import Permission
from locallibrary.catalog.models import Author
from django.urls import reverse
from locallibrary.catalog.models import BookInstance, Book, Genre
# Language
from django.contrib.auth.models import User


class AuthorListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create 13 authors for pagination tests
        number_of_authors = 13
        for author_num in range(number_of_authors):
            Author.objects.create(first_name='Christian %s' % author_num, last_name='Surname %s' % author_num, )

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/catalog/authors/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)

        self.assertTemplateUsed(resp, 'catalog/author_list.html')

    def test_pagination_is_ten(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue(len(resp.context['author_list']) == 10)

    def test_lists_all_authors(self):
        # Get second page and confirm it has (exactly) remaining 3 items
        resp = self.client.get(reverse('authors') + '?page=2')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue(len(resp.context['author_list']) == 3)


class LoanedBookInstancesByUserListViewTest(TestCase):

    def setUp(self):
        # Создание двух пользователей
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2', password='12345')
        test_user2.save()

        # Создание книги
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        # test_language = Language.objects.create(name='English')
        # test_book = Book.objects.create(title='Book Title', summary='My book summary', isbn='ABCDEFG',
        #                                author=test_author, language=test_language)
        # Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        # test_book.genre.set(genre_objects_for_book)  # Присвоение типов many-to-many напрямую недопустимо
        # test_book.save()

        # Создание 30 объектов BookInstance
        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date = timezone.now() + datetime.timedelta(days=book_copy % 5)
            if book_copy % 2:
                the_borrower = test_user1
            else:
                the_borrower = test_user2
            status = 'm'
            # BookInstance.objects.create(book=test_book, imprint='Unlikely Imprint, 2016', due_back=return_date,
            #                           borrower=the_borrower, status=status)

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('my-borrowed'))
        self.assertRedirects(resp, '/accounts/login/?next=/catalog/mybooks/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('my-borrowed'))

        # Проверка что пользователь залогинился
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # Проверка ответа на запрос
        self.assertEqual(resp.status_code, 200)

        # Проверка того, что мы используем правильный шаблон
        self.assertTemplateUsed(resp, 'catalog/bookinstance_list_borrowed_user.html')


class RenewBookInstancesViewTest(TestCase):

    def setUp(self):
        # Создание пользователя
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        test_user1.save()

        test_user2 = User.objects.create_user(username='testuser2', password='12345')
        test_user2.save()
        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        # Создание книги
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        #test_language = Language.objects.create(name='English')
        #test_book = Book.objects.create(title='Book Title', summary='My book summary', isbn='ABCDEFG',
        #                                author=test_author, language=test_language, )
        # Создание жанра Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        #test_book.genre = genre_objects_for_book
        #test_book.save()

        # Создание объекта BookInstance для для пользователя test_user1
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        #self.test_bookinstance1 = BookInstance.objects.create(book=test_book, imprint='Unlikely Imprint, 2016',
        #                                                     due_back=return_date, borrower=test_user1, status='o')

        # Создание объекта BookInstance для для пользователя test_user2
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        #self.test_bookinstance2 = BookInstance.objects.create(book=test_book, imprint='Unlikely Imprint, 2016',
        #                                                      due_back=return_date, borrower=test_user2, status='o')
