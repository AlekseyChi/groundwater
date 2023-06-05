# Start from a base Ubuntu image
FROM ubuntu:focal

# Don't prompt during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Update the package list
RUN apt-get update

# Install necessary packages
RUN apt-get install -y perl libnet-ssleay-perl openssl libauthen-pam-perl libpam-runtime libio-pty-perl apt-show-versions python3

# Download the Webmin package
ADD http://prdownloads.sourceforge.net/webadmin/webmin_1.973_all.deb /tmp/webmin.deb

# Install the Webmin package
RUN dpkg -i /tmp/webmin.deb

# Clean up
RUN rm /tmp/webmin.deb

# Webmin's default port
EXPOSE 10000

# Start Webmin
CMD ["/usr/share/webmin/miniserv.pl", "/etc/webmin/miniserv.conf"]
