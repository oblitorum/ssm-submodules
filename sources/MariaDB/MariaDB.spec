# Restore old style debuginfo creation for rpm >= 4.14.
%undefine _debugsource_packages
%undefine _debuginfo_subpackages

%global libmariadb_commit ae565ee
%global wolfssl_commit 3b3c175

# -*- rpm-spec -*-
Summary:        MariaDB: a very fast and robust SQL database server
Name:           MariaDB
Version:        10.4.32
Release:        4%{?dist}
License:        GPLv2
Group:          Applications/Databases
Vendor:         MariaDB Foundation
BuildRoot:      %_topdir/mariadb-%{version}

Source0:  https://github.com/MariaDB/server/archive/mariadb-%{version}/server-mariadb-%{version}.tar.gz
Source1:  https://github.com/MariaDB/mariadb-connector-c/archive/%{libmariadb_commit}/mariadb-connector-c-%{libmariadb_commit}.tar.gz
Source2:  https://github.com/wolfSSL/wolfssl/archive/%{wolfssl_commit}/wolfssl-%{wolfssl_commit}.tar.gz

Patch0: 0000-Ignore-RPM-Requires-libimf-for-Intel-compiler.patch
Patch1: 0001-Allow-building-with-flto-flag.patch

BuildRequires: bison boost-devel coreutils checkpolicy binutils cmake gcc-c++ gcc make libcurl-devel ncurses-devel systemtap-sdt-devel libevent-devel libaio-devel cracklib-devel glibc-devel zlib-devel xz-devel systemd-devel libxcrypt-devel java-1.8.0-openjdk java-1.8.0-openjdk-headless Judy-devel krb5-devel libxml2-devel libxml2 unixODBC-devel unixODBC openssl-devel pam-devel pkgconf-pkg-config readline-devel policycoreutils libzstd-devel snappy-devel lz4-devel gnutls-devel llvm lld gperftools-devel

%ifarch x86_64
BuildRequires: intel-oneapi-compiler-dpcpp-cpp procps-ng
%endif

%define debug_package %{nil}

%define _rpmdir %_topdir/RPMS
%define _srcrpmdir %_topdir/SRPMS

%define _unpackaged_files_terminate_build 0


%define mysql_vendor MariaDB Foundation
%define mysqlversion %{version}
%define mysqlbasedir /usr
%define mysqldatadir /var/lib/mysql
%define mysqld_user  mysql
%define mysqld_group mysql
%define _bindir     /usr/bin
%define _sbindir    /usr/sbin
%define _sysconfdir /etc
%define restart_flag_dir %{_localstatedir}/lib/rpm-state/mariadb
%define restart_flag %{restart_flag_dir}/need-restart

%define pretrans %{nil}

