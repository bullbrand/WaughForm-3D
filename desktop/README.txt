WaughForm 3D  -  from idea to object
Version 1.9.4
© 2026 David John Waugh. Free software under the GNU GPL v3 or later
(see LICENSE.txt). It comes with no warranty.

Draw your own 3D parts, or let WaughForm 3D design a printable box
(an "enclosure") around your electronics. Everything runs on your own
computer. No internet connection is needed, except for one optional
extra: looking up a part's sizes online (see "FILL IN AUTOMATICALLY"
below).


=====================================================================
 GETTING STARTED
=====================================================================

You will have one of these two files. Either one is the whole program:

  WaughForm 3D Portable 1.9.4.exe
      Just double-click it. Nothing is installed. It also works from
      a USB stick.

  WaughForm 3D Setup 1.9.4.exe
      Installs the program with a Start menu and desktop shortcut.
      Uninstall it any time from Settings > Apps.

It needs Windows 10 or 11 (64-bit).

"Windows protected your PC"?
  The first time you run it, Windows may show this blue box because the
  program isn't "signed" by a big company. Click "More info", then
  "Run anyway". You only need to do this once.

First thing to do:
  Click the "Printer" button at the top and choose your printer, or
  type its build size (X, Y and Z in mm). The app then warns you if
  anything is too big to print.

Press F1 (or click Help) at any time for a list of tools and shortcuts.
Click "About" (top right) to see which version you have; it is also in
the bottom-right corner of the 3D view.
Hover over any button to see its name, its shortcut key and what it does.
Also new: the Tape Measure leaves a guide point to draw to (type a
distance for an exact one; Shift+E deletes all guides), Shift+click with
Round rounds every edge of a box, and lines now snap to the red, green
and blue directions, so drawing straight up or in mid-air is easy.
Shortcut keys now match SketchUp: Offset is F (Round / Chamfer moved
to J) and Ctrl+T selects nothing. A quick right-click on the model
opens a menu of common jobs; right-click and drag still turns the view.
New shapes: Polygon (N) for hexagons, triangles and more, and 3D Shapes
(D) for a ball, cone, cylinder or pyramid in one go.
Slice (X) cuts a solid in two with a flat plane, so you can move or
delete either half (handy for printing a tall part in two pieces).
Check Model now fails any piece left floating in mid-air, with a
"Move down to rest" button to drop it onto what is below.
Copy, Cut and Paste for shapes: Ctrl+C, Ctrl+X, Ctrl+V (also on the
toolbar and the right-click menu). Drag toolbar buttons, or a group by
its dotted grip, to put them in your own order; right-click the toolbar
to reset it.
NEW: ESPHome device file. In the Wiring window, the "ESPHome device"
tab writes the whole ESPHome YAML for your ESP32 board with the pins
from the wiring: choose Sensor node or Voice assistant, answer a few
questions, then Copy YAML or Save .yaml. "Check with ESPHome" checks it
with the ESPHome on your computer. "Send to ESPHome" puts the device
straight into ESPHome Device Builder on your computer and opens it: plug
the board in and click Install. Wi-Fi comes from ESPHome Secrets.
To make it do something: a "Light rule" (e.g. red above 28 C, green
otherwise), or describe it in "What should it do?" and click "Make it
with AI": your AI key adds it, ESPHome checks it, and any mistake goes
back to the AI to fix. DHT11/DHT22 and DS18B20 sensors are now known.
Parts it doesn't know (e.g. imported from a .fzpz file) need nothing
from you: "Make it with AI" writes their code from the part's name,
part-file description and pins (the part file's details are now kept
when you import it).
NEW: a parts library comes with the program. "Browse parts..." in Parts
(and in the Enclosure Wizard) lists over 2,000 ready-made parts. Search
by part number or by what it does, e.g. "gyroscope", "air quality" or
"screen", or pick a kind to scroll through; "Add to my box" adds it to
your enclosure in one click. "Import pins..." uses the same parts (sensors, boards, modules, displays)
with their pins, sizes and pictures, so Fritzing isn't needed. They come
from the Fritzing parts library, (c) Fritzing contributors, CC BY-SA 3.0.
New: the Round / Chamfer tool (J) rounds off or bevels the line where
two faces meet. Type 3 then Enter for a 3 mm rounding, or 3c for a
3 mm straight chamfer.
Also new: Arc (A), Offset (F) for a copy of a face's outline inside or
outside it, and Follow Me (W) to sweep a shape along a path. F1 shows
how each one works.
For a full illustrated guide, open "WaughForm 3D User Manual.pdf".


