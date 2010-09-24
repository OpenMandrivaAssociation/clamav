%define	major 6
%define libname %mklibname %{name} %{major}
%define develname %mklibname %{name} -d

%define milter	1

%{?_with_milter:   %{expand: %%global milter 1}}
%{?_without_milter:   %{expand: %%global milter 0}}

%if %mandriva_branch == Cooker
# Cooker
%define release %mkrel 2
%else
# Old distros
%define subrel 1
%define release %mkrel 0
%endif

Summary:	An anti-virus utility for Unix
Name:		clamav
Version:	0.96.3
Release:	%release
License:	GPL
Group:		File tools
URL:		http://clamav.sourceforge.net/
#Source1:	http://www.clamav.net/%{name}-%{version}.tar.gz.sig
# clamav-0.95+ bundles support for RAR v3 in "libclamav" without permission,
# from Eugene Roshal of RARlabs. There is also patent issues involved.
#
# https://bugzilla.redhat.com/show_bug.cgi?id=334371
# http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=312552
#
# Both Redhat and debian removes this code from the upstream tar ball
# and repackages it.
Source0:	%{name}-%{version}-norar.tar.bz2
Source2:	clamav-clamd.init
Source3:	clamav-clamd.logrotate
Source4:	clamav-freshclamd.init
Source5:	clamav-freshclam.logrotate
Source6:	clamav-milter.init
Source7:	clamav-milter.sysconfig
Source8:	clamav-milter.logrotate
Source9:	clamav-clamd.sysconfig
Source10:	clamav-freshclam.sysconfig
Patch0:		clamav-mdv_conf.diff
Patch1:		clamav-0.95-linkage_fix.diff
Patch2:		clamav-0.95-build_fix.diff
Patch10:	clamav-0.92-private.patch
Patch11:	clamav-0.92-open.patch
Patch12:	clamav-0.95-cliopts.patch
Patch13:	clamav-0.95rc1-umask.patch
Requires(post): clamav-db
Requires(preun): clamav-db
Requires(post): %{libname} = %{version}
Requires(preun): %{libname} = %{version}
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(pre): rpm-helper
Requires(postun): rpm-helper
BuildRequires:	bc
BuildRequires:	bzip2-devel
BuildRequires:	curl-devel
BuildRequires:	ncurses-devel
BuildRequires:	tommath-devel
BuildRequires:	zlib-devel
%if %{milter}
BuildRequires:	sendmail-devel
BuildRequires:	tcp_wrappers-devel
%endif
Conflicts:	clamd < 0.91
%if %mdkversion == 200600
BuildRequires:	gcc-cpp >= 4.0.1-5.1.20060
BuildRequires:	gcc-c++ >= 4.0.1-5.1.20060
%endif
Buildroot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Clam AntiVirus is an anti-virus toolkit for Unix. The main purpose of this
software is the integration with mail seversions (attachment scanning). The
package provides a flexible and scalable multi-threaded daemon, a commandline
scanner, and a tool for automatic updating via Internet. The programs are based
on a shared library distributed with the Clam AntiVirus package, which you can
use in your own software.

You can build %{name} with some conditional build swithes;

(ie. use with rpm --rebuild):
    --with[out] milter	Build %{name}-milter (disabled)

%package -n	clamd
Summary:	The Clam AntiVirus Daemon
Group:		System/Servers
Requires:	%{name} = %{version}
Requires(post): clamav-db
Requires(preun): clamav-db
Requires(post): %{libname} = %{version}
Requires(preun): %{libname} = %{version}
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(pre): rpm-helper
Requires(postun): rpm-helper

%description -n	clamd
The Clam AntiVirus Daemon

%if %{milter}
%package -n	%{name}-milter
Summary:	The Clam AntiVirus milter Daemon
Group:		System/Servers
Requires:	%{name} = %{version}
Requires:	clamd = %{version}
Requires:	tcp_wrappers
Requires(post): clamav-db
Requires(preun): clamav-db
Requires(post): %{libname} = %{version}
Requires(preun): %{libname} = %{version}
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(pre): rpm-helper
Requires(postun): rpm-helper

