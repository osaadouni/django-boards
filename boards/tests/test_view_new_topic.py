from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse, resolve

from ..forms import NewTopicForm 
from ..models import Board, Topic, Post
from ..views import new_topic


class NewTopicTests(TestCase):
    """
    Test cases for creating a new topic
    """

    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Django board.')
        self.user = User.objects.create_user(username='john', email='john@doe.com', password='testme123')
        self.client.login(username='john', password='testme123')


    def test_new_topic_view_success_status_code(self):
        url = reverse('new_topic', kwargs={'pk': self.board.pk}) 
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_new_topic_view_not_found_status_code(self):
        url = reverse('new_topic', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_new_topic_url_resolve_new_topic_view(self):
        # url = '/boards/{0}/new/'.format(self.board.pk)
        new_topic_url = f'/boards/{self.board.pk}/new/'
        view = resolve(new_topic_url)
        self.assertEqual(view.func, new_topic)
       

    def test_new_topic_view_contains_link_back_to_board_topics_view(self):
        new_topic_url = reverse('new_topic', kwargs={'pk': self.board.pk}) 
        board_topics_url = reverse('board_topics', kwargs={'pk': self.board.pk})     
        response = self.client.get(new_topic_url)

        board_topics_pattern = 'href="{0}"'.format(board_topics_url)
        self.assertContains(response, board_topics_pattern)
        
    def test_new_topic_view_contains_link_back_to_home_view(self):
        new_topic_url = reverse('new_topic', kwargs={'pk': self.board.pk})
        home_url = reverse('home')
  
        response = self.client.get(new_topic_url)
        home_url_pattern = 'href="{0}"'.format(home_url)
        self.assertContains(response, home_url_pattern)


    def test_new_topic_contains_form(self):
        url = reverse('new_topic', kwargs={'pk': self.board.pk})
        response = self.client.get(url)
        form = response.context.get('form')
        self.assertIsInstance(form, NewTopicForm) 
        #self.assertContains(response, '<form')

    def test_new_topic_contains_csrf_token(self):
        url = reverse('new_topic', kwargs={'pk': self.board.pk})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')


    def test_new_topic_valid_post_data(self):
        url = reverse('new_topic', kwargs={'pk': self.board.pk})
        data = {
            'subject': 'Test title', 
            'message': 'Lorem ipsum dolor sit amet.'
        }
        response = self.client.post(url, data)
        self.assertTrue(Topic.objects.exists())
        self.assertTrue(Post.objects.exists())

    def test_new_topic_invalid_post_data(self):
        """
        Invalid post data should not redirect 
        The expected behavior is to show the form again with validations errors
        """
        url = reverse('new_topic', kwargs={'pk': self.board.pk})
        data = {}
        response = self.client.post(url, data)
        form = response.context.get('form')
        self.assertIsInstance(form, NewTopicForm)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)

    def test_new_topic_invalid_post_data_empty_fields(self):
        """
        Invalid post data should not redirect
        The expected behavior is to show the form again with validation errors
        """
        url = reverse('new_topic', kwargs={'pk': self.board.pk})
        data = { 
            'subject': '', 
            'message': '' 
        }
        response = self.client.post(url, data)
        form = response.context.get('form')
        self.assertIsInstance(form, NewTopicForm)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)

        #self.assertFalse(Topic.objects.exists())
        #self.assertFalse(Post.objects.exists())


class LoginRequiredNewTopicTests(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Django board.')
        self.url = reverse('new_topic', kwargs={'pk': self.board.pk})
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url)) 