=====================================================================
 MAKING A BOX FOR YOUR ELECTRONICS
=====================================================================

WHAT IT DOES
  You tell WaughForm 3D which electronic bits you want to put in a box,
  such as a circuit board, a speaker or a battery. It designs a
  3D-printable box that fits them, with the right holes in the right
  places. You print the box, drop the parts in and close the lid.


---------------------------------------------------------------------
 STEP 1  -  Teach it your part
---------------------------------------------------------------------

The app needs to know two things about each part: HOW BIG it is, and
WHERE ITS IMPORTANT BITS ARE (the USB socket, the screw holes, a
microphone hole...). It already knows some common parts. For a new
one, you show it a photo.

  1. Measure the part with a ruler or calipers: its length, width and
     height, in millimetres.

  2. Take a photo looking straight down on it, like looking at it
     lying on a table. A plain background helps.

  3. Click "Parts" at the top, then "+ New part". Give it a name and
     type in the measurements.

  4. Click "Top photo..." and choose your picture.

  5. Click the four corners of the board, going round like a clock:
     top-left, top-right, bottom-right, bottom-left.
     If a corner is rounded, click where it WOULD be if it were square.
     The app straightens the photo and works out its scale, so it now
     knows exactly where everything on the board is.
     If the photo was taken the other way round (tall instead of wide),
     the app turns it to match. If it comes out upside down, click
     "Turn photo 180°".

  6. Mark the important bits. Click a button above the picture, then
     click on the photo:

       Port / socket .... A USB or power socket on the edge. The box
                          gets a hole there so you can plug a cable in.
       Mounting hole .... The box gets a little post with a screw hole.
       Mic sound hole ... The box gets a small hole so the microphone
                          can hear outside.
       Speaker cone ..... The box gets slots (a grille) so the sound
                          can get out.
       Round opening .... A round hole the part shows through, e.g. the
                          two "eyes" of an ultrasonic distance sensor,
                          an IR sensor or a camera lens. Set the part to
                          "Face against a wall" and it looks out through
                          the wall, held on standoffs. These have 45°
                          braces underneath, so they print without
                          supports.
       Button, LED,
       Display window ... The lid gets a hole so you can press it or
                          see it.
       Antenna .......... Other parts are kept away from it, so the
                          Wi-Fi works well.

     Drag a mark to move it. Click the red X next to it in the list to
     remove it.

  7. Click "Save part". It is now in your library, ready to use any time.

  Optional: "Side photo for heights..." measures how tall the part is
  from a photo taken from the side. Follow the instructions in the
  yellow bar above the picture.


---------------------------------------------------------------------
 FILL IN AUTOMATICALLY  (optional, uses the internet)
---------------------------------------------------------------------

