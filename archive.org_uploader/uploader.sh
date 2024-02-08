#!/usr/bin/env bash

# Uses https://github.com/overcast07/wayback-machine-spn-scripts

# if_not_archived_within=24d,5y means explicit links not captured within 24 days (when I last tried to do this plus the fourteen days I used when I did that), and transitive links not captured with 5 years
# delay_wb_availability=1 means there's no rush and archive.org can take as long as they need
# email_result=1 means email the authenticated user a report at the end
spn.sh -a "${SAVEPAGENOW_ACCESS_KEY}:${SAVEPAGENOW_SECRET_KEY}" -d 'if_not_archived_within=24d,5y&delay_wb_availability=1&email_result=1' -o '' url-list.txt
