# HR-HMV web platform

The HR-HMV web platform is hosting the Greek registry for patients using home mechanical ventilation, typically due to chronic respiratory or neurological diseases, also including children. All data are stored in a central database, available to the contributing multiple health centers and institutions across the country, mainly for research purposes.


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What tools and packages you need to install on your system:

```
* Python 3.x.x
* Django via pip
* django-crispy-forms via pip
* mysqlclient via pip
* numpy via pip
* pandas via pip
* requests via pip
* urllib3 via pip
```

Alternatively, you can install the requirement packages found in the requirements.txt file via pip:

_pip install -r requirements.txt_


## Deployment

* Rename sample-settings.py file found in hmv directory to settings.py and adjust it in accordance with your setup.
* Just run _python manage.py runserver_ on your local machine **for development and testing purposes**.
* To deploy the project **on a live system**, follow the instructions given by the official documentation of Django: https://docs.djangoproject.com/en/4.0/howto/deployment/

## Built With

* [Python 3.6.7](http://www.python.org/) - Developing with the best programming language
* [Django 2.1.5](https://www.djangoproject.com/) - The web framework for perfectionists with deadlines.

## Authors

* **Vlasios Dimitriadis** - *Initial work* - [mechanical-ventilation](https://github.com/bdimitriadis/mechanical-ventilation)




