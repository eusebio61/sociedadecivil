FROM archlinux:base

RUN pacman-key --init

RUN yes | pacman -Sy python
