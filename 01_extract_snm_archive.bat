@echo off
REM Listing 1: Selective extraction of SNM mains files with 7-Zip.
REM Avoids unpacking the full ~45 GB archive; only the per-building
REM site-meter (mains) files needed for this analysis are extracted.

REM List the SNM archive contents without extracting (no disk cost)
"C:\Program Files\7-Zip\7z.exe" l raw.7z > snm_list.txt

REM Extract ONLY the mains (site-meter) file of the selected buildings
"C:\Program Files\7-Zip\7z.exe" x raw.7z -osnm_mains ^
  "raw\building_10\cii-adapter.h5" ^
  "raw\building_11\cii-adapter.h5" ^
  "raw\building_15\cii-adapter.h5" ^
  "raw\building_17\cii-adapter.h5"
