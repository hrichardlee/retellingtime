$base_dir = "/home/hrichardlee"
$venv_dir = "${base_dir}/retellingtimevenv"
$puppet_manifests_dir = "${base_dir}/manifests"
$source_dir = "${base_dir}/retellingtime"

include rabbitmq
include celery
include flower

class rabbitmq {
	include apt

	apt::key { "rabbitmq-key":
		key_source => "http://www.rabbitmq.com/rabbitmq-signing-key-public.asc"
	}

	apt::source { "rabbitmq":
		require => Apt::Key["rabbitmq-key"],
		location => "http://www.rabbitmq.com/debian/",
		release => "testing",
		repos => "main"
	}

	package { "rabbitmq-server":
		require => Apt::Source["rabbitmq"],
		ensure => "installed"
	}

	exec { "stop-rabbitmq-init":
		require => Package["rabbitmq-server"],
		command => "rabbitmq-server stop",
		returns => [0, 1],
		path => "/etc/init.d/"
	}

	file { "/etc/rc0.d/K20rabbitmq-server":
		require => Package["rabbitmq-server"],
		ensure => absent
	}
	file { "/etc/rc1.d/K20rabbitmq-server":
		require => Package["rabbitmq-server"],
		ensure => absent
	}
	file { "/etc/rc2.d/S20rabbitmq-server":
		require => Package["rabbitmq-server"],
		ensure => absent
	}
	file { "/etc/rc3.d/S20rabbitmq-server":
		require => Package["rabbitmq-server"],
		ensure => absent
	}
	file { "/etc/rc4.d/S20rabbitmq-server":
		require => Package["rabbitmq-server"],
		ensure => absent
	}
	file { "/etc/rc6.d/S20rabbitmq-server":
		require => Package["rabbitmq-server"],
		ensure => absent
	}

	file { "/etc/init/rabbitmq-server.conf":
		require => Package["rabbitmq-server"],
		ensure => "file",
		source => "${puppet_manifests_dir}/upstart-rabbitmq-server",
		notify => Service["rabbitmq-server"]
	}

	service { "rabbitmq-server":
		require => File["/etc/init/rabbitmq-server.conf"],
		provider => "upstart",
		ensure => "running"
	}
}

class celery {
	require rabbitmq

	file { "/etc/init/retellingtime-celery.conf":
		ensure => "file",
		source => "${puppet_manifests_dir}/upstart-retellingtime-celery",
		notify => Service["retellingtime-celery"]
	}

	service { "retellingtime-celery":
		require => File["/etc/init/retellingtime-celery.conf"],
		provider => "upstart",
		ensure => "running"
	}
}

class flower {
	require celery

	file { "/etc/init/flower.conf":
		ensure => "file",
		source => "${puppet_manifests_dir}/upstart-flower",
		notify => Service["flower"]
	}

	service { "flower":
		require => File["/etc/init/flower.conf"],
		provider => "upstart",
		ensure => "running"
	}
}