# centos/sclo spec file for php-pecl-xattr, from:
#
# remirepo spec file for php-pecl-xattr
#
# Copyright (c) 2013-2011 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/4.0/
#
# Please, preserve the changelog entries
#
%if 0%{?scl:1}
%global sub_prefix sclo-%{scl_prefix}
%if "%{scl}" == "rh-php56"
%global sub_prefix sclo-php56-
%endif
%if "%{scl}" == "rh-php70"
%global sub_prefix sclo-php70-
%endif
%if "%{scl}" == "rh-php71"
%global sub_prefix sclo-php71-
%endif
%scl_package      php-pecl-xattr
%endif

%global pecl_name xattr
%global with_zts  0%{!?_without_zts:%{?__ztsphp:1}}
%global ini_name  40-%{pecl_name}.ini

Summary:        Extended attributes
Name:           %{?sub_prefix}php-pecl-%{pecl_name}
Version:        1.3.0
Release:        2%{?dist}
License:        PHP
Group:          Development/Languages
URL:            http://pecl.php.net/package/%{pecl_name}
Source0:        http://pecl.php.net/get/%{pecl_name}-%{version}%{?prever}.tgz

BuildRequires:  %{?scl_prefix}php-devel
BuildRequires:  %{?scl_prefix}php-pear

Requires:       %{?scl_prefix}php(zend-abi) = %{php_zend_api}
Requires:       %{?scl_prefix}php(api) = %{php_core_api}

Provides:       %{?scl_prefix}php-%{pecl_name}               = %{version}
Provides:       %{?scl_prefix}php-%{pecl_name}%{?_isa}       = %{version}
Provides:       %{?scl_prefix}php-pecl(%{pecl_name})         = %{version}
Provides:       %{?scl_prefix}php-pecl(%{pecl_name})%{?_isa} = %{version}
%if "%{?scl_prefix}" != "%{?sub_prefix}"
Provides:       %{?scl_prefix}php-pecl-%{pecl_name}          = %{version}-%{release}
Provides:       %{?scl_prefix}php-pecl-%{pecl_name}%{?_isa}  = %{version}-%{release}
%endif

%if 0%{?fedora} < 20 && 0%{?rhel} < 7
# Filter private shared object
%{?filter_provides_in: %filter_provides_in %{_libdir}/.*\.so$}
%{?filter_setup}
%endif


%description
This package allows to manipulate extended attributes on filesystems
that support them.

Package built for PHP %(%{__php} -r 'echo PHP_MAJOR_VERSION.".".PHP_MINOR_VERSION;')%{?scl: as Software Collection (%{scl} by %{?scl_vendor}%{!?scl_vendor:rh})}.


%prep
%setup -q -c

# Don't install/register tests
sed -e 's/role="test"/role="src"/' \
    %{?_licensedir:-e '/LICENSE/s/role="doc"/role="src"/' } \
    -i package.xml

mv %{pecl_name}-%{version}%{?prever} NTS

cd NTS

# Sanity check, really often broken
extver=$(sed -n '/#define PHP_XATTR_VERSION/{s/.* "//;s/".*$//;p}' php_xattr.h)
if test "x${extver}" != "x%{version}%{?prever}"; then
   : Error: Upstream extension version is ${extver}, expecting %{version}%{?prever}.
   exit 1
fi
cd ..

# Create configuration file
cat > %{ini_name} << 'EOF'
; Enable %{pecl_name} extension module
extension=%{pecl_name}.so
EOF


%build
cd NTS
%{_bindir}/phpize
%configure \
    --with-libdir=%{_lib} \
    --with-php-config=%{_bindir}/php-config

make %{?_smp_mflags}


%install
make -C NTS install INSTALL_ROOT=%{buildroot}

# install config file
install -D -m 644 %{ini_name} %{buildroot}%{php_inidir}/%{ini_name}

# Install XML package description
install -D -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml

