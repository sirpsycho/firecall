#!/bin/bash

### This script installs aliases for blockip and removeip


SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Make sure the script files exist (in the same directory as this script)
if [ ! -f $SCRIPTDIR/blockip.py ] || [ ! -f $SCRIPTDIR/removeip.py ] || [ ! -f $SCRIPTDIR/config ]; then
	echo "Error - could not find all necessary files in $SCRIPTDIR"
	exit
fi

# Find user profile file path
if [ -e $HOME/.bash_profile ]; then
	PROFILELOC="${HOME}/.bash_profile"
elif [ -e $HOME/.bashrc ]; then
	PROFILELOC="$HOME/.bashrc"
else
	echo "Error - Could not find user profile to add aliases"
	exit
fi

# remove any old aliases
while read -r line; do
	[[ ! $line =~ "alias blockip"* ]] && [[ ! $line =~ "alias removeip"* ]] && echo "$line"
done <$PROFILELOC > $PROFILELOC.temp
mv $PROFILELOC.temp $PROFILELOC

# create new aliases
echo 'alias blockip="python '$SCRIPTDIR'/blockip.py"' >> $PROFILELOC
echo "[-] Created alias in '$PROFILELOC' for blockip"
echo 'alias removeip="python '$SCRIPTDIR'/removeip.py"' >> $PROFILELOC
echo "[-] Created alias in '$PROFILELOC' for removeip"

# apply the new aliases
. $PROFILELOC

# set log file
while read -r line; do
	if [[ $line =~ "LOG_FILE="* ]]; then
		echo 'LOG_FILE="'$SCRIPTDIR'/firecall.log"'
	else
		echo "$line"
	fi
done <$SCRIPTDIR/config > $SCRIPTDIR/config.temp
mv $SCRIPTDIR/config.temp $SCRIPTDIR/config
echo "[-] Set log file to '$SCRIPTDIR/firecall.log'"

echo "[-] Done."
