%define major 6
%define libname %mklibname %{name} %{major}
%define develname %mklibname %{name} -d

%define _disable_rebuild_configure 1
%define _disable_lto 1

%define milter 1
%{?_with_milter: %{expand: %%global milter 1}}
%{?_without_milter: %{expand: %%global milter 0}}

Summary:	An anti-virus utility for Unix
Name:		clamav
Version:	0.98.7
Release:	5
License:	GPLv2+
Group:		File tools
URL:		http://clamav.sourceforge.net/
#Source1:	http://www.clamav.net/%%{name}-%%{version}.tar.gz.sig
# clamav-0.95+ bundles support for RAR v3 in "libclamav" without permission,
# from Eugene Roshal of RARlabs. There is also patent issues involved.
#
# https://bugzilla.redhat.com/show_bug.cgi?id=334371
# http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=312552
#
# Both Redhat and debian removes this code from the upstream tar ball
# and repackages it.
Source0:	%{name}-%{version}-norar.tar.xz
Source1:	clamd-tmpfiles.conf
Source2:	%{name}-clamd.service
Source3:	%{name}-clamd.logrotate
Source4:	%{name}-freshclam.service
Source5:	%{name}-freshclam.logrotate
Source6:	%{name}-milter.service
Source8:	%{name}-milter.logrotate
# clamd service fails to start on clean systems without these files
Source10:	http://db.local.clamav.net/main.cvd
Source11:	http://db.local.clamav.net/daily.cvd
Source100:	%{name}.rpmlintrc
Patch0:		%{name}-mdv_conf.diff
Patch10:	%{name}-0.97.2-private.patch
Patch12:	%{name}-0.98.5-cliopts.patch
Patch13:	%{name}-0.98-umask.patch
# Fixed in this release
# https://bugzilla.clamav.net/show_bug.cgi?id=5252
#Patch14:	%%{name}-0.97.5-bug5252.diff
Requires(post,preun):	%{name}-db
Requires(post,preun):	%{libname} >= %{version}
Requires(pre,post,post,postun):	rpm-helper
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

%description
Clam AntiVirus is an anti-virus toolkit for Unix. The main purpose of this
software is the integration with mail seversions (attachment scanning). The
package provides a flexible and scalable multi-threaded daemon, a command-line
scanner, and a tool for automatic updating via Internet. The programs are
based on a shared library distributed with the Clam AntiVirus package, which
you can use in your own software.

You can build %{name} with some conditional build switches; (ie. use with rpm
--rebuild): --with[out] milter	Build %{name}-milter (disabled)

%package -n clamd
Summary:	The Clam AntiVirus Daemon
Group:		System/Servers
Requires:	%{name} = %{version}
Requires(post,preun):	%{name}-db
Requires(post,preun):	%{libname} = %{version}
Requires(pre,post):	rpm-helper


%description -n	clamd
The Clam AntiVirus Daemon.

%if %{milter}
%package -n %{name}-milter
Summary:	The Clam AntiVirus milter Daemon
Group:		System/Servers
Requires:	%{name} = %{version}
Requires:	clamd = %{version}
Requires:	tcp_wrappers
Requires(post,preun):	%{name}-db
Requires(pre,post):	rpm-helper
Requires(post,preun):	%{libname} = %{version}


%description -n	%{name}-milter
The Clam AntiVirus milter Daemon.
%endif

%package -n %{name}-db
Summary:	Virus database for %{name}
Group:		Databases
Requires:	%{name} = %{version}
Requires(pre,post):	rpm-helper

%description -n	%{name}-db
The actual virus database for %{name}.


%package -n %{libname}
Summary:	Shared libraries for %{name}
Group:		System/Libraries

%description -n	%{libname}
Shared libraries for %{name}.

%package -n %{develname}
Summary:	Development library and header files for the %{name} library
Group:		Development/C
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}
Obsoletes:	%{name}-devel < %{version}
%rename		%{_lib}clamav1-devel
%rename		%{_lib}clamav2-devel
%rename		%{_lib}clamav3-devel

%description -n	%{develname}
This package contains the development library and header files for the 
%{name} library.

%prep
%setup -q -n %{name}-%{version}

# clean up
for i in `find . -type d -name CVS` `find . -type f -name .cvs\*` `find . -type f -name .#\*` `find . -type d -name .svn`; do
    if [ -e "$i" ]; then rm -rf $i; fi >&/dev/null
