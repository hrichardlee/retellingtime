from fabric.api import env
from fabric.operations import run, put, sudo, local
from fabric.context_managers import cd, prefix, settings
from fabric.contrib.project import rsync_project


# This fab file is designed to work against Ubuntu 12.04 Server Precise
# Pangolin


# Uncomment this line and add the right hosts
# env.hosts= ['192.168.56.103']

base_dir = '/home/hrichardlee'
puppet_modules_dir = base_dir + '/.puppet/modules'
puppet_manifests_dir = base_dir + '/manifests'
venv_dir = base_dir + '/retellingtimevenv' # linked to the puppet recipe
source_dir = base_dir + '/retellingtime'


## Initial code-independent configuration
def install_puppet():
	# this only works for Ubuntu 12 (Precise Pangolin)
	run('wget https://apt.puppetlabs.com/puppetlabs-release-precise.deb')
	sudo('dpkg -i puppetlabs-release-precise.deb')
	sudo('apt-get update')
	sudo('apt-get install puppet -y')

def install_puppet_dependencies():
	# this should really be read from data somewhere
	# for retellingtime.pp
	run('puppet module install stankevich/python --version=1.6.3 --modulepath="%s" --force' % puppet_modules_dir)

	# for worker-role.pp
	run('puppet module install puppetlabs/apt --version=1.4.1 --modulepath="%s" --force' % puppet_modules_dir)
	run('puppet module install puppetlabs/stdlib --version=4.1.0 --modulepath="%s" --force' % puppet_modules_dir)

def put_manifests():
	put('deployment/manifests', base_dir)

def webserver_puppet():
	exec_puppet('retellingtime.pp')

def install_pip():
	# install pip manually to get the latest version
	run('wget https://raw.github.com/pypa/pip/master/contrib/get-pip.py')
	sudo('python get-pip.py')

def code_independent_setup():
	"""This should only need to be run once for a machine before any code gets
	put on the machine"""
	install_puppet()
	install_puppet_dependencies()
	put_manifests()
	webserver_puppet()

	install_pip()


## Utility functions
def ve_run(command, func=run, base_dir=base_dir, *args, **kwargs):
	with cd(base_dir):
		with prefix('source %s/bin/activate' % venv_dir):
			return func(command, *args, **kwargs)

def exec_puppet(manifest):
	# the things that go in the puppet config are exclusively things that can
	# be configured without looking at the code
	sudo('puppet apply %s/%s --modulepath="%s" --verbose' % (puppet_manifests_dir, manifest, puppet_modules_dir))


## Source
def put_source():
	rsync_project(remote_dir=source_dir, local_dir='./', exclude='.git', extra_opts='--filter=":- .gitignore"')

def update_reqs():
	ve_run('pip install -r requirements.txt', base_dir=source_dir)

def prep_staticfiles():
	ve_run('python manage.py collectstatic --noinput', base_dir=source_dir)
	run('rm -rf %s/staticfiles' % base_dir)
	run('mv -f %s/staticfiles %s/' % (source_dir, base_dir))

def restart_gunicorn():
	with settings(warn_only=True):
		sudo('stop retellingtime')

	sudo('start retellingtime')

def restart_celery():
	with settings(warn_only = True):
		sudo('stop retellingtime-celery')
	sudo('start retellingtime-celery')

def code_setup():
	"""This uploads a new version of source, updates python packages, and
	prepares gunicorn"""
	put_source()
	update_reqs()
	prep_staticfiles()
	restart_gunicorn()
	restart_celery()


## Needs to happen once after code has been uploaded
def data_setup():
	"""This must be run after the code has been set up on the machine."""
	ve_run('python -m nltk.downloader punkt')
	run('rm -f %s/db.sqlite3' % source_dir)
	ve_run('python manage.py syncdb --noinput', base_dir=source_dir)
	# fixtures include data for creating a superuser called hrichardlee and
	# loading initial test data
	ve_run('python manage.py loaddata deployment/fixtures/*.json', base_dir=source_dir)


## Initial machine setup
def initial_setup():
	"""This takes a fresh machine and sets up everything needed to run the
	application"""
	code_independent_setup()
	code_setup()
	data_setup()
	worker_puppet()


## Worker role setup
def worker_puppet():
	exec_puppet('worker-role.pp')


# Sass only works in VirtualBox Shared folder in version 3.2.10 (do not go
# higher) Polling with rb-inotify for sass does not work, and django's
# runserver also starts polling manually in virtualbox shared folders. So the
# server needs to be restarted every time the files are touched
def devgo():
	with settings(warn_only=True):
		local('kill `pgrep -f "python manage.py runserver"`')
	local('sass --update timelineviewer/sass:timelineviewer/static/timelineviewer/css/')
	local('python manage.py runserver 0.0.0.0:8000 --noreload')

def devresetdb():
	local('rm db.sqlite3 --force')
	local('python manage.py syncdb --noinput')
	local('python manage.py loaddata deployment/fixtures/*.json')

def devbg():
	local('celery -A timelinedata worker -l info')