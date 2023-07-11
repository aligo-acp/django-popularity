from setuptools import find_packages, setup

setup(
    name='django_popularity',
    version='0.0.0',
    packages=find_packages(exclude=['demo*']),
    install_requires=[
        'django>=3.5',
        'djangorestframework>=3.0',
        'django-appconf>=1.0.0',
        'pytrends>=4.8.0',
        'django_action_reservation @ git+https://github.com/aligo-ai/django-action-reservation.git#egg=django_action_reservation',
    ]
)
