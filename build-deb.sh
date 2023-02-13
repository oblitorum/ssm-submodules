#!/bin/bash

set -o errexit
set -o xtrace

docker run --rm -v ./:/home/builder/ssm-submodules debian:stretch-slim bash -c "
    set -o errexit
    set -o xtrace
    umask 0000

    echo 'deb http://deb.debian.org/debian bullseye-backports main' > /etc/apt/sources.list.d/bullseye-backports.list
    apt update && apt install -y golang-1.17 && \
        rm /etc/apt/sources.list.d/bullseye-backports.list && \
        apt update && apt install -y git rsync build-essential devscripts
    useradd builder -u 1000 -m -G users,wheel && \
        chmod 755 /home/builder && su - builder
    export GOROOT=/usr/lib/go-1.17 && export GOPATH=/home/builder/go &&
        PATH=/usr/lib/go-1.17/bin:\${GOPATH}/bin:\$PATH
    mkdir -p \${GOPATH}/src/github.com/golang && \
        git clone -b v0.5.4 https://github.com/golang/dep.git \${GOPATH}/src/github.com/golang/dep
    GO111MODULE=off go install -ldflags=\"-X main.version=v0.5.4\" \${GOPATH}/src/github.com/golang/dep/cmd/dep

    pushd /home/builder/ssm-submodules
        build_dir=tmp/debbuild/DEB
        sdeb_dir=/home/builder/ssm-submodules/results/SDEBS
        result_dir=results/DEBS

        rm -rf \${build_dir}
        mkdir -vp \${build_dir} \${result_dir}
        pushd \${build_dir}
            dpkg-source -x \${sdeb_dir}/pmm-client_1.17.5*.dsc
            pushd pmm-client-1.17.5
                dpkg-buildpackage -b -uc
            popd
        popd

        mv \${build_dir}/pmm-client_1.17.5*.deb \${result_dir}
        mv \${build_dir}/pmm-client_1.17.5*.changes \${result_dir}
    popd
"