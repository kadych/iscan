#  iscan.spec.in -- an rpm spec file template
#  Copyright (C) 2004--2006  Olaf Meeuwissen
#  Copyright (C) 2009  SEIKO EPSON CORPORATION
#
#  This file is part of the "Image Scan!" build infra-structure.
#
#  The "Image Scan!" build infra-structure is free software.
#  You can redistribute it and/or modify it under the terms of the GNU
#  General Public License as published by the Free Software Foundation;
#  either version 2 of the License or at your option any later version.
#
#  This program is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY;  without even the implied warranty of FITNESS
#  FOR A PARTICULAR PURPOSE or MERCHANTABILITY.
#  See the GNU General Public License for more details.
#
#  You should have received a verbatim copy of the GNU General Public
#  License along with this program; if not, write to:
#
#	 Free Software Foundation, Inc.
#	 59 Temple Place, Suite 330
#	 Boston, MA  02111-1307	 USA

# Use RPM defaults for backward compatibility with older
# distributions.
%define _binary_filedigest_algorithm    1
%define _source_filedigest_algorithm    1
%define _binary_payload                 w9.gzdio
%define _source_payload                 w9.gzdio

#  Readability macro to help determine libltdl's version at RPM build time.
%define ltdl_v7	`find /usr/lib /usr/lib64 -maxdepth 2 -name "libltdl.so.7*"   2> /dev/null`
%define usb_10	`find /usr/lib /usr/lib64 -maxdepth 2 -name "libusb-1.0.so.*" 2> /dev/null`

#  Some handy macro definitions.
#
%define pkg	iscan
%define ver	2.30.1
%define rel	1
%define subrel	%(if test -n "%{usb_10}"; then \
                    echo '.usb1.0'; \
                  else \
                    if test -n "%{ltdl_v7}"; then \
                       echo '.usb0.1.ltdl7'; \
                    else \
                       echo '.usb0.1.ltdl3'; \
                    fi; \
                  fi)
%define msg	%{_tmppath}/%{pkg}-%{ver}-%{rel}.msg

%define supported_archs		i386 i486 i586 i686 x86_64 amd64
%define gimp_api_versions	1.2 2.0

%if "%{_vendor}" == "Mandriva"
%define subrel avasys.%{distsuffix}%{mandriva_release}
%endif

# 	general package information

Name:		%{pkg}
Version:	%{ver}
Release:	%{rel}%{subrel}
Source:		%{pkg}_%{ver}-%{rel}.tar.gz
License:	GPL (with exception clauses) and AVASYSPL

Vendor:		SEIKO EPSON CORPORATION
URL:		http://download.ebz.epson.net/dsc/search/01/search/?OSC=LX
Packager:	AVASYS CORPORATION

PreReq:		sane-backends
Requires:	iscan-data
Conflicts:	iscan-network-nt < 1.1, iscan-plugin-cx4400 < 2.1, iscan-plugin-gt-7200 < 2.1, iscan-plugin-gt-7300 < 2.1, iscan-plugin-gt-9400 < 2.1, iscan-plugin-gt-f500 < 2.1, iscan-plugin-gt-f520 < 2.1, iscan-plugin-gt-f600 < 2.1, iscan-plugin-gt-f670 < 2.1, iscan-plugin-gt-f700 < 2.1, iscan-plugin-gt-s600 < 2.1, iscan-plugin-gt-x750 < 2.1

BuildRoot:	%{_tmppath}/%{pkg}-%{ver}-%{rel}-root
BuildRequires:	libusb >= 0.1.6, libxml2-devel

%ifarch %{supported_archs}
BuildRequires:	gtk2-devel, libpng-devel, libjpeg-devel, libtiff-devel

%if "%{_vendor}" == "Mandriva"
BuildRequires:	libltdl-devel, libgimp2.0-devel, libsane1-devel
%else
BuildRequires:	libtool-ltdl-devel, gimp-devel, sane-backends-devel
%endif

%endif

Group:		Applications/Multimedia
%ifnarch %{supported_archs}
Summary:	SANE backend for SEIKO EPSON scanners and all-in-ones
%description
The scanner driver provided by this package can be used by any SANE
standard compliant scanner utility.

Note that some scanners are only supported on selected architectures.
%else
Summary: simple, easy to use scanner utility for EPSON scanners
%description
Image Scan! is a graphical scanner utility for people that do not need
all the bells and whistles provided by several of the other utilities
out there (xsane, QuiteInsane, Kooka).

At the moment it only supports SEIKO EPSON scanners and all-in-ones.
However, the scanner driver it provides can be used by any other SANE
standard compliant scanner utility.

Note that several scanners require a non-free plugin before they can
be used with this software.
%endif


# 	rpmbuild sections

%prep
%setup -q


%build
%if "%{_vendor}" == "Mandriva"
%define _disable_libtoolize 1
%define _requires_exceptions devel(libgcc_s)\\|devel(libm)\\|devel(libstdc++)
%endif
%ifarch %{supported_archs}
%configure \
	--enable-dependency-reduction \
	--enable-frontend \
	--enable-gimp \
	--enable-jpeg \
	--enable-tiff \
	--enable-png
