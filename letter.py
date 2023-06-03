from file import File


class MailCreator:
    def __init__(self):
        self.boundary = 'qwerty'
        self.letter = ''

    def set_header(self, login_from: str, to: str, subject: str):
        self.letter += f'From: {login_from}\nTo: {to}\nSubject: {subject}'
        self.letter += f'\nContent-Type: multipart/mixed; ' \
                       f'boundary={self.boundary}'

    def set_content(self, file: File, is_last: bool):
        self.letter += f'\n\n--{self.boundary}'
        self.letter += f'\nMime-Version: 1.0'
        self.letter += f'\nContent-Type: image/{file.file_ext}; ' \
                       f'name="=?UTF-8?B?{file.encoded_name}?="'
        self.letter += f'\nContent-Disposition: attachment; ' \
                       f'filename="=?UTF-8?B?{file.encoded_name}?="'
        self.letter += '\nContent-Transfer-Encoding: base64\n\n'
        self.letter += file.get_encoded_file()
        self.letter += f'\n--{self.boundary}'
        if is_last:
            self.letter += '--'

    def get_letter(self):
        return f'{self.letter}\n.\n'
