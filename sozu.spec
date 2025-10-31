Name:           sozu
Version:        1.0.6
Release:        1%{?dist}
Summary:        A lightweight, fast, always-up reverse proxy server

License:        AGPL-3.0-or-later
URL:            https://www.sozu.io/
Source0:        https://github.com/sozu-proxy/sozu/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  rust >= 1.80.0
BuildRequires:  cargo
BuildRequires:  gcc
BuildRequires:  openssl-devel
BuildRequires:  protobuf-compiler
BuildRequires:  systemd

Requires:       glibc
Requires:       openssl-libs
Requires(pre):  shadow-utils
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

# Disable debuginfo package generation
# %global debug_package %{nil}

# Don't strip the binary to preserve Rust symbols
# %global __os_install_post %{nil}

%description
Sōzu is a lightweight, fast, always-up reverse proxy server written in Rust.

Key features:
- Hot configurable: Receives configuration changes at runtime through secure unix sockets
- Zero-downtime upgrades: Upgrades itself while still processing requests
- TLS termination: Works as a TLS endpoint for backend servers
- Memory safety: Built with Rust for enhanced security
- High performance: Optimized HTTP parsing and TLS handling with zero-copy operations

%prep
%setup -q -c
mv %{name}-* %{name}-%{version}

%build
cd %{name}-%{version}
export CARGO_HOME=$PWD/.cargo

# Build the main sozu binary
cargo build --release --verbose --bin sozu

%install
cd %{name}-%{version}

# Install main binary
install -D -m 755 target/release/sozu %{buildroot}%{_bindir}/sozu

# Install systemd service files
install -D -m 644 os-build/systemd/sozu.service %{buildroot}%{_unitdir}/sozu.service
install -D -m 644 os-build/systemd/sozu@.service %{buildroot}%{_unitdir}/sozu@.service

# Install configuration files
install -d %{buildroot}%{_sysconfdir}/sozu
install -D -m 644 os-build/config.toml %{buildroot}%{_sysconfdir}/sozu/config.toml

# Create runtime directories
install -d %{buildroot}%{_rundir}/sozu
install -d %{buildroot}%{_sharedstatedir}/sozu

# Install license and documentation
install -d %{buildroot}%{_licensedir}/%{name}
install -m 644 LICENSE %{buildroot}%{_licensedir}/%{name}/LICENSE

install -d %{buildroot}%{_docdir}/%{name}
install -m 644 README.md %{buildroot}%{_docdir}/%{name}/
install -m 644 CHANGELOG.md %{buildroot}%{_docdir}/%{name}/
cp -r doc/ %{buildroot}%{_docdir}/%{name}/

%pre
getent group sozu >/dev/null || groupadd -r sozu
getent passwd sozu >/dev/null || \
    useradd -r -g sozu -d %{_sharedstatedir}/sozu -s /sbin/nologin \
    -c "Sozu reverse proxy" sozu
exit 0

%post
%systemd_post sozu.service

%preun
%systemd_preun sozu.service

%postun
%systemd_postun_with_restart sozu.service

%files
%license %{_licensedir}/%{name}/LICENSE
%doc %{_docdir}/%{name}/README.md
%doc %{_docdir}/%{name}/CHANGELOG.md
%doc %{_docdir}/%{name}/doc/
%{_bindir}/sozu
%{_unitdir}/sozu.service
%{_unitdir}/sozu@.service
%config(noreplace) %{_sysconfdir}/sozu/config.toml
%attr(0755,sozu,sozu) %dir %{_rundir}/sozu
%attr(0755,sozu,sozu) %dir %{_sharedstatedir}/sozu

%changelog
* Wed Dec 25 2024 Eloi DEMOLIS <eloi.demolis@clever-cloud.com> - 1.0.6
- Update to version 1.0.6