done

%patch0 -p1 -b .mdvconf

%patch10 -p1 -b .private
%patch12 -p1 -b .cliopts
%patch13 -p1 -b .umask

# we can't ship libclamunrar
rm -rf libclamunrar
if [ -d libclamunrar ]; then
    echo "delete the libclamunrar directory and repackage the tar ball"
    exit 1
fi
mkdir -p libclamunrar{,_iface}
touch libclamunrar/{Makefile.in,all,install}

mkdir -p OMV
cp %{SOURCE3} OMV/clamav-clamd.logrotate
cp %{SOURCE5} OMV/clamav-freshclam.logrotate
cp %{SOURCE8} OMV/clamav-milter.logrotate

%build
%serverbuild
export CFLAGS="$CFLAGS -I%{_includedir}/tommath"

# IPv6 check is buggy and does not work when there are no IPv6 interface on build machine
export have_cv_ipv6=yes

%configure \
    --localstatedir=/var/lib \
    --disable-%{name} \
    --with-user=%{name} \
    --with-group=%{name} \
    --with-dbdir=/var/lib/%{name} \
    --disable-rpath \
    --disable-unrar \
    --enable-clamdtop \
    --enable-id-check \
    --enable-clamuko \
    --enable-bigstack \
    --with-zlib=%{_prefix} \
    --with-libbz2-prefix=%{_prefix} \
    --with-system-tommath \
%if %{milter}
    --enable-milter --with-tcpwrappers
%else
    --disable-milter --without-tcpwrappers
%endif

# anti rpath hack
perl -pi -e "s|^sys_lib_dlsearch_path_spec=.*|sys_lib_dlsearch_path_spec=\"/%{_lib} %{_libdir}\"|g" libtool

%make

%install
%makeinstall_std

# install the init scripts
install -D -p -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/%{name}-clamd.service
install -D -p -m 644 %{SOURCE4} %{buildroot}%{_unitdir}/%{name}-freshclam.service

install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-clamd.preset << EOF
enable %{name}-clamd.service
EOF

cat > %{buildroot}%{_presetdir}/86-freshclam.preset << EOF
enable %{name}-freshclam.service
EOF

%if %{milter}
# Install the systemd unit+tempfiles
install -D -p -m 644 %{SOURCE6} %{buildroot}%{_unitdir}/%{name}-milter.service
cat > %{buildroot}%{_presetdir}/86-milter.preset << EOF
enable %{name}-milter.service
EOF
%endif

#install tmpfiles
install -D -p -m 644 %{SOURCE1} %{buildroot}%{_tmpfilesdir}/%{name}.conf


# install the logrotate stuff
install -d %{buildroot}%{_sysconfdir}/logrotate.d
install -m644 OMV/%{name}-clamd.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/clamd
install -m644 OMV/%{name}-freshclam.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/freshclam

%if %{milter}
install -m644 OMV/%{name}-milter.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/%{name}-milter
%endif

install -d %{buildroot}%{_var}/log/%{name}
touch %{buildroot}%{_var}/log/%{name}/freshclam.log
touch %{buildroot}%{_var}/log/%{name}/clamd.log

%if %{milter}
touch %{buildroot}%{_var}/log/%{name}/%{name}-milter.log
%endif

# install config files
install -m644 etc/clamd.conf.sample %{buildroot}%{_sysconfdir}/clamd.conf
install -m644 etc/freshclam.conf.sample %{buildroot}%{_sysconfdir}/freshclam.conf

# database files
install -D -m 0644 -p %{SOURCE10} %{buildroot}/var/lib/%{name}/main.cvd
install -D -m 0644 -p %{SOURCE11} %{buildroot}/var/lib/%{name}/daily.cvd

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

systemctl restart clamd.service
systemctl restart freshclam.service

# Regards // OpenMandriva Association
EOF

cat > README.urpmi << EOF
clamav-0.95+ bundles support for RAR v3 in "libclamav" without permission,
from Eugene Roshal of RARlabs. There is also patent issues involved.
Therefore we have been forced to remove the offending code.
EOF

%multiarch_binaries %{buildroot}%{_bindir}/%{name}-config

