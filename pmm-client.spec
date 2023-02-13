%define debug_package %{nil}
%define version 1.17.5
%define patch 2
%define release %{patch}%{?dist}

%define mongodb_exporter_version	9fd6f88
%define mysqld_exporter_version		844ccb5
%define node_exporter_version		cb2dd58
%define percona_toolkit_version		3.4.0
%define pid_watchdog_version		2a86cf7
%define pmm_client_version			f858ca6
%define postgres_exporter_version	3017fce
%define proxysql_exporter_version	bbd1471
%define qan_agent_version			9399e1f
%define go_github_version			25.1.3
%define promu_version				0.1.0


%define _GOPATH %{_builddir}/%{name}-%{version}/go

Name:           pmm-client
Summary:        Percona Monitoring and Management Client
Version:        %{version}
Release:        %{release}
Group:          Applications/Databases
License:        AGPLv3
Vendor:         Percona LLC
URL:            https://percona.com
Source:         pmm-client-%{version}-%{patch}.tar.gz
Source1:		pmm-client.logrotate
AutoReq:        no
BuildRequires:	glibc-devel, golang, unzip
# glibc-static, pth-devel

%description
Percona Monitoring and Management (PMM) is an open-source platform for managing and monitoring MySQL and MongoDB
performance. It is developed by Percona in collaboration with experts in the field of managed database services,
support and consulting.
PMM is a free and open-source solution that you can run in your own environment for maximum security and reliability.
It provides thorough time-based analysis for MySQL and MongoDB servers to ensure that your data works as efficiently
as possible.

%prep
%setup -q

%build
export GOPATH=%{_GOPATH}
export GO111MODULE=off

%{__mkdir_p} %{_GOPATH}/src/github.com/percona
%{__mkdir_p} %{_GOPATH}/src/github.com/shatteredsilicon
%{__mkdir_p} %{_GOPATH}/src/github.com/prometheus
%{__mkdir_p} %{_GOPATH}/src/github.com/google/go-github
%{__mkdir_p} %{_GOPATH}/bin

tar -C %{_GOPATH}/src/github.com/percona -zxf mongodb_exporter-%{mongodb_exporter_version}.tar.gz
tar -C %{_GOPATH}/src/github.com/percona -zxf node_exporter-%{node_exporter_version}.tar.gz
tar -C %{_GOPATH}/src/github.com/percona -zxf percona-toolkit-%{percona_toolkit_version}.tar.gz
tar -C %{_GOPATH}/src/github.com/percona -zxf pid-watchdog-%{pid_watchdog_version}.tar.gz
tar -C %{_GOPATH}/src/github.com/percona -zxf postgres_exporter-%{postgres_exporter_version}.tar.gz
tar -C %{_GOPATH}/src/github.com/percona -zxf proxysql_exporter-%{proxysql_exporter_version}.tar.gz
tar -C %{_GOPATH}/src/github.com/percona -zxf qan-agent-%{qan_agent_version}.tar.gz
tar -C %{_GOPATH}/src/github.com/shatteredsilicon -zxf mysqld_exporter-%{mysqld_exporter_version}.tar.gz
tar -C %{_GOPATH}/src/github.com/shatteredsilicon -zxf pmm-client-%{pmm_client_version}.tar.gz
tar -C %{_GOPATH}/src/github.com/google/go-github -zxf go-github-%{go_github_version}.tar.gz
tar -C %{_GOPATH}/src/github.com/prometheus -zxvf promu-%{promu_version}.tar.gz



pushd %{_GOPATH}/src/github.com/percona
	%{__mv} mongodb_exporter-%{mongodb_exporter_version}	mongodb_exporter
	%{__mv} postgres_exporter-%{postgres_exporter_version}	postgres_exporter
	%{__mv} proxysql_exporter-%{proxysql_exporter_version}	proxysql_exporter
	%{__mv} node_exporter-%{node_exporter_version}		node_exporter
	%{__mv} percona-toolkit-%{percona_toolkit_version}	percona-toolkit
	%{__mv} pid-watchdog-%{pid_watchdog_version}		pid-watchdog
	%{__mv} qan-agent-%{qan_agent_version}			qan-agent

cd %{_GOPATH}/src/github.com/shatteredsilicon
	%{__mv} mysqld_exporter-%{mysqld_exporter_version}	mysqld_exporter
	%{__mv} pmm-client-%{pmm_client_version}		pmm-client


cd %{_GOPATH}/src/github.com/google/go-github
	%{__mv} go-github-%{go_github_version} v25

cd %{_GOPATH}/src/github.com/prometheus
	ln -s ../percona/node_exporter node_exporter
	%{__mv} promu-%{promu_version} promu
	cd promu
	%{__make} build
popd

pushd %{_GOPATH}/src/github.com/percona/node_exporter
	%{__make} %{?_smp_mflags} build
	%{__mv} node_exporter %{_GOPATH}/bin
cd %{_GOPATH}/src/github.com/percona/postgres_exporter
	go build github.com/percona/postgres_exporter/cmd/postgres_exporter
	%{__mv} postgres_exporter %{_GOPATH}/bin
cd %{_GOPATH}/src/github.com/percona/percona-toolkit
	GO111MODULE=on go mod download
	GO111MODULE=on go build ./src/go/pt-mongodb-summary
	%{__cp} pt-mongodb-summary %{_GOPATH}/bin
	%{__cp} bin/pt-mysql-summary %{_GOPATH}/bin
	%{__cp} bin/pt-summary %{_GOPATH}/bin
