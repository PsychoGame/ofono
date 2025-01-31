Name:       ofono
Summary:    Open Source Telephony
Version:    1.25
Release:    1
License:    GPLv2
URL:        https://github.com/sailfishos/ofono
Source:     %{name}-%{version}.tar.bz2

%define libglibutil_version 1.0.51

Requires:   dbus
Requires:   systemd
Requires:   libglibutil >= %{libglibutil_version}
Recommends: mobile-broadband-provider-info
Recommends: ofono-configs
Requires(preun): systemd
Requires(post): systemd
Requires(postun): systemd

# license macro and Recommends tag require reasonably fresh rpm
BuildRequires:  rpm >= 4.12
BuildRequires:  pkgconfig(dbus-1)
BuildRequires:  pkgconfig(dbus-glib-1)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(libudev) >= 145
BuildRequires:  pkgconfig(libwspcodec) >= 2.0
BuildRequires:  pkgconfig(libglibutil) >= %{libglibutil_version}
BuildRequires:  pkgconfig(libdbuslogserver-dbus)
BuildRequires:  pkgconfig(libdbusaccess)
BuildRequires:  pkgconfig(mobile-broadband-provider-info)
BuildRequires:  pkgconfig(systemd)
BuildRequires:  libtool
BuildRequires:  automake
BuildRequires:  autoconf

%description
Telephony stack

%package devel
Summary:    Headers for oFono
Requires:   %{name} = %{version}-%{release}

%description devel
Development headers and libraries for oFono

%package tests
Summary:    Test Scripts for oFono
Requires:   %{name} = %{version}-%{release}
Requires:   dbus-python3
Requires:   python3-gobject
Provides:   ofono-test >= 1.0
Obsoletes:  ofono-test < 1.0

%description tests
Scripts for testing oFono and its functionality

%package doc
Summary:   Documentation for %{name}
Requires:  %{name} = %{version}-%{release}

%description doc
Man pages for %{name}.

%prep
%setup -q -n %{name}-%{version}/%{name}

./bootstrap

%build
autoreconf --force --install

%configure --disable-static \
    --enable-test \
    --enable-sailfish-bt \
    --enable-sailfish-debuglog \
    --enable-sailfish-provision \
    --enable-sailfish-pushforwarder \
    --enable-sailfish-access \
    --disable-add-remove-context \
    --disable-rilmodem \
    --disable-isimodem \
    --disable-qmimodem \
    --with-systemdunitdir=%{_unitdir}

%make_build

%check
# run unit tests
make check

%install
rm -rf %{buildroot}
%make_install

mkdir -p %{buildroot}/%{_sysconfdir}/ofono/push_forwarder.d
mkdir -p %{buildroot}%{_unitdir}/network.target.wants
mkdir -p %{buildroot}/var/lib/ofono
ln -s ../ofono.service %{buildroot}%{_unitdir}/network.target.wants/ofono.service

mkdir -p %{buildroot}%{_docdir}/%{name}-%{version}
install -m0644 -t %{buildroot}%{_docdir}/%{name}-%{version} \
        ChangeLog AUTHORS README

%preun
if [ "$1" -eq 0 ]; then
systemctl stop ofono.service ||:
fi

%post
systemctl daemon-reload ||:
# Do not restart during update
# We don't want to break anything during update
# New daemon is taken in use after reboot
# systemctl reload-or-try-restart ofono.service ||:

%postun
systemctl daemon-reload ||:

%transfiletriggerin -- %{_libdir}/ofono/plugins
systemctl try-restart ofono.service ||:

%files
%defattr(-,root,root,-)
%license COPYING
%config %{_sysconfdir}/dbus-1/system.d/*.conf
%{_sbindir}/*
%{_unitdir}/network.target.wants/ofono.service
%{_unitdir}/ofono.service
%dir %{_sysconfdir}/ofono/
%dir %{_sysconfdir}/ofono/push_forwarder.d
# This file is part of phonesim and not needed with ofono.
%exclude %{_sysconfdir}/ofono/phonesim.conf
%dir %attr(775,radio,radio) /var/lib/ofono

%files devel
%defattr(-,root,root,-)
%{_includedir}/ofono/
%{_libdir}/pkgconfig/ofono.pc

%files tests
%defattr(-,root,root,-)
%{_libdir}/%{name}/test/*

%files doc
%defattr(-,root,root,-)
%{_mandir}/man8/%{name}d.*
%{_docdir}/%{name}-%{version}
