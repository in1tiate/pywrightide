from PyQt6.QtCore import QRect

from PyQt6.QtGui import QImage

from dataclasses import dataclass, field
from pathlib import Path
from math import ceil


class SpriteSheet:
    def __init__(self, image_path: Path):
        self._image_path = image_path

        animation_data_path = self._image_path.with_suffix(".txt")

        if animation_data_path.exists() and animation_data_path.is_file():
            self._animation_data = AnimationData.read_from_file(animation_data_path)
        else:
            self._animation_data = AnimationData()

        self._sheet_image = QImage(str(self._image_path))

        self._frame_width = ceil(self._sheet_image.width() / self._animation_data.horizontal_splits)
        self._frame_height = ceil(self._sheet_image.height() / self._animation_data.vertical_splits)

        self._create_position_rectangles()

    def get_frame(self, frame_number: int) -> QImage:
        if frame_number < 0 or frame_number >= self._animation_data.num_images:
            raise IndexError("Frame index out of range (Max.: {}, asked for {})".format(self._animation_data.num_images - 1, frame_number))

        return self._sheet_image.copy(self._position_rectangles[frame_number])

    @property
    def num_frames(self):
        return self._animation_data.num_images

    def get_framedelay_for_frame(self, frame_number: int) -> int:
        if frame_number < 0 or frame_number >= self._animation_data.num_images:
            raise IndexError("Frame index out of range (Max.: {}, asked for {})".format(self._animation_data.num_images - 1, frame_number))

        # If not specified, default delay is 6 ticks
        return self._animation_data.frame_delays.get(frame_number, 6)

    def get_sfx_path_for_frame(self, frame_number: int) -> str:
        if frame_number < 0 or frame_number >= self._animation_data.num_images:
            raise IndexError("Frame index out of range (Max.: {}, asked for {})".format(self._animation_data.num_images - 1, frame_number))

        # If not specified, default delay is 6 ticks
        return self._animation_data.sound_effects_at_frames.get(frame_number, "")

    @property
    def blink_mode(self) -> str:
        return self._animation_data.blink_mode

    @property
    def blip_sound_path(self) -> str:
        return self._animation_data.blip_sound_path

    def _create_position_rectangles(self):
        self._position_rectangles : list[QRect] = []
        frame_num = 0

        for y in range(self._animation_data.vertical_splits):
            if frame_num >= self._animation_data.num_images:
                break

            for x in range(self._animation_data.horizontal_splits):
                if frame_num >= self._animation_data.num_images:
                    break
                xpos = x * self._frame_width
                ypos = y * self._frame_height
                self._position_rectangles.append(QRect(xpos, ypos, self._frame_width, self._frame_height))
                frame_num += 1


@dataclass
class AnimationData:
    horizontal_splits : int = 1
    vertical_splits : int = 1
    num_images : int = 1
    num_loops : int = 0
    frame_delays : dict[int, int] = field(default_factory = lambda: dict())
    sound_effects_at_frames : dict[int, str] = field(default_factory = lambda: dict())
    blink_mode : str = ""
    blip_sound_path : str = ""

    @staticmethod
    def read_from_file(filepath : Path) :
        result = AnimationData()

        with open(filepath, 'r') as f:
            lines = f.readlines()

            for line in lines:
                if line.startswith("horizontal"):
                    line_splits = line.split()
                    if len(line_splits) != 2:
                        print("horizontal property is formatted wrong")
                        continue

                    result.horizontal_splits = int(line_splits[1])
                elif line.startswith("vertical"):
                    line_splits = line.split()
                    if len(line_splits) != 2:
                        print("vertical property is formatted wrong")
                        continue

                    result.vertical_splits = int(line_splits[1])
                elif line.startswith("length"):
                    line_splits = line.split()
                    if len(line_splits) != 2:
                        print("length property is formatted wrong")
                        continue

                    result.num_images = int(line_splits[1])
                elif line.startswith("loops"):
                    line_splits = line.split()
                    if len(line_splits) != 2:
                        print("loops property is formatted wrong")
                        continue

                    result.num_loops = int(line_splits[1])
                elif line.startswith("framedelay"):
                    line_splits = line.split()
                    if len(line_splits) != 3:
                        print("framedelay property is formatted wrong: " + line)
                        continue

                    result.frame_delays[int(line_splits[1])] = int(line_splits[2])
                elif line.startswith("sfx"):
                    line_splits = line.split()
                    if len(line_splits) != 3:
                        print("sfx property is formatted wrong: " + line)
                        continue

                    result.sound_effects_at_frames[int(line_splits[1])] = line_splits[2]
                elif line.startswith("blinkmode"):
                    line_splits = line.split()
                    if len(line_splits) != 2:
                        print("blinkmode property is formatted wrong")
                        continue

                    if line_splits[1] != "blink" and line_splits[1] != "loop" and line_splits[1] != "stop":
                        print("Unknown blink mode: {}".format(line_splits[1]))

                    result.blink_mode = line_splits[1]
                elif line.startswith("blipsound"):
                    line_splits = line.split()
                    if len(line_splits) != 2:
                        print("blipsound property is formatted wrong")
                        continue

                    result.blip_sound_path = line_splits[1]
                elif line.strip() != "":
                    print("Unknown property found: " + line)

            return result

    def write_to_file(self, filepath: Path):
        file_text = """horizontal {}\n
                    vertical {}\n
                    length {}\n
                    loops {}\n
                    """.format(self.horizontal_splits, self.vertical_splits, self.num_images, self.num_loops)

        with open(filepath, 'w') as f:
            f.write(file_text)
            if self.blink_mode != "":
                f.write("blink {}\n".format(self.blink_mode))

            if self.blip_sound_path != "":
                f.write("blipsound {}\n".format(self.blip_sound_path))

            if len(self.frame_delays) > 0:
                for frame_num in self.frame_delays.keys():
                    f.write("framedelay {} {}\n".format(frame_num, self.frame_delays[frame_num]))

            if len(self.sound_effects_at_frames) > 0:
                for frame_num in self.frame_delays.keys():
                    f.write("sfx {} {}\n".format(frame_num, self.sound_effects_at_frames[frame_num]))