%description -n	%{name}-milter
The Clam AntiVirus milter Daemon
%endif

%package -n	%{name}-db
Summary:	Virus database for %{name}
Group:		Databases
Requires:	%{name} = %{version}
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(pre): rpm-helper
Requires(postun): rpm-helper

%description -n	%{name}-db
The actual virus database for %{name}

%package -n	%{libname}
Summary:	Shared libraries for %{name}
Group:          System/Libraries

%description -n	%{libname}
Shared libraries for %{name}

%package -n	%{develname}
Summary:	Development library and header files for the %{name} library
Group:		Development/C
Requires:	%{libname} = %{version}
Provides:	%{name}-devel = %{version}-%{release}
Obsoletes:	%{name}-devel
Obsoletes:	%{mklibname clamav 1 -d}
Obsoletes:	%{mklibname clamav 2 -d}
Obsoletes:	%{mklibname clamav 3 -d}

%description -n	%{develname}
This package contains the static %{libname} library and its header
files.

%prep

%setup -q -n %{name}-%{version}

# clean up
for i in `find . -type d -name CVS` `find . -type f -name .cvs\*` `find . -type f -name .#\*` `find . -type d -name .svn`; do
    if [ -e "$i" ]; then rm -rf $i; fi >&/dev/null
done

%patch0 -p1 -b .mdvconf
%patch1 -p1 -b .linkage_fix
%patch2 -p1 -b .build_fix

%patch10 -p1 -b .private
%patch11 -p1 -b .open
%patch12 -p1 -b .cliopts
%patch13 -p1 -b .umask

# we can't ship libclamunrar
if [ -d libclamunrar ]; then
    echo "delete the libclamunrar directory and repackage the tar ball"
    exit 1
fi

mkdir -p libclamunrar{,_iface}
touch libclamunrar/{Makefile.in,all,install}

mkdir -p Mandriva
cp %{SOURCE2} Mandriva/clamav-clamd.init
cp %{SOURCE3} Mandriva/clamav-clamd.logrotate
cp %{SOURCE4} Mandriva/clamav-freshclamd.init
cp %{SOURCE5} Mandriva/clamav-freshclam.logrotate
cp %{SOURCE6} Mandriva/clamav-milter.init
cp %{SOURCE7} Mandriva/clamav-milter.sysconfig
cp %{SOURCE8} Mandriva/clamav-milter.logrotate
cp %{SOURCE9} Mandriva/clamav-clamd.sysconfig
cp %{SOURCE10} Mandriva/clamav-freshclam.sysconfig

%build
%if %mdkversion == 200600
%define __libtoolize /bin/true
%endif

%serverbuild

export CFLAGS="$CFLAGS -I%{_includedir}/tommath"

# IPv6 check is buggy and does not work when there are no IPv6 interface on build machine
export have_cv_ipv6=yes

%configure2_5x \
    --localstatedir=/var/lib \
    --disable-%{name} \
    --with-user=%{name} \
    --with-group=%{name} \
    --with-dbdir=/var/lib/%{name} \
    --disable-rpath \
    --disable-zlib-vcheck \
    --disable-unrar \
    --enable-clamdtop \
    --enable-id-check \
    --enable-clamuko \
    --enable-bigstack \
    --with-zlib=%{_prefix} \
    --with-libbz2-prefix=%{_prefix} \
    --with-system-tommath \
%if %{milter}
    --enable-milter --with-tcpwrappers \
%else
    --disable-milter --without-tcpwrappers \
%endif

# anti rpath hack
perl -pi -e "s|^sys_lib_dlsearch_path_spec=.*|sys_lib_dlsearch_path_spec=\"/%{_lib} %{_libdir}\"|g" libtool

%make

%install
rm -rf %{buildroot}

%makeinstall_std

# install the init scripts
install -d %{buildroot}%{_initrddir}
install -m755 Mandriva/clamav-clamd.init %{buildroot}%{_initrddir}/clamd
install -m755 Mandriva/clamav-freshclamd.init %{buildroot}%{_initrddir}/freshclam

