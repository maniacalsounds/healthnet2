README

Installation On Rit Lab Machines:

Open your computer's command line and navigate to the place the Healthnet files are stored.
Make sure you within the "mysite" directory of the healthnet files
Make sure Django 1.9 is installed. This can be done from the command line by running "pip install Django==1.9 --user"
Install the fullcalendar django plugin via command line by running: "pip install -e git+https://github.com/rodrigoamaral/django-fullcalendar.git#egg=django-fullcalendar --user"
Install Python's time zone manager: "pip install pytz --user"
Create migrations in the "mysite" folder that has the manage.py file in it by running: "python manage.py makemigrations"
then Migrate: "python manage.py migrate"
then Run the server: "python manage.py runserver"

The application should now be available in your web browser by going to "localhost:8000"

Installation on a personal computer:

Make sure Python 3.4.3 is installed.
Make sure git is installed and in the system's PATH variable.
Open your computer's command line and navigate to the place the Healthnet files are stored.
Make sure you within the "mysite" directory of the healthnet files
Make sure Django 1.9 is installed. This can be done from the command line by running "pip install Django==1.9"
Install the fullcalendar django plugin via command line by running: "pip install -e git+https://github.com/rodrigoamaral/django-fullcalendar.git#egg=django-fullcalendar"
Install Python's time zone manager: "pip install pytz"
Create migrations in the folder that has the manage.py file in it by running: "python manage.py makemigrations"
Migrate: "python manage.py migrate"
Run the server: "python manage.py runserver"

The application should now be available in your web browser by going to "localhost:8000"

C:\Users\Nathan\AppData\Roaming\cabal\bin;C:\Users\Nathan\AppData\Roaming\npm;C:\Program Files\Java\jdk1.8.0_45\bin;C:\Users\Nathan\AppData\Local\GitHub\PortableGit_c2ba306e536fdf878271f7fe636a147ff37326ad\bin

Other files included are the Requirements document for the project and
the test planner to guide testing of the HealthNet

For any questions or issues send Devon Bagley an email at dxb4606@g.rit.edu