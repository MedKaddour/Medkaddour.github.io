#!/bin/bash

BASE_DIR="_sass"

# Add '@use "sass:string";' at the top if not present
for file in $(find "$BASE_DIR" -type f -name "*.scss"); do
  # Check if file contains str-insert
  if grep -q "str-insert" "$file"; then
    echo "Fixing deprecated functions in $file ..."

    # Add '@use "sass:string";' if not already present
    if ! grep -q '@use "sass:string"' "$file"; then
      sed -i '1i @use "sass:string";' "$file"
    fi

    # Replace str-insert(...) with string.insert(...)
    sed -i 's/str-insert(/string.insert(/g' "$file"
  fi
done