%else
%configure
%endif
make


%install
rm -rf ${RPM_BUILD_ROOT}
make install DESTDIR=${RPM_BUILD_ROOT}
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/lib/%{pkg}
mkdir -p ${RPM_BUILD_ROOT}%{_datadir}/applications
install -m 0644 %{pkg}.desktop ${RPM_BUILD_ROOT}%{_datadir}/applications
#
#  Recent rpmbuild versions follow a FASCIST packaging policy and bomb
#  out on any installed files that are not packaged and non-installed
#  files that are.  Clean up 'make install's act here.
#
sane_confdir=%{_sysconfdir}/sane.d
./mkinstalldirs -m 0755 ${RPM_BUILD_ROOT}${sane_confdir}
install -m 0644 backend/epkowa.conf ${RPM_BUILD_ROOT}${sane_confdir}
rm ${RPM_BUILD_ROOT}%{_libdir}/sane/libsane-epkowa.so
rm ${RPM_BUILD_ROOT}%{_libdir}/sane/libsane-epkowa.a
#
#  Create a list of message catalogs that should be included in the RPM
#  binary package.  Use %lang(ll) notation so that sysadmins can choose
#  the catalogs they want installed.
#
> %{msg}
cd ${RPM_BUILD_ROOT}/%{_datadir}/locale
for lang in *
do
    test -f ${lang}/LC_MESSAGES/%{pkg}.mo || continue
    ll=`echo ${lang} | sed 's,@.*$,,'`
    echo "%lang(${ll}) %{_datadir}/locale/${lang}/LC_MESSAGES/%{pkg}.mo" \
	>> %{msg}
done


%clean
make clean			# rm -rf %{_builddir}/%{name}-%{version}
rm -rf ${RPM_BUILD_ROOT}
rm -f %{msg}


# 	rpm (un)installation scripts

#  Believe it or not, but there are distros out there that do not have
#  the sane service listed in their /etc/services.  Also note that the
#  official service name, as registered with the IANA is not sane, but
#  sane-port.  The saned alias is also commonly used.
#
%pre
srv=/etc/services
if [ -z "`grep 6566/tcp ${srv}`" ]
then
    cat >> ${srv} <<EOF
sane-port       6566/tcp   sane saned   # SANE Control Port
sane-port       6566/udp   sane saned   # SANE Control Port
EOF
fi


%post
#
#  Enable the epkowa backend unconditionally, assuming that people who
#  install this package want to use it.
#
dll=%{_sysconfdir}/sane.d/dll.conf
if [ -n "`grep '#[[:space:]]*epkowa' ${dll}`" ]
then				# uncomment existing entry
    sed -i 's,#[[:space:]]*\(epkowa\),\1,' ${dll}
elif [ -z "`grep epkowa ${dll}`" ]
then				# append brand new entry
    echo epkowa >> ${dll}
fi
#
#  Enable the GIMP plug-ins functionality system wide.
#
if test -x %{_bindir}/iscan
then
    for prefix in %{_libdir} /opt/gnome/lib /opt/gnome/lib64
    do
        [ -d ${prefix} ] || continue
        for version in %{gimp_api_versions}
        do
	    dir=${prefix}/gimp/${version}/plug-ins
            [ -d ${dir} ] || mkdir -p ${dir}
	    ln -fs %{_bindir}/iscan ${dir}
        done
    done
    plugindir="`gimptool --gimpplugindir 2> /dev/null`"
    if [ x  = x"${plugindir}" ]; then
        plugindir="`gimptool-2.0 --gimpplugindir 2> /dev/null`"
    fi
    if [ x != x"${plugindir}" ]; then
        ln -fs %{_bindir}/iscan ${plugindir}/plug-ins
    fi
fi


#  Clean up files created in our %%post.
#
%preun
STATE_DIR=%{_localstatedir}/lib/%{pkg}
VERSION=%{ver}-%{rel}
PATH=%{_libdir}/%{pkg}:$PATH
if  test -f $STATE_DIR/interpreter; then
    test -s $STATE_DIR/interpreter || rm $STATE_DIR/interpreter
fi


%postun
if [ $1 = 0 ]			#  Disable the backend we provided.
then
    dll=%{_sysconfdir}/sane.d/dll.conf
    if [ -n "`grep ^epkowa ${dll}`" ]
    then
	sed -i 's/^epkowa/#epkowa/' ${dll}
    fi
fi
#
#  Clean up our data and library directories, but only if empty.
#
rmdir %{_datadir}/%{pkg} 2> /dev/null || true
rmdir %{_libdir}/%{pkg}  2> /dev/null || true
#
#  Clean out any additions to the top-level usermap and clean up empty
#  files and directories
#
map=%{_sysconfdir}/hotplug/usb.usermap
header='# Following info courtesy of Image Scan!'
footer='# Preceding info courtesy of Image Scan!'
if [ -f $map ]; then
    if [ -n "$(grep "$header" $map)" ]; then
	sed -i "/^$header/,/^$footer/d" $map
    fi
    test -s $map || rm $map
    rmdir %{_sysconfdir}/hotplug 2> /dev/null || true