# Documentation
cd NTS
for i in $(grep 'role="doc"' ../package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 $i %{buildroot}%{pecl_docdir}/%{pecl_name}/$i
done


# when pear installed alone, after us
%triggerin -- %{?scl_prefix}php-pear
if [ -x %{__pecl} ] ; then
    %{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :
fi

# posttrans as pear can be installed after us
%posttrans
if [ -x %{__pecl} ] ; then
    %{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :
fi

%postun
if [ $1 -eq 0 -a -x %{__pecl} ] ; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi


%check
cd NTS
: Minimal load test for NTS extension
%{_bindir}/php --no-php-ini \
    --define extension=%{buildroot}%{php_extdir}/%{pecl_name}.so \
    --modules | grep %{pecl_name}

: Upstream test suite  for NTS extension
TEST_PHP_EXECUTABLE=%{__php} \
TEST_PHP_ARGS="-n -d extension=$PWD/modules/%{pecl_name}.so" \
NO_INTERACTION=1 \
REPORT_EXIT_STATUS=1 \
%{__php} -n run-tests.php --show-diff


%files
%{?_licensedir:%license NTS/LICENSE}
%doc %{pecl_docdir}/%{pecl_name}
%{pecl_xmldir}/%{name}.xml

%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%{pecl_name}.so


%changelog
* Thu Aug 10 2017 Remi Collet <remi@remirepo.net> - 1.3.0-2
- change for sclo-php71

* Fri Nov 11 2016 Remi Collet <remi@fedoraproject.org> - 1.3.0-1
- cleanup for SCLo build

* Wed Sep 14 2016 Remi Collet <remi@fedoraproject.org> - 1.3.0-2
- rebuild for PHP 7.1 new API version

* Mon Mar  7 2016 Remi Collet <remi@fedoraproject.org> - 1.3.0-1
- update to 1.3.0 (stable) - no change since RC1

* Sun Mar  6 2016 Remi Collet <remi@fedoraproject.org> - 1.3.0-0.3.RC1
- adapt for F24

* Tue Oct 13 2015 Remi Collet <remi@fedoraproject.org> - 1.3.0-0.2.RC1
- rebuild for PHP 7.0.0RC5 new API version

* Fri Sep 18 2015 Remi Collet <remi@fedoraproject.org> - 1.3.0-0.1.RC1
- update to 1.3.0RC1
- drop dependency on libxattr

* Fri Sep 18 2015 Remi Collet <remi@fedoraproject.org> - 1.2.1-5
- F23 rebuild with rh_layout

* Wed Jul 22 2015 Remi Collet <remi@fedoraproject.org> - 1.2.1-4
- rebuild against php 7.0.0beta2

* Wed Jul  8 2015 Remi Collet <remi@fedoraproject.org> - 1.2.1-3
- rebuild against php 7.0.0beta1

* Fri Jun 19 2015 Remi Collet <remi@fedoraproject.org> - 1.2.1-2
- allow build against rh-php56 (as more-php56)
- rebuild for "rh_layout" (php70)

* Sun Apr 19 2015 Remi Collet <remi@fedoraproject.org> - 1.2.1-1
- update to 1.2.1
- run upstream test suite during build

* Mon Apr  6 2015 Remi Collet <remi@fedoraproject.org> - 1.2.0-6
- add fix for PHP-7
- drop runtime dependency on pear, new scriptlets
- don't install/register tests

* Wed Dec 24 2014 Remi Collet <remi@fedoraproject.org> - 1.2.0-5.1
- Fedora 21 SCL mass rebuild

* Tue Aug 26 2014 Remi Collet <rcollet@redhat.com> - 1.2.0-5
- improve SCL build

* Thu Apr 17 2014 Remi Collet <remi@fedoraproject.org> - 1.2.0-4
- add numerical prefix to extension configuration file (php 5.6)

* Mon Mar 24 2014 Remi Collet <remi@fedoraproject.org> - 1.2.0-3
- allow SCL build

* Fri Mar 14 2014 Remi Collet <remi@fedoraproject.org> - 1.2.0-2
- install doc in pecl_docdir
- install tests in pecl_testdir
- add missing License file

* Sun Oct  6 2013 Remi Collet <remi@fedoraproject.org> - 1.2.0-1
- initial package
