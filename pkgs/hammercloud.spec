# This only works with rhel/centos 7
%global pymajor 2
%global pyminor 7
%global pyver %{pymajor}.%{pyminor}
%global epelver %{pymajor}%{pyminor}
%global __python2 %{_bindir}/python%{pyver}
%global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")
%global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")
%global srcname setuptools
%global _datarootdir /usr/share

Name:           hammercloud
Version:        XXXX
Release:        1.hc%{?dist}
Summary:        log into cloud servers

Group:          Applications/System
License:        custom
URL:            https://github.com/gtmanfred/hammercloud
Source0:        https://pypi.python.org/packages/source/h/%{name}/%{name}-%{version}.tar.gz



BuildRequires: python-setuptools
Requires:      python-requests, pexpect, python >= 2.6, python-beautifulsoup4, python-stevedore, python-yaml, python-jinja2

BuildArch:     noarch

%description
A quick way to log into cloud servers

%prep
%setup -q

%install
%{__rm} -rf %{buildroot}

%{__python2} setup.py install --root %{buildroot}

%clean
%{__rm} -rf %{buildroot}

%files
%{python2_sitelib}/*
%{_bindir}/hc
%defattr(-,root,root,-)
%doc

%changelog
