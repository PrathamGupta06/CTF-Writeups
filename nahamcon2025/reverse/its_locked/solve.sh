#!/usr/bin/env bash
#
# solve.sh — use machine-ID “hello” to unlock locked.sh
# (fixed echo and base64 flags)

set -euo pipefail
IFS=$'\n\t'

# --- copy these verbatim from your locked script ---
BCV='93iNKe0zcKfgfSwQoHYdJbWGu4Dfnw5ZZ5a3ld5UEqI='
P='llLvO8+J6gmLlp964bcJG3I3mY27I9ACsJTvXYCZv2Q='
S='lRwuwaugBEhK488I'
C='3eOcpOICWx5iy2UuoJS9gQ=='

LOCKED="locked.sh"
OUTDIR="payload"
mkdir -p "$OUTDIR"

# 1) Build the machine-key from your hint + uid
UID_NUM=$(id -u)
MACH_KEY="B-hello-${UID_NUM}"

# 2) Verify BCV decrypts as “TEST-VALUE-VERIFY”
if ! echo -n "$BCV" \
     | openssl enc -d -aes-256-cbc -md sha256 -nosalt \
         -k "$MACH_KEY" -a -A 2>/dev/null \
     | grep -qx 'TEST-VALUE-VERIFY'
then
  echo "[-] Machine-ID layer FAILED." >&2
  exit 1
fi
echo "[+] Machine-ID OK."

# 3) Decrypt the real password _P
PASS="$( echo -n "$P" \
         | openssl enc -d -aes-256-cbc -md sha256 -nosalt \
             -k "$MACH_KEY" -a -A 2>/dev/null )"
if [ -z "$PASS" ]; then
  echo "[-] Could not recover password." >&2
  exit 1
fi
echo "[+] Recovered password: $PASS"

# 4) Decrypt & eval the stub ($C)
STUB="$( echo -n "$C" \
         | openssl enc -d -aes-256-cbc -md sha256 -nosalt \
             -k "C-${S}-${PASS}" -a -A 2>/dev/null )"
echo "[+] Evaluating extraction stub…"
eval "$STUB"

# 5) Locate the payload marker in locked.sh and extract
PAYLOAD_LINE=$(grep -n '^__PAYLOAD__$' -m1 "$LOCKED" | cut -d: -f1)
if [ -z "$PAYLOAD_LINE" ]; then
  echo "[-] Could not find __PAYLOAD__ marker in $LOCKED" >&2
  exit 1
fi

tail -n +"$((PAYLOAD_LINE+1))" "$LOCKED" \
  | perl -pe 's/B3/\n/g; s/B1/\x00/g; s/B2/B/g' \
  | openssl enc -d -aes-256-cbc -md sha256 -nosalt \
      -k "${S}-${PASS}" -a -A \
  | gunzip \
  > "$OUTDIR/extracted_payload"

echo "[+] Payload written to $OUTDIR/extracted_payload"
