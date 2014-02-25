$base_dir = "/home/hrichardlee"
$venv_dir = "${base_dir}/anankevenv"
$puppet_manifests_dir = "${base_dir}/manifests"
$source_dir = "${base_dir}/ananke"


include py
# git is only necessary for the Wikipedia pip install requirement
include git
include upstart
include webserver


class git {
	package { "git":
		ensure => "installed"
	}
}

class upstart {
	file { "/etc/init/ananke.conf":
		ensure => "file",
		source => "${puppet_manifests_dir}/upstart-ananke"
	}
}

# pip is installed separately because we want to download the latest version
class py { 
	class { "python":
		version => "system",
		dev => true,
		virtualenv => true
	}
	->
	python::virtualenv { $venv_dir:
		ensure => present,
		owner => "hrichardlee",
		group => "hrichardlee"
	}
}

class webserver {
	package { "nginx":
		ensure => "installed"
	}

	service { "nginx":
		require => Package["nginx"],
		ensure => running,
		enable => true
	}

	file { "/etc/nginx/sites-enabled/default":
		require => Package["nginx"],
		ensure => absent,
		notify => Service["nginx"]
	}

	file { "/etc/nginx/sites-available/ananke":
		require => Package["nginx"],
		ensure => "file",
		source => "${puppet_manifests_dir}/nginx-ananke",
		notify => Service["nginx"]
	}

	file { "/etc/nginx/sites-enabled/ananke":
		require => Package["nginx"],
		ensure => "link",
		target => "/etc/nginx/sites-available/ananke",
		notify => Service["nginx"]
	}
}