popd

go install github.com/percona/mongodb_exporter
go install github.com/percona/proxysql_exporter
go install github.com/shatteredsilicon/pmm-client
go install github.com/shatteredsilicon/mysqld_exporter
go install github.com/percona/pid-watchdog
go install github.com/percona/qan-agent/bin/...

strip %{_GOPATH}/bin/* || true

%{__cp} %{_GOPATH}/src/github.com/percona/node_exporter/example.prom			%{_GOPATH}/
%{__cp} %{_GOPATH}/src/github.com/shatteredsilicon/mysqld_exporter/queries-mysqld.yml	%{_GOPATH}/

%install
pushd %{_GOPATH}
install -m 0755 -d $RPM_BUILD_ROOT/%{_sysconfdir}/logrotate.d
install -m 0644 %{SOURCE1} $RPM_BUILD_ROOT/%{_sysconfdir}/logrotate.d/pmm

install -m 0755 -d $RPM_BUILD_ROOT/%{_sbindir}
install -m 0755 bin/pmm-client $RPM_BUILD_ROOT/%{_sbindir}/pmm-admin

install -m 0755 -d $RPM_BUILD_ROOT/usr/local/percona/pmm-client
install -m 0755 -d $RPM_BUILD_ROOT/usr/local/percona/qan-agent/bin
install -m 0755 -d $RPM_BUILD_ROOT/usr/local/percona/pmm-client/textfile-collector
install -m 0755 bin/node_exporter $RPM_BUILD_ROOT/usr/local/percona/pmm-client/
install -m 0755 bin/mysqld_exporter $RPM_BUILD_ROOT/usr/local/percona/pmm-client/
install -m 0755 bin/postgres_exporter $RPM_BUILD_ROOT/usr/local/percona/pmm-client/
install -m 0755 bin/mongodb_exporter $RPM_BUILD_ROOT/usr/local/percona/pmm-client/
install -m 0755 bin/proxysql_exporter $RPM_BUILD_ROOT/usr/local/percona/pmm-client/
install -m 0755 bin/pt-summary $RPM_BUILD_ROOT/usr/local/percona/qan-agent/bin/
install -m 0755 bin/pt-mysql-summary $RPM_BUILD_ROOT/usr/local/percona/qan-agent/bin/
install -m 0755 bin/pt-mongodb-summary $RPM_BUILD_ROOT/usr/local/percona/qan-agent/bin/
install -m 0755 bin/percona-qan-agent $RPM_BUILD_ROOT/usr/local/percona/qan-agent/bin/
install -m 0755 bin/percona-qan-agent-installer $RPM_BUILD_ROOT/usr/local/percona/qan-agent/bin/
install -m 0644 queries-mysqld.yml $RPM_BUILD_ROOT/usr/local/percona/pmm-client
install -m 0755 example.prom $RPM_BUILD_ROOT/usr/local/percona/pmm-client/textfile-collector/

%clean
rm -rf $RPM_BUILD_ROOT

%post
# upgrade
pmm-admin ping > /dev/null
if [ $? = 0 ] && [ "$1" = "2" ]; then
    for file in $(find -L /etc/systemd/system -maxdepth 1 -name "pmm-*")
    do
        network_exists=$(grep -c "network.target" "$file")
        if [ $network_exists = 0 ]; then
            sed -i 's/Unit]/Unit]\nAfter=network.target\nAfter=syslog.target/' "$file"
        fi
    done
    for file in $(find -L /etc/systemd/system -maxdepth 1 -name "pmm-linux-metrics*")
    do
        sed -i  "s/,meminfo_numa /,meminfo_numa,textfile /" "$file"
    done
    pmm-admin restart --all
fi

%preun
# uninstall
if [ "$1" = "0" ]; then
    pmm-admin uninstall
fi

%postun
# uninstall
if [ "$1" = "0" ]; then
    rm -rf /usr/local/percona/pmm-client
    rm -rf /usr/local/percona/qan-agent
    echo "Uninstall complete."
fi

%files
%dir /usr/local/percona/pmm-client
%dir /usr/local/percona/pmm-client/textfile-collector
%dir /usr/local/percona/qan-agent/bin
/usr/local/percona/pmm-client/textfile-collector/*
/usr/local/percona/pmm-client/*
/usr/local/percona/qan-agent/bin/*
%{_sbindir}/pmm-admin
%{_sysconfdir}/logrotate.d/pmm

%changelog
* Mon Feb 13 2023 Jason Ng <oblitorum@gmail.com> - 1.17.5-2
- Upgrade to PMM 1.17.5
- Upgrade percona-toolkit to 3.4.0

* Tue Mar 29 2022 Gordan Bobic <gordan@shatteredsilicon.net> - 1.17.4-13
- Add support for MariaDB 10.5+

* Sun Mar 27 2022 Gordan Bobic <gordan@shatteredsilicon.net> - 1.17.4-12
- Fix SSL / password check for Go 1.12+

* Wed May 05 2021 Gordan Bobic <gordan@shatteredsilicon.net> - 1.17.4-11
- Fix build on aarch64
- Include specific version of promu

* Sun Apr 25 2021 Gordan Bobic <gordan@shatteredsilicon.net> - 1.17.4-10
- Fix systemd service file update bug that kept appending "textfile" collectors

* Sun Apr 25 2021 Gordan Bobic <gordan@shatteredsilicon.net> - 1.17.4-9
- Backport prometheus diskstats fix
- Bundle explicit version of go-github
- Backport fix for delegating to Go's standard reflect version
