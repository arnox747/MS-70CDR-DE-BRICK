
#!/usr/bin/env python3
"""
Build a 4 MiB flash image for the Zoom MS-70CDR
Macronix MX25L3233F SPI flash chip, suitable for a CH341A programmer.

Input files must be in the same directory as this script.
Unused bytes are filled with 0xFF.
"""

from pathlib import Path
import hashlib
import sys

SCRIPT_DIR = Path(__file__).resolve().parent

FLASH_SIZE = 0x400000  # 4 MiB = 4,194,304 bytes

# Absolute flash offsets
FIRMWARE = [
    ("boot.bin",   0x000000),
    ("Main.bin",   0x040000),
    ("FS.bin",     0x0F0000),
    ("Preset.bin", 0x3FD000),
]

OUTPUT_FILE = SCRIPT_DIR / "MS70CDR_FIRMWARE_FULL_4MB.bin"


def main():
    # Read and validate all inputs before building the image.
    image = bytearray(b"\xFF") * FLASH_SIZE

    for index, (filename, offset) in enumerate(FIRMWARE):
        path = SCRIPT_DIR / filename

        if not path.is_file():
            sys.exit(f"ERROR: Missing component file: {filename}")

        data = path.read_bytes()

        if not data:
            sys.exit(f"ERROR: Component file is empty: {filename}")

        # The next file's offset defines this file's maximum region.
        if index + 1 < len(FIRMWARE):
            region_end = FIRMWARE[index + 1][1]
        else:
            region_end = FLASH_SIZE

        max_size = region_end - offset

        if len(data) > max_size:
            sys.exit(
                f"ERROR: {filename} is too large.\n"
                f"  Start offset: 0x{offset:06X}\n"
                f"  Maximum size: {max_size:,} bytes "
                f"(0x{max_size:X})\n"
                f"  Actual size:  {len(data):,} bytes"
            )

        end = offset + len(data)
        image[offset:end] = data

        print(
            f"{filename}: {len(data):,} bytes "
            f"at 0x{offset:06X}–0x{end - 1:06X}"
        )

    # Write the complete 4 MiB image.
    try:
        OUTPUT_FILE.write_bytes(image)
    except OSError as exc:
        sys.exit(f"ERROR writing output file: {exc}")

    # Verify output size and report checksum.
    if OUTPUT_FILE.stat().st_size != FLASH_SIZE:
        sys.exit("ERROR: Output image size verification failed.")

    digest = hashlib.sha256(image).hexdigest()

    print("\nFlash image created successfully.")
    print(f"Output:  {OUTPUT_FILE}")
    print(f"Size:    {FLASH_SIZE:,} bytes (4 MiB)")
    print(f"SHA-256: {digest}")
    print("Unused space: filled with 0xFF")


if __name__ == "__main__":
    main()
