import re

FILE='Kris-with-sound-analyzed.srt'

caption_start = re.compile(r'^\d{1,4}\n')
caption_timelime = re.compile(r'^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n')

class PositionExistedError(Exception):
    pass

class caption:
    def __init__(self, position=0, start=None, end=None, text=None):
        self.position = position
        self.start = start
        self.end = end
        self.text = text

    def __str__(self):
        return f'{self.position}\n{self.start} --> {self.end}\n{self.text}\n'

    def __repr__(self):
        return f'{self.position}\n{self.start} --> {self.end}\n{self.text}\n'

    def __add__(self, other):
        return caption(self.position, self.start, other.end, f'{self.text} {other.text}')

    def set_position(self, position):
        if not isinstance(position, int):
            raise ValueError('Position must be an integer')
        if position < 0:
            raise ValueError('Position must be greater than 0')
        if self.position:
            raise PositionExistedError('Position must be greater than the current position')
        self.position = position
    
    def set_start(self, start):
        self.start = start

    def set_end(self, end):
        self.end = end

    def set_text(self, text):
        self.text = text
    
    @property
    def duration(self):
        def convert_to_seconds(time):
            hours, minutes, seconds = time.split(':')
            milliseconds = int(seconds.split(',')[1])
            seconds = int(seconds.split(',')[0])
            total_seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000
            return total_seconds
        
        return convert_to_seconds(self.end) - convert_to_seconds(self.start)
    
    

def read_srt_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines


if __name__ == '__main__':
    srt_lines = read_srt_file(FILE)
    captions = []
    caption_obj = None
    for line in srt_lines:
        if re.match(caption_start, line):
            if caption_obj is not None:
                captions.append(caption_obj)
            caption_obj = caption(int(line))
        elif re.match(caption_timelime, line):
            start, end = line.split(' --> ')
            caption_obj.set_start(start.strip())
            caption_obj.set_end(end.strip())
        elif line.strip() == '':
            pass
        else:
            caption_obj.set_text(line.strip())

    if caption_obj is not None:
        captions.append(caption_obj)

    indices_to_remove = []
    for idx, entry in enumerate(captions):
        if entry.duration < 1 and captions[idx-1].duration < 2:
            captions[idx-1] = captions[idx-1] + entry
            indices_to_remove.append(idx)
            continue
        if entry.duration < 1 and captions[idx-1].duration > 2 and idx+1 <= len(captions)-1 and captions[idx+1].duration > 2:
            captions[idx-1] = captions[idx-1] + entry
            indices_to_remove.append(idx) 
        
    for idx in reversed(indices_to_remove):
        captions.pop(idx)

    with open('new.srt', 'w') as srt:
        for idx, entry in enumerate(captions):
            srt.write(f'{idx+1}\n{entry.start} --> {entry.end}\n{entry.text}\n\n')
