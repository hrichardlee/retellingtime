$base_dir = "/home/hrichardlee"
$venv_dir = "${base_dir}/retellingtimevenv"
$puppet_manifests_dir = "${base_dir}/manifests"
$source_dir = "${base_dir}/retellingtime"


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
	file { "/etc/init/retellingtime.conf":
		ensure => "file",
		source => "${puppet_manifests_dir}/upstart-retellingtime",
		notify => Service["retellingtime"]
	}

	service { "retellingtime":
		require => File["/etc/init/retellingtime.conf"],
		provider => "upstart",
		ensure => "running"
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

	file { "/etc/nginx/sites-available/retellingtime":
		require => Package["nginx"],
		ensure => "file",
		source => "${puppet_manifests_dir}/nginx-retellingtime",
		notify => Service["nginx"]
	}

	file { "/etc/nginx/sites-enabled/retellingtime":
		require => Package["nginx"],
		ensure => "link",
		target => "/etc/nginx/sites-available/retellingtime",
		notify => Service["nginx"]
	}

	file { "/etc/nginx/ssl":
		require => Package["nginx"],
		ensure => "directory"
	}

	file { "/etc/nginx/ssl/server.crt":
		require => [Package["nginx"], File["/etc/nginx/ssl"]],
		ensure => "file",
		source => "${puppet_manifests_dir}/server.crt",
		notify => Service["nginx"]
	}

	file { "/etc/nginx/ssl/server.key":
		require => [Package["nginx"], File["/etc/nginx/ssl"]],
		ensure => "file",
		source => "${puppet_manifests_dir}/server.key",
		notify => Service["nginx"]
	}
}