fi
#
#  Clean up the GIMP plug-ins.
#
for prefix in %{_libdir} /opt/gnome/lib /opt/gnome/lib64
do
    for version in %{gimp_api_versions}
    do
	dir=${prefix}/gimp/${version}/plug-ins
	rm    ${dir}/iscan 2> /dev/null || true
	rmdir ${dir}       2> /dev/null || true
	rmdir `dirname ${dir}` 2> /dev/null || true
    done
    rmdir ${prefix}/gimp 2> /dev/null || true
done
plugindir="`gimptool --gimpplugindir 2> /dev/null`"
if [ x  = x"${plugindir}" ]; then
    plugindir="`gimptool-2.0 --gimpplugindir 2> /dev/null`"
fi
if [ x != x"${plugindir}" ]; then
    rm ${plugindir}/plug-ins/iscan 2> /dev/null || true
fi


# 	package contents

#  Note that we generate the %%{msg} file during the %%install phase
#  so that we can use %%lang(xx) notation without the need to resort
#  to a manually maintained list here.
#
%files -f %{msg}
%defattr(-,root,root)

%doc NEWS    README    AUTHORS
%doc COPYING
%doc non-free/AVASYSPL.en.txt
#  This should really go into ${RPM_DOC_DIR}/examples/.
%doc doc/xinetd.sane

%doc NEWS.ja README.ja
%doc non-free/AVASYSPL.ja.txt

%config(noreplace)	%{_sysconfdir}/sane.d/epkowa.conf

%ifarch %{supported_archs}
%{_bindir}/iscan
%{_libdir}/libesmod.so*
%{_sbindir}/iscan-registry
%endif
%{_libdir}/sane/libsane-epkowa.la
%{_libdir}/sane/libsane-epkowa.so.*
%{_mandir}/man*/*
%{_localstatedir}/lib/%{pkg}
%{_datadir}/applications/%{pkg}.desktop


# 	significant packaging changes

%changelog
* Mon Dec 15 2008  Olaf Meeuwissen <olaf.meeuwissen@avasys.jp>
  - redid the udev rules and FDI file creation using make-policy-file
    script
  - dropped hotplug support, we now assume udev and/or hal are present

* Tue May 23 2006  Olaf Meeuwissen <olaf.meeuwissen@avasys.jp>
  - create udev rules from hotplug usermap using custom utility

* Tue Jan 24 2006  Olaf Meeuwissen <olaf.meeuwissen@avasys.jp>
  - turned the dependency on sane-backend into a PreReq: because our
    %post mucks with its dll.conf
  - disable the backend when uninstalling
  - use sed's -i option to modify dll.conf in place

* Sat Jan 21 2006  Olaf Meeuwissen <iscan@member.fsf.org>
  - removed packaging of interpreter plugins

* Fri Sep 30 2005  Olaf Meeuwissen <olaf.meeuwissen@avasys.jp>
  - package the backend interpreter plugins in their own RPMs
  - added support for build on architectures other than IA32
  - beefed up the BuildRequires:

* Thu Jun 16 2005  Olaf Meeuwissen <olaf.meeuwissen@avasys.jp>
  - use gimptool to find the plugin directory (note that some distro's
    prefer to provide gimptool-2.0 only!)

* Thu May 19 2005  Olaf Meeuwissen <olaf.meeuwissen@avasys.jp>
  - fixed broken dependency specification
  - use release number defined in configure.ac

* Mon Apr 25 2005  Olaf Meeuwissen <olaf.meeuwissen@avasys.jp>
  - modified %doc entries to handle license file name changes
  - updated URL: to reflect corporate name change

* Sun Apr 10 2005  Olaf Meeuwissen <iscan@member.fsf.org>
  - integrated iscan-1.14.0 changes to add hotplug support

* Fri Dec 24 2004  Olaf Meeuwissen <iscan@member.fsf.org>
  - bumped libusb versioned dependency to use the correct version

* Fri Dec  3 2004  Olaf Meeuwissen <olaf@epkowa.co.jp>
  - fixed creation of GIMP plug-in symlinks

* Mon Nov  1 2004  Olaf Meeuwissen <olaf@epkowa.co.jp>
  - fixed libesmod.so* path (it's not in %{_libdir}/%{pkg} yet)
  - added Japanese documentation
  - doubled %s in the spec file parts to un-confuse rpmbuild
  - fixed typo in config file installation command
  - fixed generation of message catalog list

* Fri Oct 29 2004  Olaf Meeuwissen <iscan@member.fsf.org>
  - adapt to Fascist build policy
  - no longer install libsane-epkowa.so as this seems to have become
    the vogue for non-development packages
  - install libsane-epkowa.la so that the dll backend can still find
    the epkowa backend

* Tue Oct 19 2004  Olaf Meeuwissen <iscan@member.fsf.org>
  - initial spec file

# 	end of file