%if %{milter}
# install the init script
install -m755 Mandriva/clamav-milter.init %{buildroot}%{_initrddir}/clamav-milter
# install the milter config
install -d %{buildroot}%{_sysconfdir}/sysconfig
install -m644 Mandriva/clamav-milter.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/%{name}-milter
%endif

# install config files
install -d %{buildroot}%{_sysconfdir}/sysconfig
install -m0644 Mandriva/clamav-clamd.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/clamd
install -m0644 Mandriva/clamav-freshclam.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/freshclam

# install the logrotate stuff
install -d %{buildroot}%{_sysconfdir}/logrotate.d
install -m644 Mandriva/clamav-clamd.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/clamd
install -m644 Mandriva/clamav-freshclam.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/freshclam

%if %{milter}
install -m644 Mandriva/clamav-milter.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/clamav-milter
%endif

install -d %{buildroot}%{_var}/log/%{name}
touch %{buildroot}%{_var}/log/%{name}/freshclam.log
touch %{buildroot}%{_var}/log/%{name}/clamd.log

%if %{milter}
touch %{buildroot}%{_var}/log/%{name}/clamav-milter.log
%endif

# install config files
install -m644 etc/clamd.conf %{buildroot}%{_sysconfdir}/clamd.conf
install -m644 etc/freshclam.conf %{buildroot}%{_sysconfdir}/freshclam.conf

# pid file dir
install -d %{buildroot}%{_var}/run/%{name}

# fix TMPDIR
install -d %{buildroot}/var/lib/%{name}/tmp

cat > README.qmail+qmail-scanner <<EOF
#!/bin/sh
#
# The "temporary" qmail+qmail-scanner HOWTO
# -----------------------------------------
#
# For some unknown and undocumented reason clamdscan stopped working
# in the excellent qmail+qmail-scanner setup somewhere after the
# 20040103 CVS snapshot.
#
# To get it working again everything assigned to the clamav user has
# to be changed to the qscand user by hand.
#
# Hint: Change the config and chown the directories like this:
# (if you are lazy you could just execute this file)

perl -pi -e "s|%{name} %{name}|qscand qscand|g" %{_sysconfdir}/logrotate.d/clamd
perl -pi -e "s|%{name} %{name}|qscand qscand|g" %{_sysconfdir}/logrotate.d/freshclam
perl -pi -e "s|^User %{name}|User qscand|g" %{_sysconfdir}/clamd.conf
perl -pi -e "s|^DatabaseOwner %{name}|DatabaseOwner qscand|g" %{_sysconfdir}/freshclam.conf

chown -R qscand:qscand /var/lib/%{name}
chown -R qscand:qscand %{_var}/log/%{name}
chown -R qscand:qscand %{_var}/run/%{name}

if [ -x %{_initrddir}/clamd ]; then
    %{_initrddir}/clamd restart
fi

if [ -x %{_initrddir}/freshclam ]; then
    %{_initrddir}/freshclam restart
fi

# Regards // Oden Eriksson
EOF

cat > README.urpmi << EOF
clamav-0.95+ bundles support for RAR v3 in "libclamav" without permission,
from Eugene Roshal of RARlabs. There is also patent issues involved.

Therefore Mandriva has been forced to remove the offending code.
EOF

%multiarch_binaries %{buildroot}%{_bindir}/clamav-config

%pre
%_pre_useradd %{name} /var/lib/%{name} /bin/sh

if ! [ -z "`getent group amavis`" ]; then
    gpasswd -a %{name} amavis
fi

%post
%_post_service freshclam
%create_ghostfile %{_var}/log/%{name}/freshclam.log %{name} %{name} 0644

%preun
%_preun_service freshclam

%pre -n clamd
%_pre_useradd %{name} /var/lib/%{name} /bin/sh

%post -n clamd
%_post_service clamd
%create_ghostfile %{_var}/log/%{name}/clamd.log %{name} %{name} 0644

%preun -n clamd
%_preun_service clamd

