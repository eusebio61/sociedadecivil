FROM archlinux:base

RUN pacman-key --init && pacman -Syu --noconfirm systemd systemd-sysvcompat dbus python

CMD ["/sbin/init"]