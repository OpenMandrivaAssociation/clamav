%if %mdkversion == 300
%define distversion C30
#compatability macros:
%{?!mkrel:%define mkrel(c:) %{-c: 0.%{-c*}.}%{!?_with_unstable:%(perl -e '$_="%{1}";m/(.\*\\D\+)?(\\d+)$/;$rel=${2}-1;re;print "$1$rel";').%{?subrel:%subrel}%{!?subrel:1}.%{?distversion:%distversion}%{?!distversion:%(echo $[%{mdkversion}/10])}}%{?_with_unstable:%{1}}%{?distsuffix:%distsuffix}%{?!distsuffix:mdk}}
%endif

%define	major 2
%define libname %mklibname %{name} %{major}
%define develname %mklibname %{name} -d

%define milter	1

%{?_with_milter:   %{expand: %%global milter 1}}
%{?_without_milter:   %{expand: %%global milter 0}}

%if %mdkversion <= 200710
%define subrel 1
%endif

Summary:	An anti-virus utility for Unix
Name:		clamav
Version:	0.91.2
Release:	%mkrel 4
License:	GPL
Group:		File tools
URL:		http://clamav.sourceforge.net/
Source0:	http://www.clamav.net/%{name}-%{version}.tar.gz
Source1:	http://www.clamav.net/%{name}-%{version}.tar.gz.sig
Source2:	clamav-clamd.init
Source3:	clamav-clamd.logrotate
Source4:	clamav-freshclamd.init
Source5:	clamav-freshclam.logrotate
Source6:	clamav-milter.init
Source7:	clamav-milter.sysconfig
Patch0:		clamav-mdv_conf.diff
Requires(post): clamav-db
Requires(preun): clamav-db
Requires(post): %{libname} = %{version}
Requires(preun): %{libname} = %{version}
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(pre): rpm-helper
Requires(postun): rpm-helper
BuildRequires:	bzip2-devel
BuildRequires:	bc
%if %mdkversion >= 1000
BuildRequires:	autoconf2.5
BuildRequires:	automake1.7
%endif
%if %{milter}
BuildRequires:	sendmail-devel
BuildRequires:	tcp_wrappers-devel
%endif
BuildRequires:	zlib-devel
BuildRequires:	gmp-devel
%if %mdkversion >= 1020
BuildRequires:	multiarch-utils >= 1.0.3
%endif
Conflicts:	clamd < 0.91
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description 
Clam AntiVirus is an anti-virus toolkit for Unix. The main purpose
of this software is the integration with mail seversions (attachment
scanning). The package provides a flexible and scalable
multi-threaded daemon, a commandline scanner, and a tool for
automatic updating via Internet. The programs are based on a
shared library distributed with the Clam AntiVirus package, which
you can use in your own software. 

You can build %{name} with some conditional build swithes;

(ie. use with rpm --rebuild):
    --with[out] milter	Build %{name}-milter (default)

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
Summary:	The Clam AntiVirus sendmail-milter Daemon
Group:		System/Servers
Requires:	%{name} = %{version}
Requires:	clamd = %{version}
Requires:	sendmail
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
The Clam AntiVirus sendmail-milter Daemon
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
Provides:	%{name}-devel = %{version}
Obsoletes:	%{name}-devel
Obsoletes:	%{mklibname clamav 1}-devel
Obsoletes:	%{mklibname clamav 2}-devel

%description -n	%{develname}
This package contains the static %{libname} library and its header
files.

%package -n	clamdmon
Summary:	A little program for checking ClamAV daemon health
Group:		System/Servers
Requires:	clamd = %{version}

%description -n	clamdmon
ClamdMon is a little program for checking ClamAV daemon health. ClamdMon send
to clamd stream, which contain EICAR test signature. If virus found, ClamdMon
will return 1, otherwise 0. It's time to verify database integrity or/and
restart ClamAV daemon...

%prep

