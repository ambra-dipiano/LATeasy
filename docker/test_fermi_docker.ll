#!/bin/bash

docker run --rm --net=host -v test:/test fermitool:[tag] /bin/bash -c 'ls '
