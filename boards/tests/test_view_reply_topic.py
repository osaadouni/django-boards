from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse, resolve
from ..models import Board, Topic, Post
from ..views import reply_topic
from ..forms import PostForm


class ReplyTopicTestCase(TestCase):
    '''
    Base test case to be used in all 'reply_logic' view tests 
    '''
    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Django board.')
        self.username = 'john'
        self.password = '123'
        self.user = User.objects.create_user(username=self.username, email='john@doe.com', password=self.password)
        self.topic = Topic.objects.create(subject='Hello, world', board=self.board, starter=self.user)
        #Post.objects.create(message='Lorem ipsum dolor sit amet', topic=self.topic, created_by=user)
        self.url = reverse('reply_topic', kwargs={'pk': self.board.pk, 'topic_pk': self.topic.pk})


class LoginRequiredReplyTopicTests(ReplyTopicTestCase):
    def test_redirection(self):
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{0}?next={1}'.format(login_url, self.url))


class ReplyTopicTests(ReplyTopicTestCase):

    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
     
    def test_success_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200) 

    def test_url_resolves_correct_view(self):
        view = resolve('/boards/{board_pk}/topics/{topic_pk}/reply/'.format(
            board_pk=self.board.pk, topic_pk=self.topic.pk
        ))
        self.assertEqual(view.func, reply_topic)

    def test_csrf_token(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        response = self.client.get(self.url)
        form = response.context.get('form')
        self.assertIsInstance(form, PostForm) 

    def test_form_inputs(self):
        '''
        The view contains 2 inputs: csrf and textarea 
        '''
        response = self.client.get(self.url)
        self.assertContains(response, '<input', 1) 
        self.assertContains(response, '<textarea', 1) 


class SuccessfulReplyTopicTests(ReplyTopicTestCase):
    def setUp(self):
        super().setUp()
        Post.objects.create(message='Lorem ipsum dolor sit amet', topic=self.topic, created_by=self.user)
        self.client.login(username=self.username, password=self.password)

    def test_redirection(self):
        data = {'message': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit'}
        response = self.client.post(self.url, data)
        url = reverse('topic_posts', kwargs={'pk': self.board.pk, 'topic_pk': self.topic.pk})
        topic_posts_url = '{url}?page=1#2'.format(url=url)
        self.assertRedirects(response, topic_posts_url)

    def test_did_create_post(self):
        self.assertTrue(Post.objects.exists())



class InvalidReplyTopicTests(ReplyTopicTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
   
    def test_status_code(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 200) 

    def test_did_not_create_post(self):
        self.assertFalse(Post.objects.exists())