%setup -q -n %{name}-%{version}

# clean up
for i in `find . -type d -name CVS` `find . -type f -name .cvs\*` `find . -type f -name .#\*`; do
    if [ -e "$i" ]; then rm -rf $i; fi >&/dev/null
done
	
%patch0 -p1 -b .mdvconf

mkdir -p Mandriva
cp %{SOURCE2} Mandriva/clamav-clamd.init
cp %{SOURCE3} Mandriva/clamav-clamd.logrotate
cp %{SOURCE4} Mandriva/clamav-freshclamd.init
cp %{SOURCE5} Mandriva/clamav-freshclam.logrotate
cp %{SOURCE6} Mandriva/clamav-milter.init
cp %{SOURCE7} Mandriva/clamav-milter.sysconfig

%build
%if %mdkversion > 1000
export WANT_AUTOCONF_2_5=1
libtoolize --copy --force; aclocal-1.7; autoconf; automake-1.7
%endif
%if %mdkversion == 300
%define __libtoolize /bin/true
%endif

%serverbuild

%if %mdkversion == 200710
export CFLAGS="$CFLAGS -fstack-protector-all"
export CXXFLAGS="$CXXFLAGS -fstack-protector-all"
export FFLAGS="$FFLAGS -fstack-protector-all"
%endif

# build some of the contrib stuff
pushd contrib/clamdmon
    tar -zxf clamdmon-*.tar.gz
	pushd clamdmon-*
	    gcc $CFLAGS -o clamdmon clamdmon.c
	popd
popd

export SENDMAIL="%{_libdir}/sendmail"

%configure2_5x \
    --disable-%{name} \
    --with-user=%{name} \
    --with-group=%{name} \
    --with-dbdir=%{_localstatedir}/%{name} \
    --enable-id-check \
    --enable-clamuko \
    --enable-bigstack \
    --with-zlib=%{_prefix} \
    --disable-zlib-vcheck \
%if %{milter}
    --enable-milter --with-tcpwrappers \
%else
    --disable-milter --without-tcpwrappers \
%endif			
    --enable-experimental

#    --enable-debug \

%make 

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

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

# install the logrotate stuff
install -d %{buildroot}%{_sysconfdir}/logrotate.d
install -m644 Mandriva/clamav-clamd.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/clamd
install -m644 Mandriva/clamav-freshclam.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/freshclam

install -d %{buildroot}%{_var}/log/%{name}
touch %{buildroot}%{_var}/log/%{name}/freshclam.log
touch %{buildroot}%{_var}/log/%{name}/clamd.log

# install config files
install -m644 etc/clamd.conf %{buildroot}%{_sysconfdir}/clamd.conf
install -m644 etc/freshclam.conf %{buildroot}%{_sysconfdir}/freshclam.conf

# pid file dir
install -d %{buildroot}%{_var}/run/%{name}

# fix TMPDIR
install -d %{buildroot}%{_localstatedir}/%{name}/tmp

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

chown -R qscand:qscand %{_localstatedir}/%{name}
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

%if %mdkversion >= 1020
%multiarch_binaries %{buildroot}%{_bindir}/clamav-config
%endif

# clamdmon
install -m0755 contrib/clamdmon/clamdmon-*/clamdmon %{buildroot}%{_sbindir}/clamdmon

install -d %{buildroot}%{_sysconfdir}/cron.d
cat > clamdmon.crond << EOF
#!/bin/sh

*/5 * * * * root %{_sbindir}/clamdmon -p %{_localstatedir}/%{name}/clamd.socket
EOF
install -m0755 clamdmon.crond %{buildroot}%{_sysconfdir}/cron.d/clamdmon


%pre
%_pre_useradd %{name} %{_localstatedir}/%{name} /bin/sh

if ! [ -z "`getent group amavis`" ]; then
    gpasswd -a %{name} amavis
fi