# cleanup
rm -f %{buildroot}%{_libdir}/*.*a

%pre
%_pre_useradd %{name} /var/lib/%{name} /bin/sh

if ! [ -z "`getent group amavis`" ]; then
    gpasswd -a %{name} amavis
fi

%post
%create_ghostfile %{_var}/log/%{name}/freshclam.log %{name} %{name} 0644

%pre -n clamd
%_pre_useradd %{name} /var/lib/%{name} /bin/sh

%post -n clamd
%create_ghostfile %{_var}/log/%{name}/clamd.log %{name} %{name} 0644

%postun -n clamd
%_postun_userdel %{name}

%if %{milter}
%post -n %{name}-milter
%create_ghostfile %{_var}/log/%{name}/%{name}-milter.log %{name} %{name} 0644
%endif

%pre -n %{name}-db
%_pre_useradd %{name} /var/lib/%{name} /bin/sh

%post -n %{name}-db
# try to keep most uptodate database
for i in main daily; do
	if [ -f %{_var}/lib/%{name}/$i.cvd.rpmnew ]; then
		if [ %{_var}/lib/%{name}/$i.cvd.rpmnew -nt %{_var}/lib/%{name}/$i.cvd ]; then
			mv -f %{_var}/lib/%{name}/$i.cvd.rpmnew %{_var}/lib/%{name}/$i.cvd
		else
			rm -f %{_var}/lib/%{name}/$i.cvd.rpmnew
		fi
	fi
done

%postun -n %{name}-db
%_postun_userdel %{name}

%files
%doc AUTHORS BUGS FAQ NEWS README test UPGRADE README.urpmi
%doc docs/*.pdf
%doc README.qmail+qmail-scanner COPYING*
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/clamd.conf*
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/freshclam.conf*
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/freshclam
%{_presetdir}/86-freshclam.preset
%{_unitdir}/%{name}-freshclam.service
%{_tmpfilesdir}/%{name}.conf
%{_bindir}/clambc
%{_bindir}/clamconf
%{_bindir}/clamdscan
%{_bindir}/clamdtop
%{_bindir}/clamscan
%{_bindir}/clamsubmit
%{_bindir}/freshclam
%{_bindir}/sigtool
%{_mandir}/man1/clambc.1*
%{_mandir}/man1/clamconf.1.*
%{_mandir}/man1/clamdscan.1*
%{_mandir}/man1/clamdtop.1*
%{_mandir}/man1/clamscan.1*
%{_mandir}/man1/clamsubmit.1*
%{_mandir}/man1/freshclam.1*
%{_mandir}/man1/sigtool.1*
%{_mandir}/man5/clamd.conf.5*
%{_mandir}/man5/freshclam.conf.5*
%if !%{milter}
%exclude %{_mandir}/man8/%{name}-milter.8*
%endif
# %dir %attr(0755,%{name},%{name}) %{_var}/run/%{name}
%dir %attr(0755,%{name},%{name}) /var/lib/%{name}
%dir %attr(0775,%{name},%{name}) %{_var}/log/%{name}
%ghost %attr(0644,%{name},%{name}) %{_var}/log/%{name}/freshclam.log


%files -n clamd
%doc AUTHORS README
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/clamd
%{_presetdir}/86-clamd.preset
%{_unitdir}/%{name}-clamd.service
%{_sbindir}/clamd
%{_mandir}/man8/clamd.8*
%ghost %attr(0644,%{name},%{name}) %{_var}/log/%{name}/clamd.log

%if %{milter}
%files -n %{name}-milter
%doc AUTHORS README
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{name}-milter.conf*
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/%{name}-milter
%{_presetdir}/86-milter.preset
%{_unitdir}/%{name}-milter.service
%{_sbindir}/%{name}-milter
%{_mandir}/man8/%{name}-milter.8*
%{_mandir}/man5/%{name}-milter.conf.5*
%ghost %attr(0644,%{name},%{name}) %{_var}/log/%{name}/%{name}-milter.log
%endif

%files -n %{name}-db
%doc AUTHORS README
%dir %attr(0755,%{name},%{name}) /var/lib/%{name}
%config /var/lib/%{name}/*cvd
%dir %attr(0755,%{name},%{name}) /var/lib/%{name}/tmp


%files -n %{libname}
%doc AUTHORS README
%{_libdir}/*.so.%{major}*

%files -n %{develname}
%doc AUTHORS README
%{multiarch_bindir}/%{name}-config
%{_bindir}/%{name}-config
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/libclamav.pc
