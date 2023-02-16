#!/bin/sh
curl -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0' http://www.clamav.net/downloads 2>/dev/null|grep Latest |sed -e 's,.*<h3>,,;s, .*,,'
