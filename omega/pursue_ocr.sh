#!/bin/bash
# OCR the PURSUE Release_07/08 documents that archive.org never generated text
# derivatives for -- the AAWSAP/Senator Reid papers, the BAASS Ten Month Report,
# and the 1952 CIA psychological-warfare assessments.  These are the least
# machine-readable and most historically loaded part of the corpus.
set -u
UA='omega-research/1.0 (academic UAP data study; non-commercial)'
D=/home/user/UFOAI/data/raw/pursue_ocr
mkdir -p "$D/pdf" "$D/txt" "$D/pages"
n=0; tot=$(wc -l < "$D/targets.tsv")
while IFS=$'\t' read -r url name; do
  n=$((n+1))
  pdf="$D/pdf/$name"
  [ -s "$pdf" ] || curl -sS -A "$UA" -L --max-time 300 -o "$pdf" "$url"
  [ -s "$pdf" ] || { echo "[$n/$tot] FETCH FAIL $name"; continue; }
  out="$D/txt/${name%.pdf}.txt"
  if [ -s "$out" ]; then echo "[$n/$tot] cached $name"; continue; fi
  # try the embedded text layer first; OCR only if it yields almost nothing
  pdftotext -layout "$pdf" "$out" 2>/dev/null
  chars=$(wc -c < "$out" 2>/dev/null || echo 0)
  if [ "$chars" -lt 400 ]; then
    rm -rf "$D/pages/$name"; mkdir -p "$D/pages/$name"
    pdftoppm -r 300 -gray -png "$pdf" "$D/pages/$name/p" 2>/dev/null
    : > "$out"
    for img in "$D/pages/$name"/p*.png; do
      [ -e "$img" ] || continue
      tesseract "$img" stdout -l eng --psm 1 2>/dev/null >> "$out"
      printf '\n\f\n' >> "$out"
    done
    rm -rf "$D/pages/$name"
    echo "[$n/$tot] OCR  $(wc -c < "$out") chars  $name"
  else
    echo "[$n/$tot] text $chars chars  $name"
  fi
done < "$D/targets.tsv"
echo "DONE: $(ls "$D/txt" | wc -l) text files, $(du -sh "$D/txt" | cut -f1)"
