#!/bin/sh
# Print the latest ClamAV release version (stdout only — used by automation).
#
#   ./check-update.sh           print latest version
#   ./check-update.sh --cvd     also refresh main.cvd / daily.cvd / bytecode.cvd
#
# ClamAV's CDN (Cloudflare) blocks wget/curl and only allows FreshClam or
# Cisco's official cvdupdate tool:
#   https://github.com/Cisco-Talos/cvdupdate
#   https://docs.clamav.net/faq/faq-freshclam.html
#
# After --cvd, drop the old *.cvd lines from .abf.yml (abb store refuses
# to replace an existing source), then:
#   abb store main.cvd && abb store daily.cvd && abb store bytecode.cvd

set -eu

dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

latest_version() {
	# downloads page: <h3><strong>1.5.4</strong> <span class="badge">Latest</span></h3>
	ver=$(
		curl -fsSL -A 'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0' \
			https://www.clamav.net/downloads 2>/dev/null |
		sed -n 's/.*<h3><strong>\([0-9][0-9.]*\)<\/strong> *<span class="badge">Latest<\/span>.*/\1/p' |
		head -n1
	)
	if [ -z "$ver" ]; then
		ver=$(
			curl -fsSL https://api.github.com/repos/Cisco-Talos/clamav/releases/latest 2>/dev/null |
			sed -n 's/.*"tag_name": "clamav-\([0-9.]*\)".*/\1/p' |
			head -n1
		)
	fi
	if [ -z "$ver" ]; then
		echo "check-update.sh: failed to determine latest ClamAV version" >&2
		return 1
	fi
	printf '%s\n' "$ver"
}

ensure_cvdupdate() {
	if command -v cvd >/dev/null 2>&1; then
		return 0
	fi
	# pip --user installs into ~/.local/bin
	if [ -x "$HOME/.local/bin/cvd" ]; then
		PATH="$HOME/.local/bin:$PATH"
		export PATH
		return 0
	fi
	echo "Installing Cisco cvdupdate (official CVD downloader)..." >&2
	python -m pip install --user cvdupdate >&2
	PATH="$HOME/.local/bin:$PATH"
	export PATH
	command -v cvd >/dev/null 2>&1
}

download_cvds() {
	ensure_cvdupdate || {
		echo "check-update.sh: cvdupdate is not available" >&2
		return 1
	}

	# Persist state so later runs only fetch when Cisco publishes a newer CVD.
	# Keep it out of the package tree and out of a user's private-mirror config.
	cache="${XDG_CACHE_HOME:-$HOME/.cache}/clamav-abf"
	mkdir -p "$cache/db"

	cvd config set -c "$cache/config.json" -d "$cache/db"
	cvd update -c "$cache/config.json"

	missing=
	for f in main.cvd daily.cvd bytecode.cvd; do
		if [ ! -s "$cache/db/$f" ]; then
			echo "check-update.sh: missing $f after cvd update" >&2
			missing=1
			continue
		fi
		# CVD files start with "ClamAV-VDB:"
		if ! head -c 12 "$cache/db/$f" | grep -q '^ClamAV-VDB:'; then
			echo "check-update.sh: $f does not look like a ClamAV CVD" >&2
			missing=1
			continue
		fi
		/bin/cp -f "$cache/db/$f" "$dir/$f"
		file "$dir/$f" >&2
	done
	if [ -n "$missing" ]; then
		return 1
	fi
	echo "Updated $dir/{main,daily,bytecode}.cvd" >&2
	echo "Next: remove the old *.cvd lines from .abf.yml, then:" >&2
	echo "  abb store main.cvd && abb store daily.cvd && abb store bytecode.cvd" >&2
}

case "${1:-}" in
--cvd|--download-cvd)
	latest_version
	download_cvds
	;;
-h|--help)
	sed -n '2,14p' "$0" | sed 's/^# \?//'
	;;
"")
	latest_version
	;;
*)
	echo "Usage: $0 [--cvd]" >&2
	exit 2
	;;
esac
