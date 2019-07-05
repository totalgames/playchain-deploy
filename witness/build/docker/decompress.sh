#!/bin/bash
echo "* Extracting image"

export TMPDIR=`mktemp -d /tmp/selfextract.XXXXXX`

ARCHIVE=`awk '/^__ARCHIVE_BELOW__/ {print NR + 1; exit 0; }' $0`

tail -n+$ARCHIVE $0 | tar xz -C $TMPDIR

CDIR=`pwd`
cd $TMPDIR
./installer.sh $@

cd $CDIR
rm -rf $TMPDIR

exit 0

__ARCHIVE_BELOW__
