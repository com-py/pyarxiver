# pyarxiver
Python Youtube Arxiver - record from any point of live streams

This is a compact, resource-efficient program to download youtube `live` streams from any point of the stream, up to the  limit of past 5 days. The program is inspired by <a href="https://github.com/Kethsar/ytarchive"> ytarchive</a>, but with the option to choose the start time and more resource friendly.

You can run the program with or without a Python installation.

- With Python (any OS):
  - `python pyarxiver.py video-link`
    - download from the present at 720p (default)
  - `python pyarxiver.py video-link 2:30`  
    - download from 2 hours 30 minutes ago at 720p
  - `python pyarxiver.py video-link 1:1:0 1920x1080`
    - download from 1 day and 1 hour ago (25 hours back) at 1920x1080
- Without Python (Windows only):
  
  The program is packaged as binary executable, thanks to <a href="https://github.com/pyinstaller/pyinstaller"> pyinstaller</a>. Download and extract the zip file `pyarxiver-win.zip`, put it in your path, and run it just like above. For example,
  - `pyarxiver video-link 0:30`  
    - download from 30 minutes ago at 720p

The video is downloaded in chunks of `.ts` files to the default directory `fragsdir`. Each file is playable without interrupting download, better yet they can be combined to a single video file with your favorite tool. One such tool is provided here too, `combts-win.zip`. It combines the chunks (fragments) and can be used as follows:
  - `combts fragsdir`
    - combines all files (up to 1440, or 2 hours) in `fragsdir` to `vid-combtsXYZ.ts`, leaving the fragments in place. Here `XYZ` is a sequence 1,2,3 etc. to label the combined videos.
  - `combts fragsdir 1440 delete`
    - combines up to 1440 files (actual files may be fewer) in `fragsdir` and delete the fragments after the video file is produced
    - the option `delete` is preferred as it removes used chunks, so only fresh ones are included the next time you run `combts`. This way one can play the video as it is being downloaded. Of course, the `.ts` files may also be processed with <a href="https://ffmpeg.org/"> FFmpeg</a>, eg, converting it to `mp4` files.

If you use the binary executables, verify the checksums to be sure:
- `pyarxiver-win.zip SHA1: A019FFD57BB4F674D628256707865B83BD0504B6`
- `combts-win.zip SHA1: 7DFD50B1DC6257F60A4E34ADE7785A4AF4EBB6A8`
