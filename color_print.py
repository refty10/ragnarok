class ColorPrint:
    color_black = '\u001b[30m'
    color_red = '\u001b[31m'
    color_green = '\u001b[32m'
    color_yellow = '\u001b[33m'
    color_blue = '\u001b[34m'
    color_magenta = '\u001b[35m'
    color_cyan = '\u001b[36m'
    color_white = '\u001b[37m'
    color_reset = '\u001b[0m'

    @classmethod
    def black(self, message, end="\n"):
        print(self.color_black + message + self.color_reset, end=end)

    @classmethod
    def red(self, message, end="\n"):
        print(self.color_red + message + self.color_reset, end=end)

    @classmethod
    def green(self, message, end="\n"):
        print(self.color_green + message + self.color_reset, end=end)

    @classmethod
    def yellow(self, message, end="\n"):
        print(self.color_yellow + message + self.color_reset, end=end)

    @classmethod
    def blue(self, message, end="\n"):
        print(self.color_blue + message + self.color_reset, end=end)

    @classmethod
    def magenta(self, message, end="\n"):
        print(self.color_magenta + message + self.color_reset, end=end)

    @classmethod
    def cyan(self, message, end="\n"):
        print(self.color_cyan + message + self.color_reset, end=end)

    @classmethod
    def white(self, message, end="\n"):
        print(self.color_white + message + self.color_reset, end=end)