%post
%_post_service freshclam
%create_ghostfile %{_var}/log/%{name}/freshclam.log %{name} %{name} 0644

%preun
%_preun_service freshclam

%pre -n clamd
%_pre_useradd %{name} %{_localstatedir}/%{name} /bin/sh

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

%preun -n %{name}-milter
%_preun_service %{name}-milter
%endif

%pre -n %{name}-db
%_pre_useradd %{name} %{_localstatedir}/%{name} /bin/sh

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

%post -n %{libname} -p /sbin/ldconfig

%postun -n %{libname} -p /sbin/ldconfig

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc AUTHORS BUGS ChangeLog FAQ NEWS README test UPGRADE
%doc docs/*.pdf contrib/phishing
%doc README.qmail+qmail-scanner COPYING COPYING.nsis
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/clamd.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/freshclam.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/freshclam
%attr(0755,root,root) %{_initrddir}/freshclam
%{_bindir}/clamscan
%{_bindir}/clamdscan
%{_bindir}/clamconf
%{_bindir}/freshclam
%{_bindir}/sigtool
%{_mandir}/man1/sigtool.1*
%{_mandir}/man1/clamconf.1.*
%{_mandir}/man1/clamdscan.1*
%{_mandir}/man1/clamscan.1*
%{_mandir}/man1/freshclam.1*
%{_mandir}/man5/freshclam.conf.5*
%{_mandir}/man5/clamd.conf.5*
%if !%{milter}
%exclude %{_mandir}/man8/%{name}-milter.8*
%endif
%dir %attr(0755,%{name},%{name}) %{_var}/run/%{name}
%dir %attr(0755,%{name},%{name}) %{_localstatedir}/%{name}
%dir %attr(0755,%{name},%{name}) %{_var}/log/%{name}
%ghost %attr(0644,%{name},%{name}) %{_var}/log/%{name}/freshclam.log

%files -n clamd
%defattr(-,root,root)
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/clamd
%attr(0755,root,root) %{_initrddir}/clamd
%{_sbindir}/clamd
%{_mandir}/man8/clamd.8*
%ghost %attr(0644,%{name},%{name}) %{_var}/log/%{name}/clamd.log

%if %{milter}
%files -n %{name}-milter
%defattr(-,root,root)
%doc %{name}-milter/INSTALL
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/sysconfig/%{name}-milter
%attr(0755,root,root) %{_initrddir}/%{name}-milter
%{_sbindir}/%{name}-milter
%{_mandir}/man8/%{name}-milter.8*
%endif

%files -n %{name}-db
%defattr(-,root,root)
%dir %attr(0755,%{name},%{name}) %{_localstatedir}/%{name}
%attr(0644,%{name},%{name}) %config(noreplace) %{_localstatedir}/%{name}/daily.cvd
%attr(0644,%{name},%{name}) %config(noreplace) %{_localstatedir}/%{name}/main.cvd
%dir %attr(0755,%{name},%{name}) %{_localstatedir}/%{name}/tmp

%files -n %{libname}
%defattr(-,root,root)
%{_libdir}/*.so.%{major}*

%files -n %{develname}
%defattr(-,root,root)
%if %mdkversion >= 1020
%multiarch %{multiarch_bindir}/clamav-config
%endif
%{_bindir}/clamav-config
%{_includedir}/*
%{_libdir}/*.a
%{_libdir}/*.so
%{_libdir}/*.la
%{_libdir}/pkgconfig/libclamav.pc

%files -n clamdmon
%defattr(-,root,root)
%doc contrib/clamdmon/clamdmon-*/COPYING
%doc contrib/clamdmon/clamdmon-*/ChangeLog
%doc contrib/clamdmon/clamdmon-*/clamdmon.sh
%doc contrib/clamdmon/clamdmon-*/readme
%attr(0755,root,root) %config(noreplace) %{_sysconfdir}/cron.d/clamdmon
%attr(0755,root,root) %{_sbindir}/clamdmon
