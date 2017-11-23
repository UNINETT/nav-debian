#!/bin/sh -e
./dev.sh gbp buildpackage --git-ignore-new --git-builder="debuild -i -I -us -uc"

output=$(dirname $(dirname "$PWD"))
cat <<EOF

You should find your packages ready for signing with debsign in the
following directory:
${output}
EOF
