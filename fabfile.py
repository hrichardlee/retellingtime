from fabric.api import env
from fabric.operations import run, put, sudo
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
	run('puppet module install stankevich/python --version=1.6.3 --modulepath="%s" --force' % puppet_modules_dir)

def put_exec_puppet():
	# the things that go in the puppet config are exclusively things that can
	# be configured without looking at the code
	put('deployment/manifests', base_dir)
	sudo('puppet apply %s/retellingtime.pp --modulepath="%s" --verbose' % (puppet_manifests_dir, puppet_modules_dir))

def install_pip():
	# install pip manually to get the latest version
	run('wget https://raw.github.com/pypa/pip/master/contrib/get-pip.py')
	sudo('python get-pip.py')

def code_independent_setup():
	"""This should only need to be run once for a machine before any code gets
	put on the machine"""
	install_puppet()
	install_puppet_dependencies()
	put_exec_puppet()

	install_pip()


## Utility functions
def ve_run(command, func=run, base_dir=base_dir, *args, **kwargs):
	with cd(base_dir):
		with prefix('source %s/bin/activate' % venv_dir):
			return func(command, *args, **kwargs)


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

def code_setup():
	"""This uploads a new version of source, updates python packages, and
	prepares gunicorn"""
	put_source()
	update_reqs()
	prep_staticfiles()
	restart_gunicorn()


## Needs to happen once after code has been uploaded
def data_setup():
	"""This must be run after the code has been set up on the machine."""
	ve_run('python -m nltk.downloader punkt')
	ve_run('python manage.py syncdb --noinput', base_dir=source_dir)
	# this file contains data for creating a superuser called hrichardlee
	ve_run('python manage.py loaddata deployment/fixtures/hrichardlee-superuser.json', base_dir=source_dir)


## Initial machine setup
def initial_setup():
	"""This takes a fresh machine and sets up everything needed to run the
	application"""
	code_independent_setup()
	code_setup()
	data_setup()