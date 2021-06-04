import airflow
from airflow import models, settings
from airflow.contrib.auth.backends.password_auth import PasswordUser


def SetPassword():
    user = PasswordUser(models.User())

    user.username = input('Please input a username')
    user.email = input('Please input an E-Mail address')
    user.password = input('Please input a Password')
    session = settings.Session()
    session.add(user)
    session.commit()
    session.close()

if __name__ == "__main__":
    SetPassword()
