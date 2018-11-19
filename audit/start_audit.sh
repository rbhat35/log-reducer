#!/bin/bash


chown root:root audit.rules
chmod 0600 audit.rules

auditctl -D
auditctl -R audit.rules
auditctl -l