Instead of measuring, WaughForm 3D can look a part up for you using an
AI. You'll find these buttons in the blue "Fill in automatically" box
at the top of the part's details in "Parts". Choose the AI there:

  Google Gemini (free):
    1. Click "Set up free AI key...", then OK with the box empty.
       Google AI Studio opens in your web browser.
    2. Sign in with a Google account and click "Create API key".
    3. Copy the key, click "Set up free AI key..." again and paste it.
    Free for everyday use, but it is sometimes busy and Google may
    change its free limits.

  Claude (paid, usually more reliable):
    1. Choose "Claude" in the AI box, click "Set up Claude key...", then
       OK with the box empty. The Anthropic Console opens
       (https://console.anthropic.com).
    2. Sign up or sign in, and add some credit under Billing.
    3. Go to Settings > API Keys, click "Create Key" and copy it.
    4. Click "Set up Claude key..." again and paste it.
    Each look-up uses a little of your credit (roughly US$0.10-0.40 for a
    web look-up, a few cents to read a drawing - an estimate).

  Keys are kept on this computer only and are never shared with parts
  you export.

  Look up online (the easy way):
    1. Click "+ New part", then "Look up online...".
    2. Type the exact part number, e.g. "MAX98357A breakout".
    3. The AI searches the web, opens the datasheet or product page and,
       within about a minute, fills in the sizes, holes and sockets as
       a DRAFT (pins come from "Import pins...", see WIRING below). The yellow bar lists anything it wasn't sure of
       and links to the pages it used.
    4. Product photos: if it found photos of the board, they appear as
       small pictures under the yellow bar. Click the best one (a straight
       view from above), then click the board's 4 corners in it, just like
       with your own photo. The photo then sits under the part's holes and
       sockets, so you can see at a glance whether they line up.
    5. Dimension drawings: the app also looks for dimension drawings
       (pictures of the board with measurements) on those pages, and for
       a datasheet PDF. If it finds one, the AI reads it automatically and
       its exact hole and socket positions replace the look-up's guesses,
       as long as the drawing's overall size matches. The drawing is
       shown in the top-right corner so you can check it.
       If the web search finds nothing, it asks the AI what it already
       knows about the part, and says so clearly. Measure those ones.
       If it can't fill anything in, click "Show AI reply" and take a
       screenshot: it shows exactly what the AI sent back.

  Read a drawing (when the look-up can't find it):
    1. Click "Search images myself..." (Google Images) or "Search the web
       myself..." to look for a dimension drawing (a picture with arrows
       and measurements). Both search for "<part> technical documentation
       schematic sizes", which finds the maker's drawings well. Save the
       drawing as a picture or PDF, or just copy it.
    2. Click "Read a drawing...", drag the file onto the part picture,
       or press Ctrl+V. The drawing is shown in the corner (click it to
       make it bigger) beside the draft.

  Either way: CHECK every number against the sources or the drawing,
  and your calipers if you can. Fix anything wrong, then "Save part".

  Good to know:
    - AI can misread drawings. Never print a box without checking.
    - Cheap modules often come in several versions with different hole
      positions. Make sure the drawing matches YOUR board.
    - Only the part number, or the drawing and the part's name and type,
      are sent to the AI you chose. On Google's free plan Google may use
      them to improve its products.
    - Without a key, everything else still works as normal.


---------------------------------------------------------------------
 STEP 2  -  Design the box
---------------------------------------------------------------------

  1. Click "Enclosure" at the top.

  2. Choose your parts from the list and click "Add".
     To take a part out again, click the red X on its row.

  3. Choose power:
       USB cable only, or
       Battery inside (the battery, a charging board and an on/off
       switch are added for you).

  4. Choose a style:
       Compact ..... The smallest neat box, for wires soldered in place.
       Prototype ... Extra room for push-on jumper wires while you're
                     still experimenting.
       Rugged ...... Thick walls, a screw-down lid and tabs for screwing
                     the box to something.

  5. Choose a lid: push-on, click-on (snap) or screwed.

  The app works out the SMALLEST box that fits everything, following
  common-sense rules:
    - sockets go against a wall, so the hole lines up
    - the microphone faces out, kept away from the speaker
    - the battery sits next to its charger
    - nothing touches anything else

  You see a view from above. If you don't like where something went,
  DRAG it somewhere else ("Rotate part" turns it). The list underneath
  shows a green tick for things that are fine and a warning for
  anything that isn't. "Auto arrange" puts everything back.


---------------------------------------------------------------------
 STEP 3  -  Make it
---------------------------------------------------------------------

  1. Click "Generate base + lid". In about a second you get the box and
     its lid. The lid is turned over, ready to print. Faint outlines
     show where each part will sit inside (they are never printed).

  2. The app checks the design. You want to see "Ready to print".

  3. Click "Export 3MF" (or "Export STL"), open the file in your slicer
     (Cura, PrusaSlicer, Bambu Studio, OrcaSlicer...) and print it.
     The base and the lid come out as separate pieces, so you can
     print them one at a time.

  Tip: print the lid first, to check it fits snugly before printing
  the whole box.


IN ONE SENTENCE
  Measure it, photograph it, click the corners and the sockets, pick
  your parts, and the app designs and checks a printable box for you.


=====================================================================
 WIRING: WHAT WIRE GOES WHERE
=====================================================================

  Click "Wiring" at the top (or "Wiring..." in the Enclosure Wizard).
  For the parts in your box it works out:

    - which controller pin each part's signals go to. On the ESP32-S3
      it never uses the pins that would stop it working (start-up,
      USB, serial, PSRAM and LED pins).
    - the power: USB only, or battery -> charger -> switch -> the rest,
      with every ground joined.
    - warnings for anything risky, e.g. a 5 V signal into a 3.3 V pin
      (it tells you which resistors to add), or a speaker wire to GND.

  You get:
    - a diagram: each board with its pins and coloured wires (red 5 V,
      orange battery, pink 3.3 V, black GND). Drag boards to tidy it.
      Hover a wire in the list to find it in the picture.
    - a wiring list to tick off as you solder ("Save wiring list"
      saves it as a text file to print).
    - the matching pin settings for ESPHome and Arduino ("Code pins").

  Every part needs its pins. The built-in parts have them. For your
  own parts, open "Parts" and either add pins by hand at the bottom of
  the part's details, or click "Import pins...". If a parts library is
  installed on this computer it lists all its parts to search, and it
  takes the pin names, their positions and the picture. You can also
  choose a .fzpz part file (a common format for electronics parts,
  free to download for many modules). Check each pin's role, and
  measure the board: these pictures keep the pin spacing exact but are
  sometimes drawn smaller than the real board.

  To find a part file, click "Search for a part file (.fzpz)..." in the
  blue "Fill in automatically" box: it searches the web for your
  board's name plus "fzpz". Someone may already have made one, with
  all the pins, the size and a picture. Download it and drag it onto
  the part picture (or use "Import pins..." > "Use a .fzpz file..."). A board drawn standing up is turned so its
  long side runs left to right. "Turn part 90°" (under the sizes in
  Parts) turns any part a quarter turn, with its picture, features and
  pins.

  ALWAYS check each connection against the labels printed on your
  boards before you power up.


=====================================================================
 COPY AND PASTE
=====================================================================

  Right-click in any box you can type in for Cut, Copy, Paste and
  Select All (Ctrl+X, Ctrl+C, Ctrl+V and Ctrl+A work too).


=====================================================================
 SHARING
=====================================================================

  Your drawings
    "Save" makes a .3mf file. Any slicer can print it, and it opens
    again in WaughForm 3D fully editable. Send it to anyone.

  Your parts
    Parts you add are saved on your own computer only. To give them to
    someone else: open "Parts", click "Export...", and send them the
    .json file. They click "Import..." in their copy.
    If your parts have photos, you can export with or without them.
    Photos downloaded from websites belong to whoever took them, so
    choose "Export without photos" when sharing with other people.

  Your work is also saved automatically as you go, and comes back the
  next time you open the program.


=====================================================================
 CREDITS
=====================================================================

  WaughForm 3D was created by David John Waugh.
  © 2026 David John Waugh.

  WaughForm 3D is free software: you can share it and change it under
  the terms of the GNU General Public License, version 3 or (at your
  option) any later version, published by the Free Software Foundation.
  It comes WITHOUT ANY WARRANTY. The full licence is in LICENSE.txt.
  Source code, downloads and bug reports:
  https://github.com/bullbrand/WaughForm-3D

  The enclosure designer uses the Manifold geometry library
  (© The Manifold Authors, Apache License 2.0), built into the program.
  The optional Claude look-up uses the Anthropic TypeScript SDK
  (© Anthropic, Apache License 2.0), also built in.
  The parts library that comes with WaughForm 3D (over 2,000 parts with
  their pins and pictures) is made from the Fritzing parts library,
  © Fritzing contributors, licensed under CC BY-SA 3.0
  (https://creativecommons.org/licenses/by-sa/3.0/). Parts made from it,
  or brought in with "Import pins...", keep that credit in their notes,
  and anyone sharing them must keep the credit and the same licence.