%postun -n clamd
%_postun_userdel %{name}

%if %{milter}
%post -n %{name}-milter
%_post_service %{name}-milter
%create_ghostfile %{_var}/log/%{name}/clamav-milter.log %{name} %{name} 0644

%preun -n %{name}-milter
%_preun_service %{name}-milter
%endif

%pre -n %{name}-db
%_pre_useradd %{name} /var/lib/%{name} /bin/sh

%post -n %{name}-db
# try to keep most uptodate database
for i in main daily; do
	if [ -f %{_var}/lib/clamav/$i.cvd.rpmnew ]; then
		if [ %{_var}/lib/clamav/$i.cvd.rpmnew -nt %{_var}/lib/clamav/$i.cvd ]; then
			mv -f %{_var}/lib/clamav/$i.cvd.rpmnew %{_var}/lib/clamav/$i.cvd
		else
			rm -f %{_var}/lib/clamav/$i.cvd.rpmnew
		fi
	fi
done

%postun -n %{name}-db
%_postun_userdel %{name}

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc AUTHORS BUGS FAQ NEWS README test UPGRADE README.urpmi
%doc docs/*.pdf
%doc README.qmail+qmail-scanner COPYING*
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/clamd.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/freshclam.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/freshclam
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/sysconfig/freshclam
%attr(0755,root,root) %{_initrddir}/freshclam
%{_bindir}/clambc
%{_bindir}/clamconf
%{_bindir}/clamdscan
%{_bindir}/clamdtop
%{_bindir}/clamscan
%{_bindir}/freshclam
%{_bindir}/sigtool
%{_mandir}/man1/clamconf.1.*
%{_mandir}/man1/clamdscan.1*
%{_mandir}/man1/clamdtop.1*
%{_mandir}/man1/clamscan.1*
%{_mandir}/man1/freshclam.1*
%{_mandir}/man1/sigtool.1*
%{_mandir}/man5/clamd.conf.5*
%{_mandir}/man5/freshclam.conf.5*
%if !%{milter}
%exclude %{_mandir}/man8/%{name}-milter.8*
%endif
%dir %attr(0755,%{name},%{name}) %{_var}/run/%{name}
%dir %attr(0755,%{name},%{name}) /var/lib/%{name}
%dir %attr(0775,%{name},%{name}) %{_var}/log/%{name}
%ghost %attr(0644,%{name},%{name}) %{_var}/log/%{name}/freshclam.log

%files -n clamd
%defattr(-,root,root)
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/clamd
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/sysconfig/clamd
%attr(0755,root,root) %{_initrddir}/clamd
%{_sbindir}/clamd
%{_mandir}/man8/clamd.8*
%ghost %attr(0644,%{name},%{name}) %{_var}/log/%{name}/clamd.log

%if %{milter}
%files -n %{name}-milter
%defattr(-,root,root)
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/clamav-milter.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/sysconfig/%{name}-milter
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/clamav-milter
%attr(0755,root,root) %{_initrddir}/%{name}-milter
%{_sbindir}/%{name}-milter
%{_mandir}/man8/%{name}-milter.8*
%{_mandir}/man5/%{name}-milter.conf.5*
%ghost %attr(0644,%{name},%{name}) %{_var}/log/%{name}/clamav-milter.log
%endif

%files -n %{name}-db
%defattr(-,root,root)
%dir %attr(0755,%{name},%{name}) /var/lib/%{name}
%attr(0644,%{name},%{name}) %config(noreplace) /var/lib/%{name}/daily.cvd
%attr(0644,%{name},%{name}) %config(noreplace) /var/lib/%{name}/main.cvd
%dir %attr(0755,%{name},%{name}) /var/lib/%{name}/tmp

%files -n %{libname}
%defattr(-,root,root)
%{_libdir}/*.so.%{major}*

%files -n %{develname}
%defattr(-,root,root)
%multiarch %{multiarch_bindir}/clamav-config
%{_bindir}/clamav-config
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/*.*a
%{_libdir}/pkgconfig/libclamav.pc