%{?filter_setup:
%filter_provides_in \.\(test\|result\|h\|cc\|c\|inc\|opt\|ic\|cnf\|rdiff\|cpp\)$
%filter_requires_in \.\(test\|result\|h\|cc\|c\|inc\|opt\|ic\|cnf\|rdiff\|cpp\)$
%filter_from_provides /perl(\(mtr\|My::\)/d
%ifarch x86_64
%filter_from_requires /\(lib\(ft\|lzma\|tokuportability\|imf\)\)\|\(perl(\(.*mtr\|My::\|.*HandlerSocket\|Mysql\)\)/d
%else
%filter_from_requires /\(lib\(ft\|lzma\|tokuportability\)\)\|\(perl(\(.*mtr\|My::\|.*HandlerSocket\|Mysql\)\)/d
%endif
%filter_setup
}

%define ignore #



%description
MariaDB: a very fast and robust SQL database server

It is GPL v2 licensed, which means you can use the it free of charge under the
conditions of the GNU General Public License Version 2 (http://www.gnu.org/licenses/).

MariaDB documentation can be found at https://mariadb.com/kb
MariaDB bug reports should be submitted through https://jira.mariadb.org

# This is a shortcutted spec file generated by CMake RPM generator
# we skip _install step because CPack does that for us.
# We do only save CPack installed tree in _prepr
# and then restore it in build.
%prep
%setup -q -c
%setup -q -T -D -a 1
mv -fT mariadb-connector-c-%{libmariadb_commit}* server-mariadb-%{version}/libmariadb
%setup -q -T -D -a 2
mv -fT wolfssl-%{wolfssl_commit}* server-mariadb-%{version}/extra/wolfssl/wolfssl

%ifarch x86_64
%patch0 -p1 -d server-mariadb-%{version}/
%patch1 -p1 -d server-mariadb-%{version}/
%endif

%build
mkdir cpack_rpm_build_dir
cd cpack_rpm_build_dir
export CPPFLAGS='-ffunction-sections -fdata-sections -Wl,--gc-sections -Wl,--strip-all -Wno-unused-command-line-argument -fuse-ld=lld'
export LDFLAGS='-Wl,--gc-sections -Wl,--strip-all'

%ifarch x86_64
export CPPFLAGS="${CPPFLAGS} -qopt-dynamic-align -static-intel -vec -fslp-vectorize -fvec-peel-loops -fwhole-program-vtables -march=x86-64-v2 -mtune=westmere -msse4.2 -flto"
export LDFLAGS="${LDFLAGS} -static-intel"
source /opt/intel/oneapi/setvars.sh
%endif

'/usr/bin/cmake'  -DRPM=rhel9 \
                  -DLZ4_LIBS=%{_libdir}/liblz4.so \
                  -DWITH_INNODB_LZ4=ON \
                  -DWITH_ROCKSDB_LZ4=ON \
                  -DCMAKE_BUILD_TYPE=Release \
%ifarch x86_64
                  -DCMAKE_C_COMPILER=/opt/intel/oneapi/compiler/latest/bin/icx \
                  -DCMAKE_CXX_COMPILER=/opt/intel/oneapi/compiler/latest/bin/icpx \
                  -DCMAKE_LINKER=/opt/intel/oneapi/compiler/latest/bin/xild \
                  -DCMAKE_AR=/opt/intel/oneapi/compiler/latest/bin/xiar \
%endif
                  -DCMAKE_C_FLAGS="$CPPFLAGS" \
                  -DCMAKE_CXX_FLAGS="$CPPFLAGS" \
                  -DCMAKE_EXE_LINKER_FLAGS="-ltcmalloc_minimal $LD_FLAGS" \
                  -DBUILD_CONFIG=mysql_release \
                  -DWITH_EMBEDDED_SERVER=no \
                  -DWITH_SAFEMALLOC=OFF \
                  -DWITH_SSL=bundled \
                  -DWITH_JEMALLOC=no \
                  -DWITH_WSREP=no \
                  -DWITH_UNIT_TESTS=no \
                  -DPLUGIN_TOKUDB=NO \
                  -DCPACK_PACKAGING_INSTALL_PREFIX=/ ../server-mariadb-%{version}
make %{?_smp_mflags}

%install

cd cpack_rpm_build_dir
cpack -D CPACK_RPM_PACKAGE_RELEASE=%{release} -G RPM
mv *.rpm %_rpmdir

%clean

%changelog
* Fri Jan 19 2024 Gordan Bobic <gordan@shatteredsilicon.net> - 10.4.32-4
  Build time optimisations

* Wed Nov 15 2023 Gordan Bobic <gordan@shatteredsilicon.net> - 10.4.32-3
  Update to 10.4.32

* Fri Oct 27 2023 Gordan Bobic <gordan@shatteredsilicon.net> - 10.4.31-3
  Optimization to reduce binary and package sizes

* Sun Jul  4 2010 Eric Noulard <eric.noulard@gmail.com> - 10.4.31-1
  Generated by CPack RPM (no Changelog file were provided)
