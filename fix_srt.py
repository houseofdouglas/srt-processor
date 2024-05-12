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
        return f'{self.position}\n{self.start} --> {self.end}\n{self.text}'

    def __repr__(self):
        return f'{self.position}\n{self.start} --> {self.end}\n{self.text}'

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
        return self.convert_to_seconds(self.end) - self.convert_to_seconds(self.start)

    def convert_to_seconds(time):
        hours, minutes, seconds = map(int, time.split(':'))
        milliseconds = int(seconds.split(',')[1])
        seconds = int(seconds.split(',')[0])
        total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000
        return total_seconds
    
    

def read_srt_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines


if __name__ == '__main__':
    srt_lines = read_srt_file(FILE)
    captions = []
    for line in srt_lines:
        if re.match(caption_start, line):
            caption_obj = caption(int(line))
        elif re.match(caption_timelime, line):
            start, end = line.split(' --> ')
            caption_obj.set_start(start)
            caption_obj.set_end(end)
        elif line.strip() == '':
            captions.append(caption_obj)
        else:
            caption_obj.set_text(line)

    for idx, caption in enumerate(captions):
        if caption.duration < 1:
            captions[idx-1] = captions[idx-1] + caption
            captions.pop(idx)
