from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from django.urls import resolve
from django.test import TestCase

from ..views import signup
from ..forms import SignUpForm


class SignUpTests(TestCase):
    def setUp(self):
        url = reverse('signup')
        self.response = self.client.get(url)
 
    def test_signup_view_success_status_code(self):
        self.assertEqual(self.response.status_code, 200)
    
    def test_signup_url_resolves_signup_view(self):
        view = resolve('/signup/')
        self.assertEqual(view.func, signup)

    def test_signup_view_contains_csrf_token(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_signup_view_contains_user_creation_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, SignUpForm) 

    def test_form_inputs(self):
        """
        The view must contains five inputs: crsf, username, email, 
        password1, password2
        """
        self.assertContains(self.response, '<input', 5)
        self.assertContains(self.response, 'type="text"', 1)
        self.assertContains(self.response, 'type="email"', 1)
        self.assertContains(self.response, 'type="password"', 2)


class SuccessfulSignUpTests(TestCase):
    def setUp(self):
        url = reverse('signup')
        data = { 
            'username': 'john', 
            'email': 'john@doe.com', 
            'password1': 'abcdef123456',
            'password2': 'abcdef123456'
        }
 
        self.response = self.client.post(url, data)
        self.home_url = reverse('home')
        #print(self.response.status_code)

    def test_signup_success_redirection(self):
        """
        A valid form submission should redirect the user to the home page 
        """
        self.assertRedirects(self.response, self.home_url)


    def test_signup_success_user_creation(self):
        self.assertTrue(User.objects.exists())

    def test_signup_success_user_authentication(self):
        """
        Create a new request to an arbitrary page.
        The resulting response should now have a 'user' to its context, 
        after a successful sign up.
        """
        response = self.client.get(self.home_url)
        user = response.context.get('user')
        self.assertTrue(user.is_authenticated)



class InvalidSignUpTests(TestCase):
    def setUp(self):
       url = reverse('signup')
       self.response = self.client.post(url, {})

    def test_signup_failure_status_code(self):
        """
        An invalid form submission should return to the same page 
        """
        self.assertEqual(self.response.status_code, 200)

    def test_signup_failure_form_errors(self):
        form = self.response.context.get('form')
        self.assertTrue(form.errors)

    def test_signup_failure_dont_create_user(self):
        self.assertFalse(User.objects.exists()) 
